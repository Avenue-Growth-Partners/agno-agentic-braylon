# AGP Intelligence System

A modularized AI-powered system for gathering comprehensive intelligence on companies. The system uses multiple AI agents to classify companies, enrich data, and integrate with existing CRM systems.

## Features

- **AI-Powered Classification**: Determines if companies are AI-native, vertical SaaS, or software companies
- **Data Enrichment**: Integrates with Grata API for detailed company information
- **CRM Integration**: Checks and updates HubSpot records
- **Parallel Processing**: Efficiently processes large datasets with configurable batch sizes
- **Robust Error Handling**: Includes retry logic, rate limiting, and comprehensive logging
- **Modular Architecture**: Clean separation of concerns for easy maintenance and testing

## System Architecture

```
agp_intelligence/
├── __init__.py              # Package initialization
├── main.py                  # Main entry point and CLI
├── config.py                # Configuration management
├── utils.py                 # Utility functions and decorators
├── integrations.py          # External API integrations
├── tool_functions.py        # Tool functions for AI agents
├── agents.py                # AI agent definitions
├── processor.py             # Batch processing logic
├── agp_verticals.py         # Vertical category definitions
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Installation

1. **Clone or download the modularized code**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   export OPENAI_API_KEY="your_openai_api_key"
   export GRATA_API_KEY="your_grata_api_key"
   export HUBSPOT_API_KEY="your_hubspot_access_token"
   export JINA_KEY="your_jina_api_key"
   export SERPER_API_KEY="your_serper_api_key"  # Optional
   ```

## Usage

### Command Line Interface

Basic usage:
```bash
python -m agp_intelligence.main -i companies.csv -o ./results/
```

Advanced usage with custom parameters:
```bash
python -m agp_intelligence.main \
    -i companies.csv \
    -o ./results/ \
    --batch-size 20 \
    --workers 6
```

Validate configuration:
```bash
python -m agp_intelligence.main --validate-config
```

### Programmatic Usage

```python
from agp_intelligence import process_companies

# Process companies
results, failed = process_companies(
    input_file="companies.csv",
    output_dir="./results",
    batch_size=15,
    num_workers=4
)

print(f"Successfully processed: {len(results)} companies")
print(f"Failed: {len(failed)} companies")
```

### Input File Format

The input CSV file must contain at least one of these columns:
- `name`: Company name
- `domain_key`: Company domain (preferred)

Example CSV:
```csv
name,domain_key
Acme Corp,acme.com
Example Inc,example.org
Tech Startup,
,startup.tech
```

## Configuration

All configuration is managed through environment variables and the `Config` class:

### Required Environment Variables
- `OPENAI_API_KEY`: OpenAI API key for AI agents
- `GRATA_API_KEY`: Grata API key for company enrichment
- `HUBSPOT_API_KEY`: HubSpot access token for CRM integration
- `JINA_KEY`: Jina API key for web scraping

### Optional Environment Variables
- `SERPER_API_KEY`: Serper API key for web search (fallback)

### Processing Configuration
Default values can be overridden via command line or programmatically:
- `DEFAULT_BATCH_SIZE`: 15
- `DEFAULT_NUM_WORKERS`: 4
- `MAX_RETRIES`: 3
- `RATE_LIMIT_PER_MINUTE`: 30

## Output

The system generates several output files:

### Main Results
- `all_results_final.csv`: Complete results for all successfully processed companies
- `all_failed_final.csv`: Details of failed processing attempts

### Progress Files
- `all_results_progress.csv`: Incremental progress updates
- `batch_X_complete.csv`: Results for each completed batch
- `company_X_Y.csv`: Individual company results

### Logs
- `research_processing.log`: Detailed processing logs

### Output Schema

Each successfully processed company includes:
- Basic info: name, domain, description, founded year
- Classifications: is_software, is_ai_native, is_vertical
- Enrichment data: employees, growth, funding, contacts
- CRM status: hubspot presence, owner, tier
- Context: reasoning, latest news, vertical classification

## AI Agents

The system uses multiple specialized AI agents:

1. **Scraper Agent**: Extracts and summarizes website content
2. **Software SaaS Agent**: Identifies software vs hardware companies  
3. **AI Native Agent**: Determines if AI is core to the product (fine-tuned model)
4. **Vertical Agent**: Classifies vertical SaaS companies (fine-tuned model)
5. **Enricher Agent**: Gathers additional company data via Grata
6. **HubSpot Agent**: Checks CRM for existing records

## API Integrations

### Grata Integration
- Company enrichment with employee data, funding, growth metrics
- Contact information and investor details
- Industry classification and keywords

### HubSpot Integration  
- Search for existing company records
- Retrieve ownership and tier information
- Owner name resolution

### Jina Integration
- Web content extraction and summarization
- Clean markdown conversion of company websites

## Development

### Project Structure
```
agp_intelligence/
├── config.py          # Environment & configuration management
├── utils.py           # Utilities, decorators, data processing  
├── integrations.py    # External API clients (Grata, HubSpot)
├── tool_functions.py  # Agent tool function definitions
├── agents.py          # AI agent setup and team configuration
├── processor.py       # Batch processing and parallel execution
├── main.py           # CLI and main entry point
└── agp_verticals.py  # Vertical category enum (existing)
```
### Testing

```bash
# Validate configuration
python -m agp_intelligence.main --validate-config

# Test with small sample
head -5 large_dataset.csv > test_sample.csv
python -m agp_intelligence.main -i test_sample.csv -o ./test_results/
```


### Debug Mode

Enable detailed logging by setting environment variable:
```bash
export PYTHONPATH=.
export LOG_LEVEL=DEBUG
python -m agp_intelligence.main -i input.csv -o output/
```

## Support
harish@avenuegp.com