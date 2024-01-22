import requests
import datetime
import subprocess
import glob
import time
import os

GEOLOCATION_DEV = "GEOLOCATION-0A41430434C388A9"
GEOLOCATION_SPRINT = "GEOLOCATION-3F7C50D0C9065578"
GEOLOCATION_LIVE = "GEOLOCATION-4ACFC9B6B78D5BB1"
SSO_TOKEN_URL_DEV = "https://sso-dev.dynatracelabs.com/sso/oauth2/token"
SSO_TOKEN_URL_SPRINT = "https://sso-sprint.dynatracelabs.com/sso/oauth2/token"
SSO_TOKEN_URL_LIVE = "https://sso.dynatrace.com/sso/oauth2/token"
DT_RW_API_TOKEN = os.environ.get("DT_RW_API_TOKEN") # token to create all other tokens
DT_ENV_NAME = os.environ.get("DT_ENV_NAME") # abc12345
DT_ENV = os.environ.get("DT_ENV", "live") # dev, sprint" or "live"
GH_RW_TOKEN = os.environ.get("GH_RW_TOKEN") # Token ArgoCD uses to create "customer-apps" repositories. TODO: What permissions does this need?

# If any of these words are found in command execution output
# The printing of the output to console will be suppressed
# Add words here to block more things
SENSITIVE_WORDS = ["secret", "secrets", "token", "tokens", "generate-token"]

BACKSTAGE_PORT_NUMBER = 7007
ARGOCD_PORT_NUMBER = 30100

STANDARD_TIMEOUT="300s"
WAIT_FOR_ARTIFACT_TIMEOUT = 60
WAIT_FOR_ACCOUNTS_TIMEOUT = 60

COLLECTOR_WAIT_TIMEOUT_SECONDS = 30
OPENTELEMETRY_COLLECTOR_ENDPOINT = "http://localhost:4318"
CODESPACE_NAME = os.environ.get("CODESPACE_NAME")

