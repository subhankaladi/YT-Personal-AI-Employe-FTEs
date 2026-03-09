# 🔒 Security Guide - What NOT to Push to GitHub

## ⚠️ CRITICAL: Files Protected by .gitignore

The following files contain **secrets and credentials** and are now blocked by `.gitignore`:

### Authentication Files (NEVER COMMIT)

| File | Contains | Risk |
|------|----------|------|
| `credentials.json` | Google OAuth client secret | 🔴 **CRITICAL** |
| `**/.env` | API keys, tokens, secrets | 🔴 **CRITICAL** |
| `**/*.pkl` | Gmail/LinkedIn auth tokens | 🔴 **CRITICAL** |
| `AI_Employee_Vault/.linkedin_session/` | LinkedIn browser session | 🔴 **CRITICAL** |
| `AI_Employee_Vault/.gmail_token.pkl` | Gmail OAuth token | 🔴 **CRITICAL** |
| `AI_Employee_Vault/.gmail_cache.pkl` | Gmail cache data | 🟠 **HIGH** |

### What's in These Files?

#### `credentials.json`
```
- Google Client ID
- Google Client Secret (GOCSPX-...)
- Project ID
- OAuth URIs
```

#### `facebook/.env`
```
- FACEBOOK_APP_ID
- FACEBOOK_APP_SECRET
- FACEBOOK_ACCESS_TOKEN (long-lived page token)
- FACEBOOK_PAGE_ID
```

#### `*.pkl` Files
```
- Pickled OAuth tokens
- Refresh tokens
- Session cookies
```

---

## ✅ Safe to Commit

These files are **safe** and should be committed:

| File/Directory | Purpose |
|----------------|---------|
| `*.py` | Python source code |
| `*.md` | Documentation |
| `*.bat`, `*.ps1` | Scripts |
| `*.yml` | Docker/config templates |
| `.env.example` | Environment templates (no secrets) |
| `AI_Employee_Vault/scripts/` | Worker scripts |
| `AI_Employee_Vault/Plans/` | Task plans |
| `AI_Employee_Vault/*.md` | Documentation files |

---

## 🛡️ Best Practices

### 1. Before Committing, Always Run
```bash
git status
```
Check that no `.env`, `.pkl`, or `credentials.json` files appear.

### 2. Use Environment Templates
Keep `.env.example` files with placeholder values:
```bash
# .env.example (SAFE to commit)
FACEBOOK_APP_ID=your_app_id_here
FACEBOOK_APP_SECRET=your_app_secret_here
FACEBOOK_ACCESS_TOKEN=your_access_token_here
```

### 3. If You Accidentally Commit Secrets

**Immediately:**
```bash
# Remove from last commit
git reset --soft HEAD~1
git reset HEAD <sensitive_file>
git commit -m "Your commit message"

# OR if already pushed - ROTATE THE SECRETS IMMEDIATELY
# Then rewrite history:
git filter-branch --force --index-filter \
  "git rm -rf --cached --ignore-unmatch <sensitive_file>" \
  --prune-empty --tag-name-filter cat -- --all
git push --force --all
```

**Then rotate ALL exposed credentials:**
- Google OAuth: Regenerate client secret
- Facebook: Generate new app secret & access token
- LinkedIn: Revoke and regenerate tokens

---

## 📋 Current .gitignore Coverage

```
✅ credentials.json
✅ **/.env (all .env files recursively)
✅ **/*.pkl (all pickle files)
✅ AI_Employee_Vault/.linkedin_session/
✅ AI_Employee_Vault/.gmail_token.pkl
✅ AI_Employee_Vault/.gmail_cache.pkl
✅ **/__pycache__/
✅ AI_Employee_Vault/.obsidian/
✅ AI_Employee_Vault/Inbox/
✅ AI_Employee_Vault/Needs_Action/
✅ AI_Employee_Vault/In_Progress/
✅ AI_Employee_Vault/Pending_Approval/
✅ AI_Employee_Vault/Approved/
✅ AI_Employee_Vault/Rejected/
✅ AI_Employee_Vault/Done/
✅ AI_Employee_Vault/Accounting/
✅ AI_Employee_Vault/Invoices/
✅ AI_Employee_Vault/Briefings/
✅ AI_Employee_Vault/Logs/
✅ odoo/odoo-logs/
✅ *.log
✅ .DS_Store, Thumbs.db
```

---

## 🚨 If You See These in Git Status

```
# DO NOT ADD THEM - they should stay untracked
credentials.json        → Keep local only
facebook/.env           → Keep local only
*.pkl files             → Keep local only
.linkedin_session       → Keep local only
```

---

## 🔐 Secure Your Repository

1. **Make repository PRIVATE** on GitHub
2. **Enable branch protection** on main
3. **Use GitHub Secrets** for CI/CD credentials
4. **Regularly rotate** API keys and tokens
5. **Audit git history** periodically for leaks

---

Last Updated: 2026-03-09
