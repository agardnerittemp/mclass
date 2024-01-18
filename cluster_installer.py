import os
import subprocess
import time

WAIT_FOR_SECRETS_TIMEOUT = 60
WAIT_FOR_ACCOUNTS_TIMEOUT = 60
STANDARD_TIMEOUT="300s"

BACKSTAGE_PORT_NUMBER = 7007
ARGOCD_PORT_NUMBER = 30100
DT_TENANT_NAME = os.environ.get("DT_TENANT_NAME")
DT_TENANT_LIVE = os.environ.get("DT_TENANT_LIVE")
DT_TENANT_APPS = os.environ.get("DT_TENANT_APPS")
DT_ALL_INGEST_TOKEN = os.environ.get("DT_ALL_INGEST_TOKEN")
CODESPACE_NAME = os.environ.get("CODESPACE_NAME")
GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN = os.environ.get("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_USER = os.environ.get("GITHUB_USER")
DT_SSO_TOKEN_URL = os.environ.get("DT_SSO_TOKEN_URL")
DT_OAUTH_CLIENT_ID = os.environ.get("DT_OAUTH_CLIENT_ID")
DT_OAUTH_CLIENT_SECRET = os.environ.get("DT_OAUTH_CLIENT_SECRET")
DT_OAUTH_ACCOUNT_URN = os.environ.get("DT_OAUTH_ACCOUNT_URN")
DT_ALL_INGEST_TOKEN = os.environ.get("DT_ALL_INGEST_TOKEN")
DT_OP_TOKEN = os.environ.get("DT_OP_TOKEN")
DT_MONACO_TOKEN = os.environ.get("DT_MONACO_TOKEN")

# TODO: None checking the above variables

def run_command(args):
    output = subprocess.run(args, capture_output=True, text=True)
    print(output.stdout)
    return output

# Download argocd binary
# output = run_command(["wget", "-O", "argocd", "https://github.com/argoproj/argo-cd/releases/download/v2.9.3/argocd-linux-amd64"])
# output = run_command(["chmod", "+x", "argocd"])
# output = run_command(["sudo", "mv", "argocd", "/usr/bin"])

# Create cluster
output = run_command(["kind", "create", "cluster", "--config", ".devcontainer/kind-cluster.yml", "--wait", STANDARD_TIMEOUT])

# Create namespaces
namespaces = ["argocd", "opentelemetry", "dynatrace", "backstage", "monaco"]
for namespace in namespaces:
    output = run_command(["kubectl", "create", "namespace", namespace])

# Install argocd
output = run_command(["kubectl", "apply", "-n", "argocd", "-f", "https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml"])
output = run_command(["kubectl", "wait", "--for=condition=Available=True", "deployments", "-n", "argocd", "--all", f"--timeout={STANDARD_TIMEOUT}"])

# Configure argocd
output = run_command(["kubectl", "apply", "-n", "argocd", "-f", "gitops/manifests/platform/argoconfig/argocd-no-tls.yml"])
output = run_command(["kubectl", "apply", "-n", "argocd", "-f", "gitops/manifests/platform/argoconfig/argocd-nodeport.yml"])
output = run_command(["kubectl", "-n", "argocd", "rollout", "restart", "deployment/argocd-server"])
output = run_command(["kubectl", "-n", "argocd", "rollout", "status", "deployment/argocd-server", f"--timeout={STANDARD_TIMEOUT}"])

# Apply platform
output = run_command(["kubectl", "apply", "-f", "gitops/platform.yml"])

# Wait until argo secret exists (or timeout is hit)
count = 1
get_argo_secrets_output = ""
while count < WAIT_FOR_SECRETS_TIMEOUT and "argocd-initial-admin-secret" not in get_argo_secrets_output:
    print(f"Waiting for argo secret. Wait count: {count}")
    count += 1
    get_argo_secrets_output = run_command(["kubectl", "-n", "argocd", "get", "secrets"]).stdout
    time.sleep(1)

# Set the default context to the argocd namespace so 'argocd' CLI works
output = run_command(["kubectl", "config", "set-context", "--current", "--namespace=argocd"])
# Now authenticate
output = run_command(["argocd", "login", "argo", "--core"])

# Wait until argo account 'alice' exists (or timeout is hit)
count = 1
get_argo_accounts_output = ""
while count < WAIT_FOR_ACCOUNTS_TIMEOUT and "alice" not in get_argo_accounts_output:
    print(f"Waiting for argo account alice to exist. Wait count: {count}")
    count += 1
    get_argo_accounts_output = run_command(["argocd", "account", "list"]).stdout
    time.sleep(1)

if get_argo_accounts_output == "":
    exit(f"ArgoCD Account alice does not exist. Cannot proceed.")

ARGOCD_TOKEN = run_command(["argocd", "account", "generate-token", "--account", "alice"]).stdout

if ARGOCD_TOKEN is None or ARGOCD_TOKEN == "":
    exit(f"ARGOCD_TOKEN is empty: {ARGOCD_TOKEN}. Cannot proceed!")

output = run_command(["kubectl", "config", "set-context", "--current", "--namespace=default"])

# create dt-details secret in opentelemetry namespace
output = run_command(["kubectl", "-n", "opentelemetry", "create", "secret", "generic", "dt-details", f"--from-literal=DT_URL={DT_TENANT_LIVE}", f"--from-literal=DT_OTEL_ALL_INGEST_TOKEN={DT_ALL_INGEST_TOKEN}"])

# create backstage-details secret in opentelemetry namespace
output = run_command(["kubectl", "-n", "opentelemetry" "create" "secret" "generic" "backstage-secrets"
                      f"--from-literal=BASE_DOMAIN={CODESPACE_NAME}",
                      f"--from-literal=BACKSTAGE_PORT_NUMBER={BACKSTAGE_PORT_NUMBER}",
                      f"--from-literal=ARGOCD_PORT_NUMBER={ARGOCD_PORT_NUMBER}",
                      f"--from-literal=ARGOCD_TOKEN={ARGOCD_TOKEN}",
                      f"--from-literal=GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN={GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}",
                      f"--from-literal=GITHUB_TOKEN={GITHUB_TOKEN}",
                      f"--from-literal=DT_TENANT_NAME={DT_TENANT_NAME}",
                      f"--from-literal=DT_TENANT_LIVE={DT_TENANT_LIVE}",
                      f"--from-literal=DT_TENANT_APPS={DT_TENANT_APPS}",
                      f"--from-literal=DT_SSO_TOKEN_URL={DT_SSO_TOKEN_URL}",
                      f"--from-literal=DT_OAUTH_CLIENT_ID={DT_OAUTH_CLIENT_ID}",
                      f"--from-literal=DT_OAUTH_CLIENT_SECRET={DT_OAUTH_CLIENT_SECRET}",
                      f"--from-literal=DT_OAUTH_ACCOUNT_URN={DT_OAUTH_ACCOUNT_URN}"
                    ])

# Create secret for OneAgent in dynatrace namespace
output = run_command([
    "kubectl", "-n", "dynatrace", "create", "secret", "generic", "hot-day-platform-engineering",
    f"--from-literal=apiToken={DT_OP_TOKEN}",
    f"--from-literal=dataIngestToken={DT_ALL_INGEST_TOKEN}"
    ])

# Create monaco-secret in monaco namespace
output = run_command(["kubectl", "-n", "monaco", "create", "secret", "generic", "monaco-secret", f"--from-literal=monacoToken={DT_MONACO_TOKEN}"])
# Create monaco-secret in dynatrace namespace
output = run_command(["kubectl", "-n", "dynatrace", "create", "secret", "generic", "monaco-secret", f"--from-literal=monacoToken={DT_MONACO_TOKEN}"])