GITHUB_ORG_SLASH_REPOSITORY = os.environ.get("GITHUB_REPOSITORY") # eg. agardnerIT/mclass
GITHUB_REPO_NAME = os.environ.get("RepositoryName") # eg. mclass
GITHUB_DOT_COM_REPO = f"https://github.com/{GITHUB_ORG_SLASH_REPOSITORY}.git"
GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN = os.environ.get("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
#GITHUB_USER = os.environ.get("GITHUB_USER") # eg. agardnerIT
DT_OAUTH_CLIENT_ID = os.environ.get("DT_OAUTH_CLIENT_ID")
DT_OAUTH_CLIENT_SECRET = os.environ.get("DT_OAUTH_CLIENT_SECRET")
DT_OAUTH_ACCOUNT_URN = os.environ.get("DT_OAUTH_ACCOUNT_URN")

def run_command(args, ignore_errors=False):
    output = subprocess.run(args, capture_output=True, text=True)

    # Secure coding. Don't print sensitive info to console.
    # Find common elements between blocked words and args.
    # Only print output if not found.
    # If found, it means the output of this command (as given in args) is expected to be sensitive
    # So do not print.
    set1 = set(args)
    set2 = set(SENSITIVE_WORDS)
    common_elems = (set1 & set2)
    if not common_elems:
        print(output.stdout)

    # Annoyingly, if git has nothing to commit
    # it exits with a returncode == 1
    # So ignore any git errors but exit for all others
    if not ignore_errors and output.returncode > 0:
        exit(f"Got an error! Return Code: {output.returncode}. Error: {output.stderr}. Stdout: {output.stdout}. Exiting.")
    return output

def do_file_replace(pattern="", find_string="", replace_string="", recursive=False):
    for filepath in glob.iglob(pattern, recursive=recursive):
        TARGET_FILE = False
        with open(filepath, "r") as file: # open file in read mode only first
            file_content = file.read()
            if find_string in file_content:
                TARGET_FILE = True
        # Replace the text
        file_content = file_content.replace(find_string, replace_string)

        if TARGET_FILE:
            with open(filepath, "w") as file: # now open in write mode and write
                file.write(file_content)

def git_commit(target_file="", commit_msg="", push=False):
    output = run_command(["git", "add", target_file], ignore_errors=True)
    output = run_command(["git", "commit", "-m", commit_msg], ignore_errors=True)
    if push:
        output = run_command(["git", "push"], ignore_errors=True)

# Whereas the kubectl wait command can be used to wait for EXISTING artifacts (eg. deployments) to be READY.
# kubectl wait will error if the artifact DOES NOT EXIST YET.
# This function first waits for it to even exist
# eg. wait_for_artifact_to_exist(namespace="default", artifact_type="deployment", artifact_name="backstage")
def wait_for_artifact_to_exist(namespace="default", artifact_type="", artifact_name=""):
    count = 1
    get_output = run_command(["kubectl", "-n", namespace, "get", f"{artifact_type}/{artifact_name}"], ignore_errors=True)

    # if artifact does not exist, important output will be in stderr
    # if artifact DOES exist, use stdout
    if get_output.stderr != "":
        get_output = get_output.stderr
    else:
        get_output = get_output.stdout

    print(get_output)

    while count < WAIT_FOR_ARTIFACT_TIMEOUT and "not found" in get_output:
        print(f"Waiting for {artifact_type}/{artifact_name} in {namespace} to exist. Wait count: {count}")
        count += 1
        get_output = run_command(["kubectl", "-n", namespace, "get", f"{artifact_type}/{artifact_name}"], ignore_errors=True)
        # if artifact does not exist, important output will be in stderr
        # if artifact DOES exist, use stdout
        if get_output.stderr != "":
            get_output = get_output.stderr
        else:
            get_output = get_output.stdout
        print(get_output)
        time.sleep(1)

def get_otel_collector_endpoint():
    return OPENTELEMETRY_COLLECTOR_ENDPOINT

def get_github_org(github_repo):
    return github_repo[:github_repo.index("/")]

##############################
# DT FUNCTIONS

def send_log_to_dt_or_otel_collector(success, msg_string="", dt_api_token="", endpoint=get_otel_collector_endpoint(), destroy_codespace=False, dt_tenant_live=""):

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
    destroy_codespace = False # DEBUG: TODO remove. Temporarily override while developing
    if destroy_codespace:
        send_log_to_dt_or_otel_collector(success=True, msg_string=f"Destroying codespace: {CODESPACE_NAME}", destroy_codespace=False, dt_tenant_live=dt_tenant_live)

        destroy_codespace_output = subprocess.run(["gh", "codespace", "delete", "--codespace", CODESPACE_NAME], capture_output=True, text=True)

        if destroy_codespace_output.returncode == 0:
            send_log_to_dt_or_otel_collector(success=True, msg_string=f"codespace {CODESPACE_NAME} deleted successfully", destroy_codespace=False, dt_tenant_live=dt_tenant_live)
        else:
            send_log_to_dt_or_otel_collector(success=False, msg_string=f"failed to delete codespace {CODESPACE_NAME}. {destroy_codespace_output.stderr}", destroy_codespace=False, dt_tenant_live=dt_tenant_live)

def get_geolocation(dt_env):
    if dt_env.lower() == "dev":
        return GEOLOCATION_DEV
    elif dt_env.lower() == "sprint":
        return GEOLOCATION_SPRINT
    elif dt_env.lower() == "live":
        return GEOLOCATION_LIVE
    else:
        return None

def get_sso_token_url(dt_env):
    if dt_env.lower() == "dev":
        return SSO_TOKEN_URL_DEV
    elif dt_env.lower() == "sprint":
        return SSO_TOKEN_URL_SPRINT
    elif dt_env.lower() == "live":
        return SSO_TOKEN_URL_LIVE
    else:
        return None
    
def create_dt_api_token(token_name, scopes, dt_rw_api_token, dt_tenant_live):

    # Automatically expire tokens 1 day in future.
    time_future = datetime.datetime.now() + datetime.timedelta(days=1)
    expiry_date = time_future.strftime("%Y-%m-%dT%H:%M:%S.999Z")

    headers = {
        "accept": "application/json; charset=utf-8",
        "content-type": "application/json; charset=utf-8",
        "authorization": f"api-token {dt_rw_api_token}"
    }

    payload = {
        "name": token_name,
        "scopes": scopes,
        "expirationDate": expiry_date
    }

    resp = requests.post(
        url=f"{dt_tenant_live}/api/v2/apiTokens",
        headers=headers,
        json=payload
    )

    if resp.status_code != 201:
        exit(f"Cannot create DT API token: {token_name}. Response was: {resp.status_code}. {resp.text}. Exiting.")

    return resp.json()['token']

def build_dt_urls(dt_env, dt_env_name):
    dt_tenant_apps = f"https://{dt_env_name}.{dt_env}.apps.dynatrace.com"
    dt_tenant_live = f"https://{dt_env_name}.{dt_env}.dynatrace.com"

    # if environment is "dev" or "sprint"
    # ".dynatracelabs.com" not ".dynatrace.com"
    if dt_env.lower() == "dev" or dt_env.lower() == "sprint":
        dt_tenant_apps = dt_tenant_apps.replace(".dynatrace.com", ".dynatracelabs.com")
        dt_tenant_live = dt_tenant_live.replace(".dynatrace.com", ".dynatracelabs.com")
    
    return dt_tenant_apps, dt_tenant_live




# Build DT environment URLs
# DT_TENANT_APPS, DT_TENANT_LIVE = build_dt_urls(dt_env_name=DT_ENV_NAME, dt_env=DT_ENV)
# DT_ALL_INGEST_TOKEN = create_dt_api_token()