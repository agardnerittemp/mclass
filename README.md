# mclass

##  Cretae a GitHub Organization

[Create a free GitHub organization](https://github.com/account/organizations/new?plan=free)

> Do not skip this step! The demo **will not work without an organization**. It will not work under your user account.

### Why won't it work?

Currently, the [ArgoCD SCM Provider Generator for GitHub](https://argocd-applicationset.readthedocs.io/en/stable/Generators-SCM-Provider/#github) only supports syncing from organizations, not user accounts.

##Fork Repo

For this repo into your new organisation.

In your fork, go to: "Settings > Secrets and variables > codespaces".

Create secrets with these EXACT names:

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

## Run without Keptn

In your forked repository, go to: "Settings > Secrets and variables > Codespaces"

Create a secret called (case sensitive): `INSTALL_KEPTN`

Set the value to `false`.

The demo can run with 2 CPU.

[Create a codespace now](https://github.com/codespaces/new)

## Run with Keptn

The demo needs 4 CPU.

[Create a codespace now](https://github.com/codespaces/new)

## Instructions (in progress)

Wait until the `Running postStartCommand...` disappears. It should take 3-4 minutes.

Get argocd password
```
ARGOCDPWD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
echo $ARGOCDPWD
```

Change to "Ports" tab and open ArgoCD & log in.

## Observability of the Codespace

The codespace self-tests on startup so look for a pytest trace showing the health.

If something goes wrong setting up the codespace, logs are sent directly to the Dynatrace SaaS ingest endpoint so `fetch logs` to see what went wrong.