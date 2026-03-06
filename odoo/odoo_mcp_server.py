# Odoo MCP Server - Gold Tier Integration
# MCP server for Odoo 19.0 Community Edition via JSON-RPC

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import requests
from requests.auth import HTTPBasicAuth

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("odoo-mcp-server")

# Odoo Configuration
ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "odoo")
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "admin@example.com")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "admin")
ODOO_API_KEY = os.getenv("ODOO_API_KEY", "gold-tier-api-key-2026")

class OdooClient:
    """Client for Odoo JSON-RPC API"""
    
    def __init__(self, url: str, db: str, username: str, password: str):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        self.session = requests.Session()
        
    def authenticate(self) -> bool:
        """Authenticate with Odoo and get user ID"""
        try:
            # Common authentication endpoint
            common_url = f"{self.url}/web/session/authenticate"
            payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "db": self.db,
                    "login": self.username,
                    "password": self.password
                },
                "id": 1
            }
            
            response = self.session.post(common_url, json=payload, timeout=10)
            result = response.json()
            
            if result.get("result", {}).get("uid"):
                self.uid = result["result"]["uid"]
                logger.info(f"Authenticated as user {self.uid}")
                return True
            else:
                logger.error("Authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    def execute_kw(self, model: str, method: str, args: List = None, kwargs: Dict = None) -> Any:
        """Execute Odoo model method"""
        if not self.uid:
            if not self.authenticate():
                raise Exception("Not authenticated")
        
        endpoint = f"{self.url}/web/dataset/call_kw"
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": model,
                "method": method,
                "args": args or [],
                "kwargs": kwargs or {}
            },
            "id": 1
        }
        
        try:
            response = self.session.post(endpoint, json=payload, timeout=30)
            result = response.json()
            
            if "error" in result:
                raise Exception(f"Odoo error: {result['error']}")
            
            return result.get("result", {})
            
        except Exception as e:
            logger.error(f"Execute error: {e}")
            raise

# Initialize Odoo client
odoo_client = OdooClient(ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD)

