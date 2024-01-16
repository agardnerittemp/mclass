import subprocess
import requests

def sendNotification(success, error_string=""):

    url = "https://webhook.site/1e9185e3-1225-439b-8381-044fd1f417cc"

    payload = {
        "success": success,
        "error": error_string
    }

    response = requests.post(url=url, json=payload)

    print(f"Response: {response.status_code}")

#def destroyCodespace():
    # TODO

#################################
# Main test harness
#################################
try:
    output = subprocess.run(["kubectl", "get", "namespaces"], capture_output=True, text=True) # works

    if "argocd" not in output.stdout:
        sendNotification(success=False, error_string="argocd namespace missing")
        # TODO
        # destroyCodespace()
except Exception as e:
    sendNotification(success=False, error_string=str(e))
    # TODO
    # destroyCodespace()