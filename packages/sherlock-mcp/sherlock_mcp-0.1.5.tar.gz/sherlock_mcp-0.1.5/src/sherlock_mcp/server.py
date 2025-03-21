from mcp.server.fastmcp import FastMCP
from sherlock.core import Sherlock
import os


# Create FastMCP instance
mcp = FastMCP("Fewsats MCP Server")


def get_sherlock():
    """Get or create a Sherlock instance. 
    We want to create the class instance inside the tool, 
    so the init errors will bubble up to the tool and hence the MCP client instead of silently failing
    during the server creation.
    """
    return Sherlock()


def handle_response(response):
    """
    Handle responses from Sherlock methods.
    Sherlock methods already process the response using _handle_response,
    which returns either a processed JSON object for successful requests or the response object itself.
    """
    if hasattr(response, 'status_code'):
        # This is a raw response object
        try: return response.status_code, response.json()
        except: return response.status_code, response.text
    # This is already processed data (like a dictionary)
    return response


@mcp.tool()
async def search(q: str) -> str:
    """
    Search for available domains matching the query.
    Returns search results with available/unavailable domains, their prices in USD cents, and a search ID needed for purchase requests.
    The query can be a full domain name with or without the TLD but not subdomains or text.

    Valid queries: 
        - "example"
        - "example.com" 
        - "my-domain"
    
    Invalid queries:
        - "www.example.com"  # no subdomains
        - "this is a search" # no spaces
        - "sub.domain.com"   # no subdomains
    """
    return handle_response(get_sherlock()._search(q))


# @mcp.tool()
# async def me():
#     """
#     Makes an authenticated request to verify the current authentication status and retrieve basic user details.
#     Returns user information including logged_in status, email, and the public key being used for authentication.
#     """
#     return handle_response(get_sherlock().me())


@mcp.tool()
async def claim_account(email: str):
    """
    Links an email address to an AI agent's account for web interface access and account recovery.

    Important notes:
    - Only accounts without an existing email can be linked
    - Each email can only be linked to one account
    - This method is rarely needed since emails are also set during domain registration
    """
    return handle_response(get_sherlock()._claim_account(email))


@mcp.tool()
async def set_contact_information(cfn: str, cln: str, cem: str, cadd: str, cct: str, cst: str, cpc: str, ccn: str):
    """
    Set the contact information that will be used for domain purchases and ICANN registration.
    Contact information must be set before attempting any domain purchases.

    All fields are required:
        first_name: First name
        last_name: Last name
        email: Email address
        address: Street address
        city: City
        state: Two-letter state code for US/Canada (e.g., 'CA', 'NY') or province name (e.g., 'Madrid')
        postal_code: Postal code
        country: Two-letter country code ('US', 'ES', 'FR')
    """
    return handle_response(get_sherlock()._set_contact_information(cfn, cln, cem, cadd, cct, cst, cpc, ccn))


@mcp.tool()
async def get_contact_information():
    """
    Retrieve the currently configured contact information that will be used for domain purchases and ICANN registration.
    """
    return handle_response(get_sherlock()._get_contact_information())


@mcp.tool()
async def get_purchase_offers(sid: str, domain: str):
    """
    Request available payment options for a domain.
    This method returns an L402 offer, which includes details such as offer_id, amount, currency, and more.
    The returned offer can be processed by any tool supporting L402 offers.
    The TLD .ai mandates a minimum registration and renewal period of two years. So inform the user that they need to purchase a 2 year package when they request a .ai domain.

    The L402 offer structure:
    {
        'offers': [
            {
                'offer_id': 'example_offer_id',  # String identifier for the offer
                'amount': 100,                 # Numeric cost value in USD cents
                'currency': 'usd',             # Currency code
                'description': 'Example offer', # Text description
                'title': 'Example Package'      # Title of the package
            }
        ],
        'payment_context_token': 'example_token',  # Payment context token
        'payment_request_url': 'https://api.example.com/payment-request',  # Payment URL
        'version': '0.2.2'  # API version
    }

    sid: Search ID from a previous search request
    domain: Domain name to purchase from the search results related to `sid`
    """

    return handle_response(get_sherlock()._get_purchase_offers(sid, domain))



@mcp.tool()
async def domains():
    """
    List domains owned by the authenticated user.
    Each domain object contains:
        id (str): Unique domain identifier (domain_id in other methods)
        domain_name (str): The registered domain name
        created_at (str): ISO timestamp of domain creation
        expires_at (str): ISO timestamp of domain expiration
        auto_renew (bool): Whether domain is set to auto-renew
        locked (bool): Domain transfer lock status
        private (bool): WHOIS privacy protection status
        nameservers (list): List of nameserver hostnames
        status (str): Domain status (e.g. 'active')
    """
    return handle_response(get_sherlock()._domains())


@mcp.tool()
async def dns_records(domain_id: str):
    """
    Get DNS records for a domain.

    domain_id: Domain UUID (e.g: 'd1234567-89ab-cdef-0123-456789abcdef')
    Each DNS record contains:
        id (str): Unique record identifier
        type (str): DNS record type (e.g. 'A', 'CNAME', 'MX', 'TXT')
        name (str): DNS record name
        value (str): DNS record value
        ttl (int): Time to live in seconds
    """
    return handle_response(get_sherlock()._dns_records(domain_id))


@mcp.tool()
async def create_dns(domain_id: str, type: str = "TXT", name: str = "test", value: str = "test-1", ttl: int = 3600):
    """
    Create a new DNS record for a domain.

    domain_id: Domain UUID (e.g., 'd1234567-89ab-cdef-0123-456789abcdef')
    type: DNS record type ('A', 'AAAA', 'CNAME', 'MX', 'TXT', etc.)
    name: Subdomain or record name (e.g., 'www' creates www.yourdomain.com)
    value: Record value (e.g., IP address for A records, domain for CNAME)
    ttl: Time To Live in seconds (default: 3600)
    """
    return handle_response(get_sherlock()._create_dns_record(domain_id, type, name, value, ttl))


@mcp.tool()
async def update_dns(domain_id: str, record_id: str, type: str = "TXT", name: str = "test-2", value: str = "test-2", ttl: int = 3600):
    """
    Update an existing DNS record for a domain.

    NOTE: Updating a record will change its record id.
    domain_id: Domain UUID (e.g., 'd1234567-89ab-cdef-0123-456789abcdef')
    record_id: DNS record UUID to update
    type: DNS record type ('A', 'AAAA', 'CNAME', 'MX', 'TXT', etc.)
    name: Subdomain or record name (e.g., 'www' for www.yourdomain.com)
    value: New record value (e.g., IP address for A records)
    ttl: Time To Live in seconds (default: 3600)
    """
    return handle_response(get_sherlock()._update_dns_record(domain_id, record_id, type, name, value, ttl))


@mcp.tool()
async def delete_dns(domain_id: str, record_id: str):
    """
    Delete a DNS record for a domain.

    domain_id: Domain UUID (e.g., 'd1234567-89ab-cdef-0123-456789abcdef')
    record_id: DNS record ID to delete
    """
    return handle_response(get_sherlock()._delete_dns_record(domain_id, record_id))


def main():
    mcp.run()
