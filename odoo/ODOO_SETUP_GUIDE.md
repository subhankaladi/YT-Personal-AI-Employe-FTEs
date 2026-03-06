# Odoo Setup Guide - Gold Tier

## Problem: Internal Server Error (500)

This error occurs when Odoo is still initializing the database. The initialization takes 2-3 minutes.

## Solution

### Step 1: Stop and Clean (if needed)

```bash
cd odoo
docker-compose down
docker volume rm odoo_odoo-db-data
```

### Step 2: Start Fresh

```bash
docker-compose up -d
```

### Step 3: Wait for Initialization

**IMPORTANT:** Odoo takes 2-3 minutes to initialize the database on first run.

Watch for initialization to complete:

```bash
# Check every 30 seconds
docker-compose logs odoo --tail=20
```

When you see this in the logs, Odoo is ready:
```
INFO ? werkzeug: 172.18.0.1 - - "GET /web HTTP/1.1" 200 -
```

### Step 4: Access Odoo

1. Open: http://localhost:8069

2. Create your database:
   - **Database name:** `odoo`
   - **Email:** `admin@example.com`
   - **Password:** `admin` (CHANGE THIS IMMEDIATELY!)

3. Install modules:
   - Accounting
   - Invoicing
   - CRM
   - Contacts

### Step 5: Configure MCP Server

After setup, update `odoo_mcp_server.py`:

```python
ODOO_URL = "http://localhost:8069"
ODOO_DB = "odoo"
ODOO_USERNAME = "admin@example.com"
ODOO_PASSWORD = "your-new-password"  # Change after first login!
```

## Troubleshooting

### Still Getting 500 Error?

**Check if Odoo is still initializing:**
```bash
docker-compose logs odoo --tail=50
```

**Look for these messages:**
- `Odoo is starting` - Still initializing
- `HTTP service running` - Ready soon
- `200 OK` in werkzeug logs - Ready!

### Database Errors

If you see `relation "ir_module_module" does not exist`:
1. Stop Odoo: `docker-compose down`
2. Remove volume: `docker volume rm odoo_odoo-db-data`
3. Start fresh: `docker-compose up -d`
4. Wait 3 minutes

### Container Keeps Restarting

Check logs for errors:
```bash
docker-compose logs odoo
docker-compose logs db
```

## Quick Start Script

Run the startup script:
```bash
cd odoo
start-odoo.bat
```

This script waits for Odoo to be ready before showing the setup instructions.

## Verify Odoo is Running

```bash
# Check container status
docker-compose ps

# Check logs
docker-compose logs odoo --tail=20

# Test connection
curl http://localhost:8069
```

When you see HTML response (not 500 error), Odoo is ready!

---

*Odoo 19.0 Community Edition - Gold Tier Integration*
