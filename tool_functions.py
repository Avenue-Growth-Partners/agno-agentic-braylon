"""
Tool functions for AGP Intelligence agents.
Contains function definitions that agents can use as tools.
"""
from .config import Config
from .integrations import GrataIntegration, HubspotIntegration


def enrich_company(domain: str) -> str:
    """
    Use this function to enrich a company with more private information
    like employee count, employee growth, funding and other investor details.
    You might also get a vertical information from grata that you can choose
    to verify your answer with. Only use this function if you know the domain. 
    The name of the company alone isn't sufficient to call this function.
    
    Args:
        domain (str): The website of the company. For search, its better to remove the http or https and www. 
                     If the company website is https://acme.com make the domain as acme.com when searching for grata.

    Returns:
        str: A stringified json dict containing all the company information.

    Sample Response:
        {
            "id":"6NKSP6VM",
            "employees_growth_six_month":25.93,
            "employees_growth_monthly":3.03,
            "employees_growth_quarterly":6.25,
            "growth":21.43,
            "employees":"34",
            "business_models":"Software",
            "end_customer":"B2C,B2B",
            "vertical":"Finance",
            "keywords":"home builder,real estate software",
            "contact_name":"John Cecilian",
            "contact_title":"Co-Founder & CEO",
            "contact_email":"john@cecilianpartners.com",
            "investors":"Resolve Growth Partners,Land Advisors Organization,Ben Franklin Technology Partners of Southeastern Pennsylvania",
            "last_updated_by_datasource":"2023-09-28",
            "web_traffic_change_quarter":-12.2,
            "web_traffic_change_yearly":-73.57,
            "web_traffic_change_monthly":-18.41,
            "web_traffic_change_six_month":8.9,
            "employee_pct_in_spec":0.92,
            "name":"Cecilian Partners",
            "website":"cecilianpartners.com",
            "year_founded":2019,
            "description":"Cecilian Partners is a Proptech company built around the customer experience for Community Developers, Home Builders and Homebuyers. We simplify data, digital marketing, and operations by centralizing the entire new home buying process. TECHNOLOGY We have created a real estate software platform that simplifies the management of community development through smart inventory management, lot management and the most accurate anti-repetition algorithm and sophisticated business reporting in the category. SERVICES Our goal is to be an extension of your team, and help you thrive in an ever-changing world of data, technology, and consumer trends. Through storytelling and tailored strategic thinking, we help our clients deliver a modern customer experience.",
            "linkedin_url":"https://www.linkedin.com/company/cecilianpartners/",
            "state":"Pennsylvania",
            "city":"New Hope",
            "country":"United States",
            "postcode":"18938",
            "total_raised":16.86
        }
    """
    try:
        gi = GrataIntegration(api_key=Config.GRATA_API_KEY, session_token=None)
        response = gi.grata_enrich(domain, format_response=True, param_type="domain")
        return str(response)
    except Exception as e:
        print(e.args)
        return "{}"


def search_company_in_hubspot(domain: str) -> str:
    """
    This function allows you to search for a domain and check if its already present in hubspot.
    
    Args:
        domain (str): The domain that needs to be checked in hubspot.
    
    Returns: 
        str: A stringified json object if the company is present in hubspot.
    
    Properties Explanation:
        agp_tier: Named account means its claimed by an investment team member. Unclaimed means its not claimed. 
                 Drop coverage means it is not considered by the investment team anymore. Either its disqualified 
                 immediately or not a fit anymore. 
        is_ai_native: If the company is an AI native software application which means the software workflows are powered by AI.
        machine_id: An identifier if its tracked by machine. Can be used to search in database with this id. 
        hubspot_owner_id: Its an identifier which corresponds to an investment team member. 

    Sample Response: 
        {
            'archived': False,
            'archived_at': None,
            'associations': None,
            'created_at': datetime.datetime(2025, 3, 27, 14, 6, 21, 217000, tzinfo=tzutc()),
            'id': '31455796299',
            'properties': {
                'agp_tier': 'Named Account', 
                'createdate': '2025-03-27T14:06:21.217Z',
                'domain': 'www.interactiveeq.com',
                'hs_lastmodifieddate': '2025-03-27T14:11:37.090Z',
                'hs_object_id': '31455796299',
                'hubspot_owner_id': '79267418',
                'is_ai_native': None,
                'machine_id': None,
                'name': 'InteractiveEQ'
            },
            'updated_at': datetime.datetime(2025, 3, 27, 14, 11, 37, 90000, tzinfo=tzutc())
        }
    """
    try:
        hi = HubspotIntegration(Config.HUBSPOT_ACCESS_TOKEN)
        response = hi.search_for_domain(domain)
        
        if response is not None:
            if isinstance(response, tuple):
                if response[0] == 'No HubSpot object found for domain:':
                    return str(f"The company {response[1]} is not present in Hubspot.")
            if hasattr(response, 'properties') and response.properties is not None:
                response.properties['hubspot_owner'] = hi.get_company_owner_name(
                    response.properties.get('hubspot_owner_id')
                )
        return str(response)
    
    except Exception as e:
        print(e.args)
        return "Error occurred while searching HubSpot"