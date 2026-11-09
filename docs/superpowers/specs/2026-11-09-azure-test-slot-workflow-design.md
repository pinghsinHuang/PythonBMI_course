# Azure Test Slot Workflow Design

- **Intent:** Deploy pull requests targeting `main` to the Azure App Service slot named `test` so changes can be checked before merging.
- **Goal:** Keep the existing production deployment behavior on `main` while sharing its test, package, Azure login, platform verification, and deployment setup with the new PR workflow.
- **Non-goals:** Do not deploy PR changes to production, change application packaging/runtime, or use `pull_request_target`.
- **Approaches:** Duplicating the current workflow is simplest but risks production and test workflows drifting. Extracting a reusable workflow centralizes shared steps but requires a small refactor to the existing production workflow. The user chose the reusable-workflow approach to keep both deployments consistent.
- **Trigger and target:** `deploy-azure-test.yml` runs for PRs targeting `main` on `opened`, `synchronize`, and `reopened`, and calls the shared workflow with slot name `test`. The existing production caller retains its `push`-to-`main` path filters and manual `workflow_dispatch`.
- **Implementation decisions:** Add a `workflow_call` reusable workflow for shared deployment steps; pass the existing Azure credential secret through the caller and continue reading the existing repository variables for app name and resource group. Keep production deployment on the default app slot by omitting the slot input there.
- **Security constraint:** Standard `pull_request` events do not expose repository secrets to workflows from forked PRs, so such PR runs cannot deploy to Azure. Do not switch to `pull_request_target` to bypass this restriction.
