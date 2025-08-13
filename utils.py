"""
Utility functions for AGP Intelligence system.
Contains data processing, validation, and helper functions.
"""
import pandas as pd
import numpy as np
import re
import time
import random
import logging
from functools import wraps
from itertools import islice
from pandas import isna, isnull
from numpy import mean


def setup_logging(output_dir: str) -> logging.Logger:
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"{output_dir}/research_processing.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def clean_growth_percentage(growth) -> float:
    """
    Clean and normalize growth percentage values.
    
    Args:
        growth: Raw growth value from data source
        
    Returns:
        float: Cleaned growth percentage or -1 if invalid
    """
    if (
        isna(growth)
        or growth is None
        or isnull(growth)
        or (type(growth) == str and growth.lower() == "none")
    ):
        return -1
    if type(growth) == str:
        try:
            growth = float(growth)
        except Exception:
            return -1
    return round(growth * 100, 2)


def clean_funding_value(funding) -> float:
    """
    Clean and normalize funding values.
    
    Args:
        funding: Raw funding value from data source
        
    Returns:
        float: Cleaned funding value in millions, None if invalid
    """
    if (
        isna(funding)
        or funding is None
        or isnull(funding)
        or (type(funding) == str and funding.lower() == "none")
    ):
        return None
    if type(funding) == str:
        try:
            funding = float(funding)
        except Exception:
            if "bootstrap" in funding.lower() or "bootstrapped" in funding.lower():
                return 0
            if "-" in funding:
                numeric_matches = re.findall(r"\d+", funding)
                return mean([int(s) for s in numeric_matches])
    
    if funding > 1e4:
        return round(funding / 1e6, 2)
    return funding


def chunk(iterable, size):
    """Split an iterable into chunks of specified size."""
    it = iter(iterable)
    return iter(lambda: list(islice(it, size)), [])


def construct_prompt(row) -> str:
    """
    Construct a prompt string from a DataFrame row.
    
    Args:
        row: DataFrame row containing company information
        
    Returns:
        str: Formatted prompt string
    """
    row_dict = row.to_dict()
    name = row_dict.get("name")
    domain = row_dict.get("domain_key")
    
    if name is not None and domain is not None:
        return f"The company name is {name} and the domain is {domain}"
    if name is not None and domain is None:
        return f"The company name is {name}"
    if name is None and domain is not None:
        return f"The company domain is {domain}"
    
    raise ValueError("Row must contain either 'name' or 'domain_key'")


def validate_input_file(file_path: str) -> pd.DataFrame:
    """
    Validate and load input CSV file.
    
    Args:
        file_path: Path to input CSV file
        
    Returns:
        pd.DataFrame: Validated DataFrame with required columns
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If required columns are missing
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file '{file_path}' does not exist.")
    
    df = pd.read_csv(file_path)
    
    if "domain_key" not in df.columns and "name" not in df.columns:
        raise ValueError("Input file must contain either 'domain_key' or 'name' column")
    
    # Filter to only required columns
    cols_to_parse = []
    if "domain_key" in df.columns:
        cols_to_parse.append("domain_key")
    if "name" in df.columns:
        cols_to_parse.append("name")
    
    return df[cols_to_parse]


# Decorator functions for rate limiting and retries
def rate_limit(max_per_minute):
    """Rate limiting decorator."""
    min_interval = 60.0 / max_per_minute
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            to_wait = min_interval - elapsed
            
            if to_wait > 0:
                time.sleep(to_wait)
                
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator


def retry_with_exponential_backoff(
    max_retries=5, 
    initial_delay=1, 
    exponential_base=2, 
    jitter=True
):
    """Retry decorator with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            num_retries = 0
            delay = initial_delay
            
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    num_retries += 1
                    if num_retries > max_retries:
                        logging.error(f"Max retries exceeded: {str(e)}")
                        raise
                    
                    delay *= exponential_base
                    if jitter:
                        delay *= (random.random() + 0.5)  # Between 0.5 and 1.5
                        
                    logging.info(f"Retrying in {delay:.2f} seconds... (Attempt {num_retries}/{max_retries})")
                    time.sleep(delay)
        return wrapper
    return decorator