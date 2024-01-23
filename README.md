# mclass

## Prerequisites

### Create SaaS trial tenant

If you don't already have a Dynatrace SaaS tenant, sign up for a free trial here: [free 15 day Dynatrace trial](https://www.dynatrace.com/trial)

Make a note of the Dynatrace environment name. This the the first part of the URL. `abc12345` would be the environment ID for `https://abc12345.apps.dynatrace.com`

* For those running in other environments (such as `sprint`), make a note of your environment: `dev`, `sprint` or `live`

### Create DT oAuth Client

Follow [the documentation](https://www.dynatrace.com/support/help/platform-modules/business-analytics/ba-api-ingest) to set up an OAuth client + policy + bind to your service user account email.

This is required so the platform can send business events (aka bizevents) to Dynatrace.

You should now have 4 pieces of information:

1. A DT environment ID
1. An oAuth client ID
1. An oAuth client secret
1. An account URN

### Create DT API Token

Create a Dynatrace access token with the following permissions. This token will be used by the setup script to automatically create all other required DT tokens.

1. apiTokens.read
1. apiTokens.write

You should now have 5 pieces of information:

1. A DT environment ID
1. An oAuth client ID
1. An oAuth client secret
1. An account URN
1. An API token

### Create a GitHub Organization

[Create a free GitHub organization](https://github.com/account/organizations/new?plan=free)

> Do not skip this step! The demo **will not work without an organization**. It will not work under your user account.

#### Why won't it work?

Currently, the [ArgoCD SCM Provider Generator for GitHub](https://argocd-applicationset.readthedocs.io/en/stable/Generators-SCM-Provider/#github) only supports syncing from organizations, not user accounts.

### Fork Repo

For this repo into your new organisation.

### Create GitHub Personal Access Token

Go [here](https://github.com/settings/personal-access-tokens/new) and create a new "fine grained" token:

- Resource owner: `YourOrg/YourForkedRepo`
- Choose `Only selected repositories` and again select your fork

#### Permissions required

##### Repository Permisions

- Administration (read + write)
- Codespaces (read + write)
- Contents (read and write)

## Setup Instructions

### Create Codespace Secrets

At this point you should have six pieces of information (seven if Dynatrace is running in an environment other than `live`).

In your fork, go to: `Settings > Secrets and Variables > Codespaces`. Create secrets with these EXACT names:

- `GH_RW_TOKEN` (the GitHub Personal Access Token)
- `DT_ENV_NAME` (eg. `abc12345`)
- `DT_RW_API_TOKEN` - The DT API token created above.
- `DT_OAUTH_ACCOUNT_URN`
- `DT_OAUTH_CLIENT_ID`
- `DT_OAUTH_CLIENT_SECRET`
- (optional) `DT_ENV` eg. `dev`, `sprint` or `live`. Defaults to `live`

## Starting the Platform

In your fork, click the green "Code" button then change to "Codespaces" and click  "create codespace on main".

The codespace will launch in a new browser window.

Wait until the `Running postStartCommand...` disappears. It should take ~10 minutes.

## Usage Instructions (in progress)

Get argocd password
```
ARGOCDPWD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
echo $ARGOCDPWD
```

Change to "Ports" tab and open ArgoCD (port 30100) & log in.

Backstage is also available (port 30105).

## Observability of the Codespace

The codespace self-tests on startup so look for a pytest trace showing the health.

If something goes wrong setting up the codespace, logs are sent directly to the Dynatrace SaaS ingest endpoint so `fetch logs` to see what went wrong.

## Updating to Latest

When this repo is updated / has bug fixes applied, it will be necessary to update your forked copy. This can be done easily:

1. In your fork, click the "sync fork" button.
1. If prompted, discard any commits.
1. You may need to sync the fork again by clicking "update branch".

At this point, you should see:

![fork not behind upstream](assets/branch-not-behind-upstream.png)

## Cleanup / Destroy Resources

1. TODO: Need a script to delete DT tokens
2. Go to https://github.com/codespaces and delete the codespace
3. Go to https://github.com/yourOrg > settings and delete the organization

# Debugging

## View Creation Log

```
tail -f /workspaces/.codespaces/.persistedshare/creation.log
```