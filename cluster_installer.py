import os
import subprocess
import time
import glob


#####################
# FUNCTIONS
#####################

def run_command(args):
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
    if "git" not in args and output.returncode > 0:
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
    output = run_command(["git", "add", target_file])
    output = run_command(["git", "commit", "-m", commit_msg])
    if push:
        output = run_command(["git", "push"])

def get_geolocation(tenant=""):
    if ".dev." in DT_TENANT_LIVE:
        return "GEOLOCATION-0A41430434C388A9"
    if ".sprint." in DT_TENANT_LIVE:
        return "GEOLOCATION-3F7C50D0C9065578"
    if ".live." in DT_TENANT_LIVE:
        return "GEOLOCATION-4ACFC9B6B78D5BB1"
    else:
        return None

###########################################
# INPUT VARIABLES
###########################################

WAIT_FOR_SECRETS_TIMEOUT = 60
WAIT_FOR_ACCOUNTS_TIMEOUT = 60

STANDARD_TIMEOUT="300s"
# If any of these words are found in command execution output
# The printing of the output to console will be suppressed
# Add words here to block more things
SENSITIVE_WORDS = ["secret", "secrets", "token", "tokens", "generate-token"]

BACKSTAGE_PORT_NUMBER = 7007
ARGOCD_PORT_NUMBER = 30100
DT_TENANT_NAME = os.environ.get("DT_TENANT_NAME")
DT_TENANT_LIVE = os.environ.get("DT_TENANT_LIVE")
DT_TENANT_APPS = os.environ.get("DT_TENANT_APPS")
DT_GEOLOCATION = None
DT_ALL_INGEST_TOKEN = os.environ.get("DT_ALL_INGEST_TOKEN")
CODESPACE_NAME = os.environ.get("CODESPACE_NAME")
GITHUB_ORG_SLASH_REPOSITORY = os.environ.get("GITHUB_REPOSITORY")
GITHUB_DOT_COM_REPO = f"https://github.com/{GITHUB_ORG_SLASH_REPOSITORY}.git"
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

# Set DT GEOLOCATION based on env type used
# TODO: Find a better way here. If this was widely used, all load would be on one GEOLOCATION.
DT_GEOLOCATION = get_geolocation(DT_TENANT_LIVE)


###########################
# TEMP AREA
###########################

#exit()

# END TEMP AREA

# Delete cluster first, in case this is a re-run
run_command(["kind", "delete", "cluster"])

# Find and replace placeholders
# Commit up to repo
# Find and replace DT_TENANT_LIVE_PLACEHOLDER with real text
# Commit back to repo
do_file_replace(pattern="./**/*.yml", find_string="DT_TENANT_LIVE_PLACEHOLDER", replace_string=DT_TENANT_LIVE, recursive=True)
git_commit(target_file="-A", commit_msg="update DT_TENANT_LIVE_PLACEHOLDER", push=True)

# Find and replace DT_TENANT_APPS_PLACEHOLDER with real text
do_file_replace(pattern="./**/*.yml", find_string="DT_TENANT_APPS_PLACEHOLDER", replace_string=DT_TENANT_APPS, recursive=True)
git_commit(target_file="-A", commit_msg="update DT_TENANT_APPS_PLACEHOLDER", push=True)

# Find and replace GITHUB_DOT_COM_REPO_PLACEHOLDER with real text
do_file_replace(pattern="./**/*.yml", find_string="GITHUB_DOT_COM_REPO_PLACEHOLDER", replace_string=GITHUB_DOT_COM_REPO, recursive=True)
git_commit(target_file="-A", commit_msg="update GITHUB_DOT_COM_REPO_PLACEHOLDER", push=True)

# Find and replace GEOLOCATION_PLACEHOLDER with real text
do_file_replace(pattern="./**/*.yml", find_string="GEOLOCATION_PLACEHOLDER", replace_string=DT_GEOLOCATION, recursive=True)
git_commit(target_file="-A", commit_msg="update GEOLOCATION_PLACEHOLDER", push=True)


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

# Wait for backstage deployment
output = run_command(["kubectl", "wait", "--for=condition=Available=True", "deployments", "-n", "backstage", "backstage", f"--timeout={STANDARD_TIMEOUT}"])

# create backstage-details secret in backstage namespace
output = run_command(["kubectl", "-n", "backstage", "create", "secret", "generic", "backstage-secrets",
                      f"--from-literal=BASE_DOMAIN={CODESPACE_NAME}",
                      f"--from-literal=BACKSTAGE_PORT_NUMBER={BACKSTAGE_PORT_NUMBER}",
                      f"--from-literal=ARGOCD_PORT_NUMBER={ARGOCD_PORT_NUMBER}",
                      f"--from-literal=ARGOCD_TOKEN={ARGOCD_TOKEN}",
                      f"--from-literal=GITHUB_USER={GITHUB_USER}",
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

# restart backstage to pick up secret and start successfully
output = run_command(["kubectl", "-n", "backstage", "rollout", "restart", "deployment/backstage"])
output = run_command(["kubectl", "-n", "backstage", "rollout", "status", "deployment/backstage", f"--timeout={STANDARD_TIMEOUT}"])

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