"""
External API integrations for AGP Intelligence system.
Contains HubSpot and Grata API integration classes.
"""
import json
import pandas as pd
import requests
from time import sleep
from itertools import chain
from hubspot import HubSpot
from requests.exceptions import HTTPError

from .config import Config
from .utils import clean_growth_percentage, clean_funding_value, chunk


class HubspotIntegration:
    """Integration class for HubSpot CRM API."""
    
    def __init__(self, access_token: str):
        """
        Initialize HubSpot integration.
        
        Args:
            access_token: HubSpot API access token
        """
        self.client = HubSpot(access_token=access_token)
        self.properties = [
            "name", "domain", "machine_id", "agp_tier", 
            "hubspot_owner_id", "is_ai_native"
        ]
    
    def search_for_domain(self, domain: str):
        """
        Search for a company by domain in HubSpot.
        
        Args:
            domain: Company domain to search for
            
        Returns:
            Company object if found, error message if not found
        """
        search_request = {
            "filterGroups": [
                {
                    "filters": [
                        {
                            "propertyName": "domain",
                            "operator": "CONTAINS_TOKEN",
                            "value": domain
                        }
                    ]
                }
            ],
            "properties": self.properties,
            "limit": 1
        }
        
        try:
            response = self.client.crm.companies.search_api.do_search(search_request)
            
            if response.results:
                company = response.results[0]
                company_details = self.client.crm.companies.basic_api.get_by_id(
                    company.id, properties=self.properties
                )
                return company_details
            else:
                return "No HubSpot object found for domain:", domain
                
        except Exception as e:
            return f"An error occurred due to {e}. Don't use this response"
    
    def get_company_owner_name(self, owner_id: str) -> str:
        """
        Get company owner name from owner ID.
        
        Args:
            owner_id: HubSpot owner ID
            
        Returns:
            Owner name if found, None otherwise
        """
        return Config.HUBSPOT_OWNER_MAP.get(owner_id)


