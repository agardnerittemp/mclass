import subprocess
import requests

def sendNotification(success, msg_string="", destroy_codespace=False):

    url = "https://webhook.site/1e9185e3-1225-439b-8381-044fd1f417cc"

    payload = {
        "success": success,
        "msg": msg_string
    }

    response = requests.post(url=url, json=payload)

    # TODO
    # If user wishes to immediately 
    #if destroy_codespace:
    # destroyCodespace()

# Do not call this directly
# Instead, use `sendNotification(..., destroy_codespace=True)`
#def destroyCodespace():
    # TODO


#################################
# Main test harness
#################################
try:
    # Test 1: Does argocd namespace exist
    output = subprocess.run(["kubectl", "get", "namespaces"], capture_output=True, text=True) # works

    if "argocd" not in output.stdout:
        sendNotification(success=False, msg_string="argocd namespace missing", destroy_codespace=True)
        
except Exception as e:
    sendNotification(success=False, msg_string=str(e), destroy_codespace=True)

# test harness successful. Send congrats message
sendNotification(success=True, msg_string="test harness executed successfully")