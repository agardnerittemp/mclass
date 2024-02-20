from utils import *

DT_TENANT_APPS, DT_TENANT_LIVE = build_dt_urls(dt_env_name=DT_ENV_NAME, dt_env=DT_ENV)
DT_SSO_TOKEN_URL = get_sso_token_url(dt_env=DT_TENANT_APPS)

upload_dt_asset(sso_token_url=DT_SSO_TOKEN_URL, path="dynatraceassets/notebooks/analyze-argocd-notification-events.json", name="test6", type="notebook", upload_content_type="application/json", dt_tenant_apps=DT_TENANT_APPS)