class GrataIntegration:
    """Integration class for Grata API."""
    
    MILLION = 1e6
    
    def __init__(self, api_key: str, session_token: str = None):
        """
        Initialize Grata integration.
        
        Args:
            api_key: Grata API key
            session_token: Optional session token for scraping
        """
        self.session_token = session_token
        self.api_key = api_key
        
        # API URLs
        base_url = f"https://search.grata.com/api/{Config.GRATA_API_VERSION}"
        self.ENRICH_URL = f"{base_url}/enrich/"
        self.SIMILAR_SEARCH_URL = f"{base_url}/search-similar/"
        self.COMPANY_SEARCH_URL = f"{base_url}/search/"
        self.BULK_ENRICH_URL = f"{base_url}/bulk/enrich/"
        self.ENRICH_URL_SCRAPE = "https://search.grata.com/api/company/"
        
        # Headers
        self.HEADERS = {
            "Content-Type": "application/json",
            "Authorization": self.api_key,
        }
        self.SCRAPE_HEADERS = {
            "Content-Type": "application/json",
            "Authorization": f"{self.session_token}",
        }

    def _call_request(self, method: str, url: str, payload: dict, headers: dict):
        """
        Make HTTP request to Grata API.
        
        Args:
            method: HTTP method (POST or GET)
            url: Request URL
            payload: Request payload
            headers: Request headers
            
        Returns:
            JSON response
            
        Raises:
            HTTPError: For authentication errors
            Exception: For other API errors
        """
        if method == "POST":
            response = requests.request("POST", url, json=payload, headers=headers)
        elif method == "GET":
            response = requests.request("GET", url, headers=headers)
        else:
            raise Exception("Unrecognized method")

        if response.status_code == 200:
            return json.loads(response.content)
        if response.status_code == 401:
            print(f"Response is {response}")
            raise HTTPError(
                "Grata authentication error. "
                "Check if the API key is set. If it is, check if its expired by checking the grata UI"
            )
        
        print(f"The status code is {response.status_code} and response is {response}")
        raise Exception(f"Not able to get response due to {response.raw}")
    
    def _get_company_updated_date(self, comp: dict) -> str:
        """
        Get the most recent update date for a company.
        
        Args:
            comp: Company data dictionary
            
        Returns:
            Most recent update date in YYYY-MM-DD format, None if no date found
        """
        default_time = pd.to_datetime("1900-01-01", utc=True)
        
        # Get funding date
        funding_date = None
        if ("latest_funding" in comp.keys() and 
            "date" in comp["latest_funding"].keys()):
            funding_date = pd.to_datetime(comp["latest_funding"]["date"], utc=True)
        funding_date = funding_date if funding_date is not None else default_time
        
        # Get last crawled date
        last_crawled_date = None
        if "last_crawled" in comp.keys():
            last_crawled_date = pd.to_datetime(comp["last_crawled"], utc=True)
        last_crawled_date = last_crawled_date if last_crawled_date is not None else default_time

        # Get last employment change date
        last_employment_change_date = None
        if "employees_change_last" in comp.keys():
            last_employment_change_date = pd.to_datetime(comp["employees_change_last"], utc=True)
        last_employment_change_date = (
            last_employment_change_date if last_employment_change_date is not None else default_time
        )
        
        last_updated_date = max([funding_date, last_crawled_date, last_employment_change_date])
        return last_updated_date.strftime("%Y-%m-%d") if last_updated_date != default_time else None

    def grata_enrich(self, param: str, format_response: bool = True, param_type: str = 'id'):
        """
        Enrich a company using Grata API.
        
        Args:
            param: Company identifier (ID or domain)
            format_response: Whether to format the response
            param_type: Type of parameter ('id' or 'domain')
            
        Returns:
            Formatted or raw company data
        """
        try:
            if self.api_key is None:
                raise NotImplementedError(
                    "API Key is empty. "
                    "Go to grata UI and find the API key under the account section and set it."
                )
            
            response = None
            if self.session_token is not None and param_type == 'id':
                url = f"{self.ENRICH_URL_SCRAPE}{param}/"
                response = self._call_request("GET", url, None, self.SCRAPE_HEADERS)
            else:
                if param_type == 'id':
                    payload = {"company_uid": param}
                elif param_type == 'domain':
                    payload = {"domain": param}
                else:
                    raise Exception("Invalid param type. Must be one of id or domain.")
                
                response = self._call_request("POST", self.ENRICH_URL, payload, self.HEADERS)
            
            if format_response:
                return self._format_grata_company(response)
            else:
                return response
                
        except Exception as e:
            print(e.args)
            return {}

    def _format_grata_company(self, response: dict) -> dict:
        """
        Format Grata company response into standardized format.
        
        Args:
            response: Raw Grata API response
            
        Returns:
            Formatted company data dictionary
        """
        processed = {}
        try:
            comp = response
            hq_location = None

            # Basic company info
            processed["id"] = comp["company_uid"]
            processed["name"] = comp["name"]
            processed["website"] = comp["domain"]
            processed["year_founded"] = comp["year_founded"]
            processed["description"] = (
                str(comp["description"]).replace("\r", "") 
                if "description" in comp.keys() else None
            )
            processed["linkedin_url"] = comp["social_linkedin"]

            # Employee metrics
            if "employees_growth" in comp.keys() and comp["employees_growth"] is not None:
                processed["employees_growth_six_month"] = (
                    clean_growth_percentage(comp["employees_growth"].get("percent_six_month"))
                )
                processed["growth"] = (
                    clean_growth_percentage(comp["employees_growth"].get("percent_one_year"))
                )
                processed["employees_growth_monthly"] = (
                    clean_growth_percentage(comp["employees_growth"].get("percent_one_month"))
                )
                processed["employees_growth_quarterly"] = (
                    clean_growth_percentage(comp["employees_growth"].get("percent_three_month"))
                )
            else:
                processed["employees_growth_six_month"] = None
                processed["growth"] = None
                processed["employees_growth_monthly"] = None
                processed["employees_growth_quarterly"] = None

            # Employee count
            if ("employees_on_professional_networks" in comp.keys() and
                comp["employees_on_professional_networks"] is not None):
                processed["employees"] = comp["employees_on_professional_networks"].get("count")
            else:
                processed["employees"] = None

            # Business information
            processed["business_models"] = (
                ",".join(comp["business_models"])
                if "business_models" in comp.keys() and comp["business_models"] else ""
            )
            processed["end_customer"] = (
                ",".join(comp["end_customer"])
                if "end_customer" in comp.keys() and comp["end_customer"] else ""
            )
            
            # Vertical classification
            if ("classifications" in comp.keys() and 
                comp["classifications"] and
                "software_industries" in comp["classifications"] and
                comp["classifications"]["software_industries"]):
                processed["vertical"] = comp["classifications"]["software_industries"][0]["industry_name"]
            else:
                processed["vertical"] = ""

            processed["keywords"] = (
                ",".join(comp["keywords"])
                if "keywords" in comp.keys() and comp["keywords"] else ""
            )

            # Contact information
            executive_contact_with_email = []
            if ("contacts" in comp.keys() and 
                comp["contacts"] and 
                "contacts" in comp["contacts"]):
                executive_contact_with_email = [
                    e for e in comp["contacts"]["contacts"]
                    if ("email_deliverability" in e.keys() and
                        e["email_deliverability"] and
                        e["email_deliverability"].lower() in ["high confidence", "potentially deliverable"])
                ]

            if executive_contact_with_email:
                contact = executive_contact_with_email[0]
                processed["contact_name"] = contact.get("name", "")
                processed["contact_title"] = contact.get("title", "")
                processed["contact_email"] = contact.get("work_email", "")
            else:
                processed["contact_name"] = None
                processed["contact_title"] = None
                processed["contact_email"] = None

            # Location breakdown
            if "employee_location_breakdown" in comp.keys():
                us_canada_pct = [
                    loc for loc in comp["employee_location_breakdown"]
                    if ("country" in loc.keys() and
                        loc["country"].lower() in ["united states", "canada"])
                ]
                processed["employee_pct_in_spec"] = sum(
                    loc.get("country_percentage", 0) for loc in us_canada_pct
                )
            else:
                processed["employee_pct_in_spec"] = None

            # Investors
            processed["investors"] = (
                ",".join([c["name"] if isinstance(c, dict) else c for c in comp["investors"]])
                if "investors" in comp.keys() and comp["investors"] else ""
            )

            processed["last_updated_by_datasource"] = self._get_company_updated_date(comp)

            # Web traffic (not available in API yet)
            processed["web_traffic_change_quarter"] = None
            processed["web_traffic_change_yearly"] = None
            processed["web_traffic_change_monthly"] = None
            processed["web_traffic_change_six_month"] = None

            # Location information
            hq_location = [
                loc for loc in comp["locations"]["locations"] 
                if loc["location_type"] == "HQ"
            ]
            hq_location = hq_location[0] if hq_location else {}

            processed["state"] = hq_location.get("region_name")
            processed["city"] = hq_location.get("city_name")
            processed["country"] = hq_location.get("country_name")
            processed["postcode"] = hq_location.get("postal_code")

            # Funding information
            processed["total_raised"] = (
                clean_funding_value(comp["total_funding"])
                if (comp.get("total_funding") and 
                    comp["total_funding"] != "none" and 
                    comp["total_funding"] != "") else 0.0
            )

            return processed
            
        except Exception as e:
            print(e.args)
            print(response)
            return processed

    def bulk_enrich(self, grata_ids: list):
        """
        Bulk enrich multiple companies.
        
        Args:
            grata_ids: List of Grata company IDs
            
        Returns:
            Tuple of (DataFrame with company data, error info)
        """
        id_chunks = chunk(grata_ids, Config.GRATA_BULK_ENRICH_BATCH_SIZE)
        raw_responses = []
        
        for ch in id_chunks:
            ids = list(ch)
            payload = {"company_uids": ids}
            response = self._call_request("POST", self.BULK_ENRICH_URL, payload, self.HEADERS)
            raw_responses.append(response)
            sleep(1)

        companies = [c["companies"] for c in raw_responses]
        companies = list(chain(*companies))
        formatted = [self._format_grata_company(c) for c in companies]
        companies_df = pd.DataFrame(formatted)
        return companies_df, None