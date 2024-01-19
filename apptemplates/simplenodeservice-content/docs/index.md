# Docs for ${{ values.projectName }} in environment ${{ values.releaseStage }}

Managed by: ${{ values.teamIdentifier }}
Environment: ${{ values.releaseStage }}

## ArgoCD Status

[![](https://argo.BASE_DOMAIN_PLACEHOLDER/api/badge?name=${{ values.projectName }}-${{ values.teamIdentifier }}-${{ values.releaseStage }}-cd)](https://argo.BASE_DOMAIN_PLACEHOLDER/applications/argocd/${{ values.projectName }}-${{ values.teamIdentifier }}-${{ values.releaseStage }}-cd)

## Monitored by Dynatrace
📈Click the logo to view your dashboard 📈

[![](https://raw.githubusercontent.com/agardnerIT/mclass/main/dtlogo.svg)](https://jao16384.sprint.apps.dynatracelabs.com/ui/apps/dynatrace.dashboards/)