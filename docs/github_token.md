# Refreshing the `GITHUB_TOKEN`

GitHub automatically provisions a short-lived `GITHUB_TOKEN` secret for every
workflow run, but you may also need to generate or rotate your own Personal
Access Token (PAT) to test automation locally or update repository secrets.
Follow the steps below to obtain a new token, update dependent systems, and keep
the credential secure throughout its lifecycle.

## 1. Inventory the Existing Usage

Before revoking anything, make a quick list of every place the token is used.
Check these locations so you can update them immediately after rotation:

| Where to check | What to look for |
| --- | --- |
| `gh auth status`, credential helpers, or password managers | Saved logins/aliases that mention the repository |
| GitHub repository/organization secrets | Entries named `GITHUB_TOKEN`, `PAT_*`, or similar |
| Local `.env`, `.envrc`, or CI/CD variables | Exported environment variables referencing the soon-to-expire token |

Document the use case (local scripting, Actions workflow, third-party
integration, etc.). This context informs the scopes you select for the new
token and makes the next rotation easier.

## 2. Generate a Token via the Web UI

1. Sign in to GitHub and open **Settings → Developer settings → Personal access
   tokens**.
2. Choose **Fine-grained tokens** (recommended) so the token can be limited to
   the `stop-azs` repository. Use **Tokens (classic)** only if a workflow still
   depends on legacy scopes.
3. Click **Generate new token**, set an expiration date (30–90 days is a good
   default), and provide a useful note such as `stop-azs automation`.
4. Select the repositories and permissions/scopes the workflow requires. Keep
   the surface area tight—most scenarios only need **Contents: Read/Write** and
   **Workflows: Read/Write**.
5. Click **Generate token** and copy the value immediately. GitHub will never
   display it again.

## 3. Generate or Refresh via the GitHub CLI

If you prefer the [GitHub CLI](https://cli.github.com/), you can issue a new
token with scopes that mirror what your automation needs:

```bash
gh auth login --scopes "repo,workflow"
# or refresh an existing login
gh auth refresh -h github.com -s repo,workflow
```

The CLI stores credentials using the system keychain. Run `gh auth status` to
confirm which tokens are active and when they expire. To update an Actions
secret directly from the CLI, pipe the new token into `gh secret set PAT_STOP_AZS`.

## 4. Update GitHub Secrets or Local Configuration

Once the token is generated, replace it everywhere you inventoried in step 1:

* **GitHub repository secret** – open **Settings → Secrets and variables →
  Actions → New repository secret**, or run `gh secret set PAT_STOP_AZS
  < token.txt`. Paste the PAT value and save it.
* **Local development** – export it temporarily (e.g. `export
  GITHUB_TOKEN=ghp_...`) or store it in a password manager. Avoid committing
  `.env` files that contain the secret.
* **Third-party tooling** – if a deployment system, scheduler, or integration
  references the PAT, update that configuration immediately to prevent service
  interruptions.

After updating each location, run a quick smoke test (for example, `gh repo
list` or the workflow that previously failed) to confirm the new token works.

## 5. Rotate and Revoke

* Schedule token reviews (e.g. every 90 days) and record the rotation date in a
  secure log or the password manager entry.
* Revoke unused or compromised tokens immediately via **Developer settings** →
  **Fine-grained tokens**/**Tokens (classic)**.
* Update any CI/CD variables or local `.env` files that reference the old token.
  If a workflow run fails due to a missing secret, redeploy with the refreshed
  PAT to confirm resolution.

Documenting the scope, expiration date, and point of contact alongside the
secret keeps the team aligned on how automation is authenticated.
