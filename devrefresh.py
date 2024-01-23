from utils import *

run_command(["rm", "-rf", "/workspaces/mclass"])

input("Press a key when the fork is synced to upstream. Waiting....")

run_command(["cd", "/workspaces"])
run_command("git", "clone", GITHUB_DOT_COM_REPO)

print("All done. Now run: `python3 /workspaces/mclass/cluster_installer.py`")