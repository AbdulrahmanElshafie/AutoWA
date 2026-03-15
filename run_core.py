import os
import sys
from core.runner import execute_jobs

if __name__ == "__main__":
    # Default path from system contract or allow overriding via command line
    csv_path = "data/jobs.csv" if len(sys.argv) == 1 else sys.argv[1]
    
    csv_full_path = os.path.abspath(csv_path)
    if not os.path.exists(csv_full_path):
        print(f"Error: {csv_full_path} not found.")
        print("Please ensure the data directory and jobs.csv file exist before running.")
        sys.exit(1)
        
    print(f"Starting execution for {csv_full_path}...")
    
    stats = execute_jobs(csv_full_path)
    
    print("Execution completed.")
    print("Results:")
    print(f"  Total   : {stats.get('total', 0)}")
    print(f"  Success : {stats.get('success', 0)}")
    print(f"  Failed  : {stats.get('fail', 0)}")
