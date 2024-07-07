import os
import mlflow
import subprocess
import time

MLFLOW_RUN_ID=os.environ["MLFLOW_RUN_ID"]

# Define the directory and repository
directory = "temp_data/weekly-london-cycles-db"
repo_url = "https://github.com/fferegrino/weekly-london-cycles-db"


with mlflow.start_run(run_id=MLFLOW_RUN_ID):
    mlflow.log_param("dataset_repo_url", repo_url)
    t0 = time.time()

    # Check if the directory does not exist
    if not os.path.isdir(directory):
        # Clone the repository with a shallow copy
        subprocess.run(["git", "clone", "-q", "--depth", "1", repo_url, directory])

    else:
        # Directory exists, print a message
        print(f"The repository already exists in the `{directory}` folder.")
    

    os.chdir(directory)

    # Get the latest commit hash
    commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode('utf-8').strip()

    mlflow.log_param("dataset_commit_hash", commit_hash)

    t1 = time.time()

    mlflow.log_metric("dataset_download_time", t1 - t0)