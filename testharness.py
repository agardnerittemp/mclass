import subprocess
import requests

def sendNotification(url, success):
    return "TODO"

try:
    #output = subprocess.run(["ls", "-al"], capture_output=True, text=True) # works
    output = subprocess.run(["kubectl", "get", "nodes"], capture_output=True, text=True) # works

    if "test.txt" in output.stdout:
        print("Found test.txt")
    else:
        print("test.txt missing")
except Exception as e:
    exit(f"ERROR: Got an error. Perhaps kubectl is not installed? {e}")