# Odoo Database Creation - Fix for "Access Denied"

## The Problem

You're getting "Access Denied" when trying to create the database because the master admin password needs to be set.

## Solution - Step by Step

### Step 1: Access Odoo Database Manager

1. Open your browser
2. Go to: **http://localhost:8069/web/database/manager**

### Step 2: Set Master Password

When prompted for "Master Password", enter: **admin**

(This is set in docker-compose.yml via ADMIN_PASSWD environment variable)

### Step 3: Create Database

Click "Create Database" and fill in:

| Field | Value |
|-------|-------|
| **Database Name** | `odoo` |
| **Email** | `admin@example.com` |
| **Password** | `admin` |
| **Confirm Password** | `admin` |
| **Master Password** | `admin` |
| **Demo Data** | ☑️ Check this (for testing) |
| **Language** | English (US) |
| **Country** | Your country |
| **Timezone** | Your timezone |

Click **"Create Database"**

### Step 4: Install Modules

After database is created, you'll see the Apps page. Install these:

1. **Accounting** - Click "Install"
2. **Invoicing** - Click "Install"
3. **CRM** - Click "Install"
4. **Contacts** - Click "Install"

### Step 5: Login

After installation:
- **Email:** admin@example.com
- **Password:** admin

**IMPORTANT:** Change the password immediately after login!

---

## Troubleshooting

### Still Getting "Access Denied"?

Try these alternatives:

**Option 1: Use Database Selector**
1. Go to: http://localhost:8069
2. Click "Manage Databases"
3. Use master password: `admin`

**Option 2: Direct Database Creation URL**
1. Go to: http://localhost:8069/web/database/create
2. Fill in the form above

### "Master Password" Field Missing?

The master password field might be hidden. Try:
1. Go to http://localhost:8069/web/database/manager
2. You should see a password field at the top
3. Enter `admin` there first

### Database Name Error?

Make sure:
- Use only lowercase letters
- No spaces
- Only letters, numbers, underscores, hyphens, or dots
- Example: `odoo`, `my_database`, `odoo-db`

---

## After Setup - Configure MCP Server

Once Odoo is set up, update `odoo_mcp_server.py`:

```python
ODOO_URL = "http://localhost:8069"
ODOO_DB = "odoo"
ODOO_USERNAME = "admin@example.com"
ODOO_PASSWORD = "admin"  # Change to your new password
```

Then test the connection:

```bash
cd odoo
python odoo_mcp_server.py
```

---

## Quick Reference

| URL | Purpose |
|-----|---------|
| http://localhost:8069 | Main Odoo interface |
| http://localhost:8069/web/database/manager | Database management |
| http://localhost:8069/web/database/create | Create new database |
| http://localhost:8069/web/database/selector | Select database |

**Master Password:** admin  
**Default Email:** admin@example.com  
**Default Password:** admin (CHANGE THIS!)
