from utils import *

run_command(["rm", "-rf", f"/workspaces/{GITHUB_REPO_NAME}"])

input("Press a key when the fork is synced to upstream. Waiting....")

run_command("git", "clone", GITHUB_DOT_COM_REPO, f"/workspaces/{GITHUB_REPO_NAME}")

print(f"All done. Now run: `python3 /workspaces/{GITHUB_REPO_NAME}/cluster_installer.py`")