# Create MCP server
server = Server("odoo-mcp")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available Odoo tools"""
    return [
        Tool(
            name="odoo_authenticate",
            description="Authenticate with Odoo server",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "Odoo username/email"},
                    "password": {"type": "string", "description": "Odoo password"}
                },
                "required": ["username", "password"]
            }
        ),
        Tool(
            name="odoo_create_invoice",
            description="Create a new customer invoice in Odoo",
            inputSchema={
                "type": "object",
                "properties": {
                    "partner_name": {"type": "string", "description": "Customer name"},
                    "partner_email": {"type": "string", "description": "Customer email"},
                    "amount": {"type": "number", "description": "Invoice amount"},
                    "description": {"type": "string", "description": "Invoice line description"},
                    "due_date": {"type": "string", "description": "Due date (YYYY-MM-DD)"},
                    "reference": {"type": "string", "description": "Invoice reference"}
                },
                "required": ["partner_name", "amount", "description"]
            }
        ),
        Tool(
            name="odoo_search_invoices",
            description="Search for invoices in Odoo",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {"type": "array", "description": "Odoo domain filter", "items": {"type": "array"}},
                    "limit": {"type": "integer", "description": "Maximum results", "default": 10}
                }
            }
        ),
        Tool(
            name="odoo_create_partner",
            description="Create a new business partner (customer/vendor)",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Partner name"},
                    "email": {"type": "string", "description": "Email address"},
                    "phone": {"type": "string", "description": "Phone number"},
                    "is_customer": {"type": "boolean", "description": "Is this a customer?"},
                    "is_vendor": {"type": "boolean", "description": "Is this a vendor?"}
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="odoo_search_partners",
            description="Search for business partners",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Partner name to search"},
                    "email": {"type": "string", "description": "Email to search"},
                    "limit": {"type": "integer", "description": "Maximum results", "default": 10}
                }
            }
        ),
        Tool(
            name="odoo_create_payment",
            description="Register a payment for an invoice",
            inputSchema={
                "type": "object",
                "properties": {
                    "invoice_id": {"type": "integer", "description": "Invoice ID"},
                    "amount": {"type": "number", "description": "Payment amount"},
                    "payment_date": {"type": "string", "description": "Payment date (YYYY-MM-DD)"},
                    "payment_method": {"type": "string", "description": "Payment method (bank, cash, etc.)"},
                    "reference": {"type": "string", "description": "Payment reference"}
                },
                "required": ["invoice_id", "amount"]
            }
        ),
        Tool(
            name="odoo_get_account_summary",
            description="Get accounting summary (receivables, payables, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "date_from": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "date_to": {"type": "string", "description": "End date (YYYY-MM-DD)"}
                }
            }
        ),
        Tool(
            name="odoo_create_journal_entry",
            description="Create a journal entry in Odoo accounting",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Entry date (YYYY-MM-DD)"},
                    "journal_id": {"type": "integer", "description": "Journal ID"},
                    "ref": {"type": "string", "description": "Reference"},
                    "line_ids": {
                        "type": "array",
                        "description": "Journal entry lines",
                        "items": {
                            "type": "object",
                            "properties": {
                                "account_id": {"type": "integer", "description": "Account ID"},
                                "debit": {"type": "number", "description": "Debit amount"},
                                "credit": {"type": "number", "description": "Credit amount"},
                                "name": {"type": "string", "description": "Line description"}
                            }
                        }
                    }
                },
                "required": ["date", "line_ids"]
            }
        ),
        Tool(
            name="odoo_search_products",
            description="Search for products/services",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Product name"},
                    "default_code": {"type": "string", "description": "Product code"},
                    "limit": {"type": "integer", "description": "Maximum results", "default": 10}
                }
            }
        ),
        Tool(
            name="odoo_execute_custom",
            description="Execute custom Odoo model method",
            inputSchema={
                "type": "object",
                "properties": {
                    "model": {"type": "string", "description": "Odoo model name"},
                    "method": {"type": "string", "description": "Method name"},
                    "args": {"type": "array", "description": "Method arguments"},
                    "kwargs": {"type": "object", "description": "Method keyword arguments"}
                },
                "required": ["model", "method"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Execute Odoo tool"""
    try:
        if name == "odoo_authenticate":
            odoo_client.username = arguments.get("username", ODOO_USERNAME)
            odoo_client.password = arguments.get("password", ODOO_PASSWORD)
            success = odoo_client.authenticate()
            return [TextContent(
                type="text",
                text=json.dumps({"success": success, "uid": odoo_client.uid}, indent=2)
            )]
        
        elif name == "odoo_create_invoice":
            # First, find or create partner
            partner_name = arguments["partner_name"]
            partner_email = arguments.get("partner_email", "")
            
            # Search for existing partner
            partners = odoo_client.execute_kw(
                "res.partner",
                "search_read",
                [[["name", "=", partner_name]]],
                {"limit": 1}
            )
            
            if not partners:
                # Create new partner
                partner_vals = {"name": partner_name}
                if partner_email:
                    partner_vals["email"] = partner_email
                partner_id = odoo_client.execute_kw(
                    "res.partner",
                    "create",
                    [partner_vals]
                )
            else:
                partner_id = partners[0]["id"]
            
            # Create invoice
            invoice_vals = {
                "move_type": "out_invoice",
                "partner_id": partner_id,
                "invoice_line_ids": [(0, 0, {
                    "name": arguments["description"],
                    "price_unit": arguments["amount"],
                    "quantity": 1.0
                })]
            }
            
            if arguments.get("due_date"):
                invoice_vals["invoice_date_due"] = arguments["due_date"]
            if arguments.get("reference"):
                invoice_vals["ref"] = arguments["reference"]
            
            invoice_id = odoo_client.execute_kw("account.move", "create", [invoice_vals])
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "invoice_id": invoice_id,
                    "partner_id": partner_id,
                    "message": f"Invoice created successfully"
                }, indent=2)
            )]
        
        elif name == "odoo_search_invoices":
            domain = arguments.get("domain", [])
            limit = arguments.get("limit", 10)
            
            invoices = odoo_client.execute_kw(
                "account.move",
                "search_read",
                [domain],
                {
                    "fields": ["id", "name", "partner_id", "amount_total", "amount_due", 
                              "invoice_date", "invoice_date_due", "state", "payment_state"],
                    "limit": limit
                }
            )
            
            return [TextContent(
                type="text",
                text=json.dumps({"invoices": invoices}, indent=2)
            )]
        
        elif name == "odoo_create_partner":
            partner_vals = {
                "name": arguments["name"],
                "email": arguments.get("email", ""),
                "phone": arguments.get("phone", ""),
                "customer_rank": 1 if arguments.get("is_customer", True) else 0,
                "supplier_rank": 1 if arguments.get("is_vendor", False) else 0
            }
            
            partner_id = odoo_client.execute_kw("res.partner", "create", [partner_vals])
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "partner_id": partner_id,
                    "message": f"Partner '{arguments['name']}' created successfully"
                }, indent=2)
            )]
        
        elif name == "odoo_search_partners":
            domain = []
            if arguments.get("name"):
                domain.append(["name", "ilike", arguments["name"]])
            if arguments.get("email"):
                domain.append(["email", "=", arguments["email"]])
            
            limit = arguments.get("limit", 10)
            
            partners = odoo_client.execute_kw(
                "res.partner",
                "search_read",
                [domain],
                {
                    "fields": ["id", "name", "email", "phone", "customer_rank", "supplier_rank"],
                    "limit": limit
                }
            )
            
            return [TextContent(
                type="text",
                text=json.dumps({"partners": partners}, indent=2)
            )]
        
        elif name == "odoo_create_payment":
            # Register payment on invoice
            invoice_id = arguments["invoice_id"]
            amount = arguments["amount"]
            
            # Get invoice journal
            invoice = odoo_client.execute_kw(
                "account.move",
                "read",
                [[invoice_id]],
                {"fields": ["journal_id"]}
            )[0]
            
            payment_vals = {
                "journal_id": invoice["journal_id"][0],
                "payment_type": "inbound",
                "partner_type": "customer",
                "partner_id": False,  # Will be set from invoice
                "amount": amount,
                "date": arguments.get("payment_date", ""),
                "ref": arguments.get("reference", "")
            }
            
            payment_id = odoo_client.execute_kw("account.payment", "create", [payment_vals])
            
            # Reconcile with invoice
            odoo_client.execute_kw("account.payment", "action_post", [[payment_id]])
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "payment_id": payment_id,
                    "message": f"Payment of {amount} registered successfully"
                }, indent=2)
            )]
        
        elif name == "odoo_get_account_summary":
            # Get total receivables and payables
            date_from = arguments.get("date_from", "")
            date_to = arguments.get("date_to", "")
            
            domain = []
            if date_from:
                domain.append(["date", ">=", date_from])
            if date_to:
                domain.append(["date", "<=", date_to])
            
            # Get invoice totals
            invoices_out = odoo_client.execute_kw(
                "account.move",
                "search_read",
                [[["move_type", "in", ["out_invoice", "out_refund"]]] + domain],
                {"fields": ["amount_total", "amount_residual"]}
            )
            
            invoices_in = odoo_client.execute_kw(
                "account.move",
                "search_read",
                [[["move_type", "in", ["in_invoice", "in_refund"]]] + domain],
                {"fields": ["amount_total", "amount_residual"]}
            )
            
            total_receivable = sum(inv["amount_residual"] for inv in invoices_out)
            total_payable = sum(inv["amount_residual"] for inv in invoices_in)
            total_revenue = sum(inv["amount_total"] for inv in invoices_out)
            total_expenses = sum(inv["amount_total"] for inv in invoices_in)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "period": f"{date_from or 'all'} to {date_to or 'all'}",
                    "receivables": total_receivable,
                    "payables": total_payable,
                    "revenue": total_revenue,
                    "expenses": total_expenses,
                    "profit": total_revenue - total_expenses,
                    "invoice_count": len(invoices_out),
                    "bill_count": len(invoices_in)
                }, indent=2)
            )]
        
        elif name == "odoo_create_journal_entry":
            entry_vals = {
                "date": arguments["date"],
                "journal_id": arguments.get("journal_id", 1),
                "ref": arguments.get("ref", ""),
                "line_ids": [
                    (0, 0, {
                        "account_id": line["account_id"],
                        "debit": line.get("debit", 0),
                        "credit": line.get("credit", 0),
                        "name": line.get("name", "")
                    })
                    for line in arguments["line_ids"]
                ]
            }
            
            entry_id = odoo_client.execute_kw("account.move", "create", [entry_vals])
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "entry_id": entry_id,
                    "message": "Journal entry created successfully"
                }, indent=2)
            )]
        
        elif name == "odoo_search_products":
            domain = []
            if arguments.get("name"):
                domain.append(["name", "ilike", arguments["name"]])
            if arguments.get("default_code"):
                domain.append(["default_code", "=", arguments["default_code"]])
            
            limit = arguments.get("limit", 10)
            
            products = odoo_client.execute_kw(
                "product.template",
                "search_read",
                [domain],
                {
                    "fields": ["id", "name", "default_code", "list_price", "standard_price"],
                    "limit": limit
                }
            )
            
            return [TextContent(
                type="text",
                text=json.dumps({"products": products}, indent=2)
            )]
        
        elif name == "odoo_execute_custom":
            model = arguments["model"]
            method = arguments["method"]
            args = arguments.get("args", [])
            kwargs = arguments.get("kwargs", {})
            
            result = odoo_client.execute_kw(model, method, args, kwargs)
            
            return [TextContent(
                type="text",
                text=json.dumps({"result": result}, indent=2)
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
            
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]

async def main():
    """Run the Odoo MCP server"""
    logger.info("Starting Odoo MCP Server...")
    logger.info(f"Odoo URL: {ODOO_URL}")
    logger.info(f"Database: {ODOO_DB}")
    
    # Try to authenticate
    if odoo_client.authenticate():
        logger.info("Successfully authenticated with Odoo")
    else:
        logger.warning("Could not authenticate with Odoo. Will retry on first tool call.")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
