"""
Agent setup and configuration for AGP Intelligence system.
Contains agent definitions and team setup.
"""
from typing import List
from pydantic import BaseModel, Field
from agno.tools.jina import JinaReaderTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.agent import Agent
from agno.team.team import Team
from agno.models.openai import OpenAIChat

from .config import Config
from .tool_functions import enrich_company, search_company_in_hubspot
from .agp_verticals import VerticalCategory


class AGPIntelligenceOutput(BaseModel):
    """Output model for AGP Intelligence team."""
    
    name: str = Field(..., description="Name of the company")
    domain: str = Field(..., description="The website domain of the company")
    company_summary: str = Field(..., description="The clean summary from the `scraper_agent`.")
    is_software: bool = Field(..., description="Prediction as to whether the company sells a software product or not. The `software_saas_agent` will determine this. Ensure no companies that sell a hardware device are marked as true")
    is_ai_native: bool = Field(..., description="Prediction as to whether the company is AI native or not. The `ai_native_agent` will determine this.")
    is_vertical: bool = Field(..., description="Prediction as to whether the company is a vertical saas or not. The `vertical_agent` will determine this.")
    reasoning: str = Field(..., description="The reasoning for predictions and the whole context goes here")
    vertical: VerticalCategory = Field(
        ...,
        description="Look at grata vertical and also the summarized description of the company and decide on which vertical this company serves to. Should be one of the options from below:\n"
                   f"{VerticalCategory.instructions()}"
    )
    total_raised: float = Field(..., description="Amount of funding raised in total. If you have good confidence that the company hasn't raised any money return 0. Else if its unknown, return -1. Always return in Millions. Do the conversion properly.")
    is_present_in_hubspot: bool = Field(..., description="If the company is present in hubspot or not. True if present and false if not.")
    hubspot_owner: str = Field(..., description='Who owns the company in hubspot. If company not present in hubspot then mention it as N/A')
    hubspot_agp_tier: str = Field(..., description='What is the AGP Tier of the company in hubspot. If its not present then mention it as N/A. Usual values include Named Account, Unclaimed, Drop Coverage, Portco etc.')
    employees: int = Field(..., description="Number of employees in this company.")
    employee_growth: float = Field(..., description="Employee growth over the last one year")
    grata_vertical: str = Field(..., description="Vertical as mentioned by grata datasource")
    latest_news: List[str] = Field(..., description="Top 5 latest news about the company. List the URLs and a short summary of the article.")
    contact_name: str = Field(..., description="Name of the founder or ceo or any of the c suite people.")
    contact_email: str = Field(..., description="Contact email of the founder or any c-level employee of the company.")
    linkedin_url: str = Field(..., description="Linkedin URL of the company")
    context: str = Field(..., description="What is the context you received to make the predictions. The tools responses are put here as a string.")


def create_scraper_agent() -> Agent:
    """Create the scraper agent for website content extraction."""
    scraper_tools = [
        JinaReaderTools(api_key=Config.JINA_KEY, timeout=100, read_url=True)
    ]

    return Agent(
        name="scraper_agent", 
        role="This agent provides a nice summary of the domain using jina reader",
        model=OpenAIChat(id='gpt-4o-mini', api_key=Config.OPENAI_API_KEY),
        description="You are a scraper agent that uses jina reader tools to provide a summary about a company using the domain.",
        tools=scraper_tools,
        monitoring=True,
        instructions='''
        For the company name and domain, get the markdown using the jina reader tool and provide a nice summary of what the company does.
        Talk about the who the company might sell into and also provide a summary of the AI features present in the website.
        '''
    )


def create_ai_native_agent() -> Agent:
    """Create the AI native prediction agent."""
    scraper_tools = [
        JinaReaderTools(api_key=Config.JINA_KEY, timeout=100, read_url=True)
    ]

    return Agent(
        name="ai_native_agent", 
        role="This agent predicts whether a company is AI native or not",
        model=OpenAIChat(id=Config.AI_NATIVE_MODEL_ID, api_key=Config.OPENAI_API_KEY),
        description="You are a prediction agent that uses scraped information about the company to determine if the company's software product is AI native or not.",
        monitoring=True,
        tools=scraper_tools,
        instructions='''
        Using the scraped summary from the `scraper agent` 
        figure out whether its AI native or not. 
        An AI native company means that the company will have AI/Machine learning workflows that are critical to the software
        and provides real value to the end user. It might also generate or use unique datasets to train/retrain its proprietary AI.
        '''
    )


