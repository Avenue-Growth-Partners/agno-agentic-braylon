"""
Processing module for AGP Intelligence system.
Handles batch processing and parallel execution.
"""
import time
import pandas as pd
import concurrent.futures
from tqdm import tqdm
from agno.agent import RunResponse

from .config import Config
from .utils import rate_limit, retry_with_exponential_backoff, setup_logging
from .agents import setup_agents


class CompanyProcessor:
    """Main processor class for handling company intelligence gathering."""
    
    def __init__(self, output_dir: str):
        """
        Initialize the processor.
        
        Args:
            output_dir: Directory for output files
        """
        self.output_dir = output_dir
        self.logger = setup_logging(output_dir)
        
    @retry_with_exponential_backoff(
        max_retries=Config.MAX_RETRIES, 
        initial_delay=Config.INITIAL_RETRY_DELAY
    )
    @rate_limit(max_per_minute=Config.RATE_LIMIT_PER_MINUTE)
    def process_company(self, intelligence_agent, prompt: str) -> dict:
        """
        Process a single company with retry logic and rate limiting.
        
        Args:
            intelligence_agent: The agent team for processing
            prompt: Company prompt string
            
        Returns:
            dict: Processed company data
            
        Raises:
            Exception: If processing fails after retries
        """
        try:
            structured_output_response: RunResponse = intelligence_agent.run(prompt)
            return structured_output_response.content.__dict__
        except Exception as e:
            self.logger.error(f"Error processing prompt: {prompt}. Error: {str(e)}")
            raise  # Let the retry decorator handle it

    def process_batch(self, intelligence_agent, batch_prompts: list, batch_num: int) -> tuple:
        """
        Process a batch of companies sequentially.
        
        Args:
            intelligence_agent: The agent team for processing
            batch_prompts: List of prompts to process
            batch_num: Batch number for identification
            
        Returns:
            tuple: (results, failed_prompts)
        """
        results = []
        failed_prompts = []
        
        for prompt in tqdm(batch_prompts, desc=f"Processing batch {batch_num} sequentially"):
            try:
                result = self.process_company(intelligence_agent, prompt)
                results.append(result)
                # Save individual result immediately to prevent data loss on crashes
                pd.DataFrame([result]).to_csv(
                    f'{self.output_dir}/company_{len(results)}_{batch_num}.csv', 
                    index=False
                )
            except Exception as e:
                self.logger.error(f"Failed to process {prompt}: {str(e)}")
                failed_prompts.append({"prompt": prompt, "error": str(e)})
        
        # Save batch results
        if results:
            resp_df = pd.DataFrame(results)
            resp_df.to_csv(f'{self.output_dir}/batch_{batch_num}_complete.csv', index=False)
            
        # Save failed prompts for retry later
        if failed_prompts:
            pd.DataFrame(failed_prompts).to_csv(
                f'{self.output_dir}/batch_{batch_num}_failed.csv', 
                index=False
            )
        
        return results, failed_prompts

    def process_companies_parallel(
        self, 
        prompts: list, 
        batch_size: int = None, 
        num_workers: int = None
    ) -> tuple:
        """
        Process companies in parallel batches.
        
        Args:
            prompts: List of company prompts
            batch_size: Size of each batch (defaults to config value)
            num_workers: Number of parallel workers (defaults to config value)
            
        Returns:
            tuple: (all_results, all_failed)
        """
        if batch_size is None:
            batch_size = Config.DEFAULT_BATCH_SIZE
        if num_workers is None:
            num_workers = Config.DEFAULT_NUM_WORKERS
            
        start_time = time.time()
        total_companies = len(prompts)
        
        self.logger.info(f"Total companies to process: {total_companies}")
        self.logger.info(f"Batch size: {batch_size}, Workers: {num_workers}")
        
        all_results = []
        all_failed = []
        
        # Create a ThreadPoolExecutor for processing batches in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = []
            
            # Submit batch processing jobs
            for batch_num, i in enumerate(range(0, len(prompts), batch_size), 1):
                batch_prompts = prompts[i:i+batch_size]
                # Each batch gets its own intelligence_agent instance to avoid concurrency issues
                batch_agent = setup_agents()
                future = executor.submit(
                    self.process_batch, 
                    batch_agent, 
                    batch_prompts, 
                    batch_num
                )
                futures.append(future)
                
                # Don't overwhelm the system, submit a few batches at a time
                if len(futures) >= num_workers * 2 or i + batch_size >= len(prompts):
                    for future in concurrent.futures.as_completed(futures):
                        results, failed = future.result()
                        all_results.extend(results)
                        all_failed.extend(failed)
                    futures = []  # Reset futures list
                    
                    # Save overall progress
                    self._save_progress(all_results, all_failed)
        
        # Final save of all results
        self._save_final_results(all_results, all_failed)
        
        # Calculate and log timing information
        end_time = time.time()
        total_time = end_time - start_time
        
        self.logger.info(f"Processed {len(all_results)} companies successfully")
        self.logger.info(f"Failed to process {len(all_failed)} companies")
        self.logger.info(f"Total time taken: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
        self.logger.info(f"Average time per company: {total_time/total_companies:.2f} seconds")
        
        return all_results, all_failed

    def _save_progress(self, all_results: list, all_failed: list):
        """Save progress to files."""
        if all_results:
            pd.DataFrame(all_results).to_csv(
                f'{self.output_dir}/all_results_progress.csv', 
                index=False
            )
        if all_failed:
            pd.DataFrame(all_failed).to_csv(
                f'{self.output_dir}/all_failed_progress.csv', 
                index=False
            )

    def _save_final_results(self, all_results: list, all_failed: list):
        """Save final results to files."""
        if all_results:
            pd.DataFrame(all_results).to_csv(
                f'{self.output_dir}/all_results_final.csv', 
                index=False
            )
        if all_failed:
            pd.DataFrame(all_failed).to_csv(
                f'{self.output_dir}/all_failed_final.csv', 
                index=False
            )