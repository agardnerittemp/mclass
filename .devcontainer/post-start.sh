#!/bin/bash

echo "[post-start] start" >> ~/status

# Start the cluster
minikube start

echo "[post-start] minikube available" >> ~/status

# install argocd
kubectl create namespace argocd
echo "[post-start] argocd namespace created" >> ~/status
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl wait --for=condition=Available=True deploy -n argocd --all --timeout=90s
echo "[post-start] argocd deployed" >> ~/status

##########################
# 1. Install test harness dependencies
# 2. Run test harness
pip install -r ../requirements.txt

python ../testharness.py

echo "post-start complete" >> ~/status