#!/bin/bash

echo "post-start start" >> ~/status

# Start the cluster
minikube start

# install argocd
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

##########################
# 1. Install test harness dependencies
# 2. Run test harness
pip install -r requirements.txt

python testharness.py

echo "post-start complete" >> ~/status