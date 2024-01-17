import subprocess
import requests
import os
import time
import pytest

# This file should be executed by pytest
# like: 

COLLECTOR_WAIT_TIMEOUT_SECONDS = 300
opentelemetry_collector_endpoint = "http://localhost:4318"
codespace_name = os.environ.get("CODESPACE_NAME")
dt_tenant_live = os.environ.get("DT_TENANT_LIVE")
dt_api_token = os.environ.get("DT_ALL_INGEST_TOKEN")

def run_command(args):
    output = subprocess.run(args, capture_output=True, text=True)
    return output

def sendLog(success, msg_string="", endpoint=opentelemetry_collector_endpoint, destroy_codespace=False):

    attributes_list = [{"key": "success", "value": { "boolean": success }}]

    timestamp = str(time.time_ns())

    if "dynatrace" in endpoint:
        # Local collector not available
        # Send directly to cluster
        payload = {
            "content": msg_string,
            "log.source": "testharness.py",
            "severity": "error"
        }

        headers = {
            "accept": "application/json; charset=utf-8",
            "Authorization": f"Api-Token {dt_api_token}",
            "Content-Type": "application/json"
        }

        requests.post(f"{dt_tenant_live}/api/v2/logs/ingest", 
          headers = headers,
          json=payload,
          timeout=5
        )
    else: # Send via local OTEL collector
        payload = {
            "resourceLogs": [{
                "resource": {
                    "attributes": []
                },
                "scopeLogs": [{
                    "scope": {},
                    "logRecords": [{
                        "timeUnixNano": timestamp,
                        "body": {
                            "stringValue": msg_string
                        },
                        "attributes": attributes_list,
                        "droppedAttributesCount": 0
                    }]
                }]
            }]
        }

        requests.post(f"{endpoint}/v1/logs", headers={ "Content-Type": "application/json" }, json=payload, timeout=5)

    # If user wishes to immediately
    # destroy the codespace, do it now
    # Note: Log lines inside here must have destroy_codespace=False to avoid circular calls
    destroy_codespace = False # DEBUG: Temporarily override while developing
    if destroy_codespace:
        sendLog(success=True, msg_string=f"Destroying codespace: {codespace_name}", destroy_codespace=False)

        destroy_codespace_output = subprocess.run(["gh", "codespace", "delete", "--codespace", codespace_name], capture_output=True, text=True)

        if destroy_codespace_output.returncode == 0:
            sendLog(success=True, msg_string=f"codespace {codespace_name} deleted successfully", destroy_codespace=False)
        else:
            sendLog(success=False, msg_string=f"failed to delete codespace {codespace_name}. {destroy_codespace_output.stderr}", destroy_codespace=False)

#################################################
# TEST SUITE BEGINS
#
# pytest executes `test_` methods in order
#################################################
def test_wait_for_collector():
    count = 1

    COLLECTOR_AVAILABLE = False
    while count < COLLECTOR_WAIT_TIMEOUT_SECONDS:
        collector_response = requests.get(f"{opentelemetry_collector_endpoint}/v1/logs")
        
        # A 405 code means "GET worked but a GET isn't valid for this endpoint"
        # This is precisely what we're expecting as the real OP should be a POST
        if collector_response.status_code == 405:
            COLLECTOR_AVAILABLE = True
            sendLog(success=True, msg_string=f"OpenTelemetry collector available after {count} seconds. Proceed with test harness.")
            break
        else:
            count += 1
            time.sleep(1) # sleep for 1s

    # OTEL collector is not yet available
    # Send warning directly to cluster
    if not COLLECTOR_AVAILABLE:
        sendLog(success=False, endpoint=dt_tenant_live, msg_string="OpenTelemetry collector not available. Send via direct-to-cluster ingest endpoint.", destroy_codespace=True)
        raise Exception("On cluster collector is not available. Terminating codespace. Check DT for logs.")


def test_ensure_argocd_namespace_exists():
    output = run_command(["kubectl", "get", "namespaces"])
    assert "argocd" in output.stdout

def test_ensure_opentelemetry_namespace_exists():
    output = run_command(["kubectl", "get", "namespaces"])
    assert "opentelemetry" in output.stdout

def test_ensure_opentelemetry_dtdetails_secret_exists():
    output = run_command(["kubectl", "-n", "opentelemetry", "get", "secrets"])
    assert "dt-details" in output.stdout

# test harness successful. Send congrats message
sendLog(success=True, msg_string="test harness executed successfully: v1.0.0", destroy_codespace=True)