#!/bin/bash

echo "[post-start] start" >> ~/status

# Start the cluster
kind create cluster --config .devcontainer/kind-cluster.yml --wait 300s

echo "[post-start] cluster available" >> ~/status

# install argocd
kubectl create namespace argocd
echo "[post-start] argocd namespace created" >> ~/status
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl wait --for=condition=Available=True deploy -n argocd --all --timeout=300s
echo "[post-start] argocd deployed" >> ~/status


kubectl apply -n argocd -f gitops/manifests/platform/argoconfig/argocd-no-tls.yml
kubectl apply -n argocd -f gitops/manifests/platform/argoconfig/argocd-nodeport.yml
kubectl -n argocd rollout restart deploy/argocd-server
kubectl -n argocd rollout status deploy/argocd-server --timeout=300s
echo "[post-start] argocd configured and restarted" >> ~/status

kubectl create namespace opentelemetry
kubectl -n opentelemetry create secret generic dt-details --from-literal=DT_URL=$DT_TENANT_LIVE --from-literal=DT_OTEL_ALL_INGEST_TOKEN=$DT_ALL_INGEST_TOKEN

# Install platform
kubectl apply -f gitops/platform.yml

##########################
# 1. Install Python and test harness dependencies
sudo apt install -y python3
sudo apt install -y python3-pip
pip install --break-system-packages -r requirements.txt
echo "[post-start] python and additional modules installed"

##########################
# 2. Run test harness
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
pytest --export-traces codespaces_test.py

echo "[post-start] pytest finished" >> ~/status

echo "[post-start] complete" >> ~/status