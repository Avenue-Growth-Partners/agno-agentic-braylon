"""
Main entry point for AGP Intelligence system.
Handles command line arguments and orchestrates the processing pipeline.
"""
import os
import sys
import argparse
from typing import Optional

from .config import Config
from .utils import validate_input_file, construct_prompt
from .processor import CompanyProcessor


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Run agentic intelligence gathering for companies and store results'
    )
    
    parser.add_argument(
        '-i', '--input', 
        required=True, 
        help='Input CSV file path containing company data'
    )
    parser.add_argument(
        '-o', '--output', 
        required=True, 
        help='Output directory path for results'
    )
    parser.add_argument(
        '--batch-size', 
        type=int, 
        default=Config.DEFAULT_BATCH_SIZE,
        help=f'Batch size for processing (default: {Config.DEFAULT_BATCH_SIZE})'
    )
    parser.add_argument(
        '--workers', 
        type=int, 
        default=Config.DEFAULT_NUM_WORKERS,
        help=f'Number of parallel workers (default: {Config.DEFAULT_NUM_WORKERS})'
    )
    parser.add_argument(
        '--validate-config', 
        action='store_true',
        help='Validate configuration and exit'
    )
    
    return parser.parse_args()


def validate_arguments(args: argparse.Namespace) -> None:
    """
    Validate command line arguments.
    
    Args:
        args: Parsed command line arguments
        
    Raises:
        SystemExit: If validation fails
    """
    # Validate input file exists
    if not os.path.isfile(args.input):
        print(f"Error: Input file '{args.input}' does not exist.")
        sys.exit(1)
    
    # Validate or create output directory
    if not os.path.exists(args.output):
        print(f"Output directory '{args.output}' does not exist. Creating it...")
        try:
            os.makedirs(args.output, exist_ok=True)
        except OSError as e:
            print(f"Error creating output directory: {e}")
            sys.exit(1)
    elif not os.path.isdir(args.output):
        print(f"Error: '{args.output}' exists but is not a directory.")
        sys.exit(1)


def process_companies(
    input_file: str,
    output_dir: str,
    batch_size: Optional[int] = None,
    num_workers: Optional[int] = None
) -> tuple:
    """
    Main processing function for companies.
    
    Args:
        input_file: Path to input CSV file
        output_dir: Directory for output files
        batch_size: Batch size for processing
        num_workers: Number of parallel workers
        
    Returns:
        tuple: (successful_results, failed_results)
    """
    # Load and validate data
    df = validate_input_file(input_file)
    
    # Generate prompts
    prompts = list(df.apply(lambda x: construct_prompt(x), axis=1))
    
    # Initialize processor
    processor = CompanyProcessor(output_dir)
    
    # Process companies
    results, failed = processor.process_companies_parallel(
        prompts=prompts,
        batch_size=batch_size,
        num_workers=num_workers
    )
    
    return results, failed


def main() -> int:
    """
    Main entry point.
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Validate configuration if requested
        if args.validate_config:
            try:
                Config.validate_config()
                print("Configuration validation passed!")
                return 0
            except ValueError as e:
                print(f"Configuration validation failed: {e}")
                return 1
        
        # Validate arguments
        validate_arguments(args)
        
        # Validate configuration
        try:
            Config.validate_config()
        except ValueError as e:
            print(f"Configuration error: {e}")
            print("Please set the required environment variables and try again.")
            return 1
        
        print("Starting AGP Intelligence processing...")
        print(f"Input file: {args.input}")
        print(f"Output directory: {args.output}")
        print(f"Batch size: {args.batch_size}")
        print(f"Workers: {args.workers}")
        
        # Process companies
        results, failed = process_companies(
            input_file=args.input,
            output_dir=args.output,
            batch_size=args.batch_size,
            num_workers=args.workers
        )
        
        # Print summary
        total_processed = len(results) + len(failed)
        success_rate = (len(results) / total_processed * 100) if total_processed > 0 else 0
        
        print(f"Processing Summary:")
        print(f"Successfully processed: {len(results)} companies")
        print(f"Failed: {len(failed)} companies")
        print(f"Success rate: {success_rate:.1f}%")
        print(f"Results saved to: {args.output}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n Processing interrupted by user")
        return 1
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())