def create_vertical_agent() -> Agent:
    """Create the vertical SaaS prediction agent."""
    scraper_tools = [
        JinaReaderTools(api_key=Config.JINA_KEY, timeout=100, read_url=True)
    ]

    return Agent(
        name="vertical_agent", 
        role="This agent predicts whether a company is vertical saas or not",
        model=OpenAIChat(id=Config.VERTICAL_MODEL_ID, api_key=Config.OPENAI_API_KEY),
        description="You are a prediction agent that uses scraped information about the company to determine if the company's software product is served towards a specific vertical or not.",
        show_tool_calls=True,
        tools=scraper_tools,
        monitoring=True,
        instructions='''
        Use the scraped website information of the company and predict whether the company is a vertical saas or not.
        The end customer must be from one specific vertical. 
        This is a fine tuned model so you know what is a vertical saas company from your trained examples.
        '''
    )


def create_software_saas_agent() -> Agent:
    """Create the software/SaaS identification agent."""
    scraper_tools = [
        JinaReaderTools(api_key=Config.JINA_KEY, timeout=100, read_url=True)
    ]

    return Agent(
        name="software_saas_agent", 
        role="This agent predicts whether a company sells a software product or not",
        model=OpenAIChat(id="gpt-4o-mini", api_key=Config.OPENAI_API_KEY),
        description="You are a prediction agent that uses scraped information about the company to determine if the company sells a software product or not. If it sells a hardware product or a physical product that can be touched then its not a SaaS product. SaaS products are typically web based software",
        show_tool_calls=True,
        tools=scraper_tools,
        monitoring=True,
        instructions='''
        Use the scraped website information of the company and predict whether the company sells a software product or not.
        The software product must be classified as a SaaS - Software as a Service.
        '''
    )


def create_enricher_agent() -> Agent:
    """Create the company enrichment agent."""
    enricher_tools = [
        GoogleSearchTools(),
        enrich_company
    ]

    return Agent(
        name="enricher_agent", 
        role="This agent searches for a company's domain if its not there and then enriches the company using grata. If domain is available use that domain directly.",
        model=OpenAIChat(id="gpt-4o-mini", api_key=Config.OPENAI_API_KEY),
        description="You are an enricher agent that uses the tool to enrich a company and get more information using grata.",
        tools=enricher_tools,
        show_tool_calls=True,
        monitoring=True,
        instructions='''
        Use the tools wisely to obtain information about the company. Gets information from grata.
        '''
    )


def create_hubspot_agent() -> Agent:
    """Create the HubSpot search agent."""
    hubspot_tools = [
        GoogleSearchTools(),
        search_company_in_hubspot
    ]

    return Agent(
        name="hubspot_agent", 
        role="This agent searches for a company's domain if its not there and then checks if the company is present in hubspot or not. If domain is available use that domain directly.",
        model=OpenAIChat(id="gpt-4o-mini", api_key=Config.OPENAI_API_KEY),
        description="You are a hubspot agent that uses the tool to check if the company is present in hubspot or not.",
        tools=hubspot_tools,
        show_tool_calls=True,
        monitoring=True,
        instructions='''
        Use the tools wisely to check if a company is already added in our CRM. Gets information from hubspot.
        '''
    )


def setup_agents() -> Team:
    """
    Set up and configure the AGP Intelligence team.
    
    Returns:
        Team: Configured team of agents for company intelligence gathering
    """
    # Create individual agents
    ai_native_agent = create_ai_native_agent()
    vertical_agent = create_vertical_agent()
    scraper_agent = create_scraper_agent()
    software_saas_agent = create_software_saas_agent()
    enricher_agent = create_enricher_agent()
    hubspot_agent = create_hubspot_agent()

    # Create intelligence team
    intelligence_agent = Team(
        name="AGP Intelligence Team",
        mode="coordinate",
        model=OpenAIChat("gpt-4o", api_key=Config.OPENAI_API_KEY),
        members=[ai_native_agent, vertical_agent, scraper_agent, software_saas_agent, enricher_agent, hubspot_agent],
        show_tool_calls=True,
        markdown=True,
        description="You are an investor researching about companies and figuring out if the companies are vertical saas and AI native companies.",
        "It also gets information about the company from grata and checks if its already added in Hubspot.",
        instructions=[
            "If the domain is not given for the company, use google search to find the domain of the company.",
            "Enrich the company using grata",
            "Check if the company is present in Hubspot or not and get the relevant details, like `agp_tier` and `company_owner`",
            "Use the scraper agent to get the markdown of the company and summarize it according to instructions",
            "Use the Software SaaS agent to determine whether it sells a software product",
            "Use the AI native agent and the vertical agent to figure out the predictions",
            "Summarize all the outputs and parse it to the response model. Ensure all the outputs are correctly mapped to each column."
        ],
        show_members_responses=True,
        response_model=AGPIntelligenceOutput,
        monitoring=True
    )
    
    return intelligence_agent
