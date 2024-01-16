import subprocess
import requests

def sendNotification(success):

    url = "https://webhook.site/1e9185e3-1225-439b-8381-044fd1f417cc"

    payload = {
        "foo": "bar",
        "success": success
    }

    response = requests.post(url=url, json=payload)

    print(f"Response: {response.status_code}")

try:
    #output = subprocess.run(["ls", "-al"], capture_output=True, text=True) # works
    output = subprocess.run(["kubectl", "get", "nodes"], capture_output=True, text=True) # works

    if "test.txt" in output.stdout:
        print("Found test.txt")
    else:
        print("test.txt missing")
except Exception as e:
    exit(f"ERROR: Got an error. Perhaps kubectl is not installed? {e}")