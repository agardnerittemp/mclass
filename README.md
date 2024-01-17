# mclass

Fork this repo.

In your fork. Go to: "Settings > Secrets and variables > codespaces". Create secrets with these EXACT names:

- `DT_ALL_INGEST_TOKEN`
- `DT_MONACO_TOKEN`
- `DT_OAUTH_ACCOUNT_URN`
- `DT_OAUTH_CLIENT_ID`
- `DT_OAUTH_CLIENT_SECRET`
- `DT_OP_TOKEN`
- `DT_SSO_TOKEN_URL`
- `DT_TENANT_APPS`
- `DT_TENANT_LIVE`
- `DT_TENANT_NAME`


Wait until the `Running postStartCommand...` disappears. It should take 3-4 minutes.

Get argocd password
```
ARGOCDPWD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
echo $ARGOCDPWD
```

Change to "Ports" tab and open ArgoCD & log in.