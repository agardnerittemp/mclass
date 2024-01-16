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

kubectl create namespace opentelemetry
kubectl -n opentelemetry create secret generic dt-details --from-literal=DT_URL=$DT_TENANT_LIVE --from-literal=DT_OTEL_ALL_INGEST_TOKEN=$DT_ALL_INGEST_TOKEN

# Install platform
kubectl apply -f gitops/platform.yml

##########################
# 1. Install test harness dependencies
pip install -r requirements.txt
echo "[post-start] python requirements installed"

##########################
# 2. Run test harness
#python testharness.py

#echo "[post-start] testharness.py finished"

echo "[post-start] complete" >> ~/status