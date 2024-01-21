# mclass

## Prerequisites

### Create DT oAuth Client

Follow [the documentation](https://www.dynatrace.com/support/help/platform-modules/business-analytics/ba-api-ingest) to set up an OAuth client + policy + bind to your service user account email.

This is required so the platform can send business events (aka bizevents) to Dynatrace.

You should now have 3 pieces of information:

1. An oAuth client ID
1. An oAuth client secret
1. An account URN

### Create DT API Token

Create a Dynatrace access token with the following permissions. This token will be used by the setup script to automatically create all other required DT tokens.

1. apiTokens.read
1. apiTokens.write

You should now have 4 pieces of information:

1. An oAuth client ID
1. An oAuth client secret
1. An account URN
1. An API token

###  Create a GitHub Organization

[Create a free GitHub organization](https://github.com/account/organizations/new?plan=free)

> Do not skip this step! The demo **will not work without an organization**. It will not work under your user account.

#### Why won't it work?

Currently, the [ArgoCD SCM Provider Generator for GitHub](https://argocd-applicationset.readthedocs.io/en/stable/Generators-SCM-Provider/#github) only supports syncing from organizations, not user accounts.

## Setup Instructions

### Fork Repo

For this repo into your new organisation.

In your fork, go to: "Settings > Secrets and variables > codespaces".

Create secrets with these EXACT names.

- `DT_RW_API_TOKEN` - A DT API token with `apiTokens.write` and `apiTokens.read` permissions.
- `DT_ENV_NAME` eg. `abc12345`
- (optional) `DT_ENV` eg. `dev`, `sprint` or `live`. Defaults to `live`
- `DT_OAUTH_ACCOUNT_URN`
- `DT_OAUTH_CLIENT_ID`
- `DT_OAUTH_CLIENT_SECRET`

## Starting the Platform

### Run without Keptn

In addition to the secrets above, create another secret called (case sensitive): `INSTALL_KEPTN`

Set the value to `false`.

The demo can run with 2 CPU.

[Create a codespace now](https://github.com/codespaces/new)

### Run with Keptn

The demo needs 4 CPU.

[Create a codespace now](https://github.com/codespaces/new)

## Usage Instructions (in progress)

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