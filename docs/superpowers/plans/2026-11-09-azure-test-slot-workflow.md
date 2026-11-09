# Azure Test Slot Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deploy pull requests targeting `main` to the Azure App Service `test` slot through a new GitHub Actions workflow.

**Architecture:** Extract the existing build, test, packaging, Azure login, platform check, and deploy steps into a local reusable workflow. Keep the existing workflow as the production caller and add a separate PR caller that supplies `test` as the slot name.

**Tech Stack:** GitHub Actions reusable workflows, Azure Web Apps Deploy action, Windows PowerShell packaging.

**Spec:** `docs/superpowers/specs/2026-11-09-azure-test-slot-workflow-design.md`

## Global Constraints

- Production deployment remains on `main` push and manual `workflow_dispatch`, with existing path filters and default App Service slot.
- `deploy-azure-test.yml` targets PRs to `main` on `opened`, `synchronize`, and `reopened` only.
- PR deployment uses the slot named `test`.
- Keep standard `pull_request`; do not use `pull_request_target`.
- Continue using repository variables `AZURE_WEBAPP_NAME`, `AZURE_RESOURCE_GROUP` and secret `AZURE_CREDENTIALS`.

## Review Focus

- Production push still deploys to the default slot. Verify the production caller omits the slot input and preserves manual dispatch.
- Edits to the reusable workflow still trigger production deployment from `main`. Verify its path is included in production caller filters.
- PRs to other base branches do not deploy to `test`. Verify `branches: [main]`.
- PR synchronize events deploy the current PR head rather than the base branch. Verify the reusable workflow checkout runs in the caller's PR context.
- Fork PRs do not get Azure secrets. Keep `pull_request` and note deployment is unavailable for fork PRs; never elevate to `pull_request_target`.

---

### Task 1: Share deployment and add the test-slot PR caller

**Files:**
- Create: `.github/workflows/deploy-azure-reusable.yml`
- Create: `.github/workflows/deploy-azure-test.yml`
- Modify: `.github/workflows/deploy-azure.yml`

**Interfaces:**
- Reusable workflow input: `slot_name`, optional string defaulting to empty.
- Callers inherit `AZURE_CREDENTIALS`; reusable workflow reads `vars.AZURE_WEBAPP_NAME` and `vars.AZURE_RESOURCE_GROUP`.
- Empty `slot_name` deploys to the default slot; nonempty `slot_name` is passed as `slot-name` to `azure/webapps-deploy@v3`.

- [x] **Step 1: Create the `dev` branch from `origin/main`** as previously requested, then make the workflow changes on that branch.

- [x] **Step 2: Extract the existing deployment steps** into `deploy-azure-reusable.yml`, triggered by `workflow_call`; preserve tests, Windows packaging, runtime checksum verification, Azure login, and Windows App Service validation. Use conditional deploy steps so the production caller omits `slot-name`, while a caller with `slot_name` passes it through.

- [x] **Step 3: Convert `deploy-azure.yml` into the production caller**; preserve its `push` filters and `workflow_dispatch`, add the reusable workflow path to `push.paths`, pass `secrets: inherit`, and omit `slot_name`.

- [x] **Step 4: Add `deploy-azure-test.yml`** with a `pull_request` trigger targeting `main` for `opened`, `synchronize`, and `reopened`; call the reusable workflow with `slot_name: test` and `secrets: inherit`.

- [x] **Step 5: Validate all three workflow files** using `actionlint` if installed, otherwise parse them with Ruby's YAML parser; inspect the resulting trigger, caller input, slot target, and production caller to confirm the constraints above.

- [x] **Step 6: Run the application test suite**

Run: `./.venv-py39/bin/python -m unittest discover -s tests`
Expected: all tests pass; the workflow-only change does not regress the application.

- [x] **Step 7: Check the patch**

Run: `git diff --check`
Expected: no whitespace errors.
