#!/bin/bash

echo "[post-create] start" >> ~/status

# this runs in background after UI is available

# (optional) upgrade packages
#sudo apt-get update
#sudo apt-get upgrade -y
#sudo apt-get autoremove -y
#sudo apt-get clean -y

# add your commands here

sudo apt install gh -y
wget -O argocd https://github.com/argoproj/argo-cd/releases/download/v2.9.3/argocd-linux-amd64
chmod +x argocd
sudo mv argocd /usr/bin

#echo alias k=kubectl >> /home/vscode/.zshrc

echo "[post-create] complete" >> ~/status