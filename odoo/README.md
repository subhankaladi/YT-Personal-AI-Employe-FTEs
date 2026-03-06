# Odoo 19.0 Community Edition - Gold Tier Integration
# Default Admin Credentials (change after first login!)
# Email: admin@example.com
# Password: admin

# Database Configuration
# Host: db (internal Docker network)
# Port: 5432
# User: odoo
# Password: odoo

# External Access
# URL: http://localhost:8069
# JSON-RPC Port: 8069

# API Configuration for MCP Server
# API Key: gold-tier-api-key-2026
# API Endpoint: http://localhost:8069/api/v1

# First Time Setup:
# 1. Start Docker Compose: docker-compose up -d
# 2. Wait 2-3 minutes for Odoo to initialize
# 3. Open http://localhost:8069 in browser
# 4. Create your first database (company name: "AI Employee FTE")
# 5. Install Accounting, Invoicing, and CRM modules
# 6. Configure chart of accounts for your business

# Modules to Install for Gold Tier:
# - Accounting (l10n_generic_co)
# - Invoicing (account)
# - CRM (crm)
# - Contacts (contacts)
# - Settings (base)
