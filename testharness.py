import subprocess
import requests
import os

codespace_name = os.environ.get("CODESPACE_NAME")

def sendNotification(success, msg_string="", destroy_codespace=False):

    url = "https://webhook.site/1e9185e3-1225-439b-8381-044fd1f417cc"

    payload = {
        "success": success,
        "msg": msg_string
    }

    response = requests.post(url=url, json=payload)

    # If user wishes to immediately 
    if destroy_codespace:
        print(f"Destroying codespace: {codespace_name}")
        #codespace_name = 
        destroy_codespace_output = subprocess.run(["gh", "codespace", "delete", "--codespace", codespace_name], capture_output=True, text=True)
        print(destroy_codespace_output)
        if destroy_codespace_output.returncode == 0:
            sendNotification(success=True, msg_string=f"codespace {codespace_name} deleted successfully", destroy_codespace=False)
        else:
            sendNotification(success=False, msg_string=f"failed to delete codespace {codespace_name}. {destroy_codespace_output.stderr}", destroy_codespace=False)



#################################
# Main test harness
#################################
try:
    #########
    # Test 1: Does argocd namespace exist
    #########
    output = subprocess.run(["kubectl", "get", "namespaces"], capture_output=True, text=True) # works

    if "argocd" not in output.stdout:
        sendNotification(success=False, msg_string="argocd namespace missing", destroy_codespace=True)
        
except Exception as e:
    sendNotification(success=False, msg_string=str(e), destroy_codespace=True)

# test harness successful. Send congrats message
sendNotification(success=True, msg_string="test harness executed successfully: v1.0.0", destroy_codespace=True)