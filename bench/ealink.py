import os
import time
import logging
import pandas as pd

from src.anchor.anchor import GitAnchor
from src.anchor.extractor import GitSourceType
from src.schema.git import TOOLS as GIT_TOOLS
from src.schema.code import TOOLS as CODE_TOOLS
from src.schema.issue import TOOLS as ISSUE_TOOLS
from bench import data_gen

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Silence src.anchor.agent logging
logging.getLogger("src.anchor.agent").setLevel(logging.WARNING)

data_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
)
repos_dir = os.path.join(data_dir, "ealink", "repos")
csv_dir = os.path.join(data_dir, "ealink", "csv")
results_dir = os.path.join(data_dir, "ealink", "results")


def ensure_dataset_available():
    # Check if <data_dir>/ealink/csv directory exists
    if os.path.exists(os.path.join(data_dir, "ealink", "csv")):
        logger.info("EALink dataset already available.")
    else:
        data_gen.prepare_ealink_dataset()


def ensure_repositories_cloned():
    # Check if <data_dir>/ealink/repos directory exists
    if os.path.exists(repos_dir):
        logger.info("EALink target repositories already available.")
    else:
        os.makedirs(repos_dir, exist_ok=True)
        # for all csv file in <ealink/csv> directory, print its name
        for csv_file in os.listdir(csv_dir):
            if csv_file.endswith(".csv"):
                logger.info(f"Cloning repositories for {csv_file}")
                data = pd.read_csv(os.path.join(csv_dir, csv_file))
                for repo_url in data["repo_url"].unique():
                    repo_name = repo_url.split("/")[-1].replace(".git", "")
                    repo_path = os.path.join(repos_dir, repo_name)
                    if not os.path.exists(repo_path):
                        os.system(f"git clone {repo_url} {repo_path}")
                        logger.info(f"Cloned {repo_name} to {repo_path}")
                    else:
                        logger.info(f"{repo_name} already cloned at {repo_path}")


def do_bench_mark():
    os.makedirs(results_dir, exist_ok=True)
    all_token_used = 0

    for csv_file in os.listdir(csv_dir):
        if "calcite" not in csv_file:
            continue

        if csv_file.endswith(".csv"):
            logger.info(f"Running benchmark for {csv_file}")
            data = pd.read_csv(os.path.join(csv_dir, csv_file))
            # iterate over all rows in the dataframe
            # Process data in batches of 100
            batch_size = 2
            for batch_start in range(0, len(data), batch_size):
                batch_end = min(batch_start + batch_size, len(data))
                logger.info("######################################################")
                logger.info(f"Processing batch from {batch_start} to {batch_end - 1}")

                for index in range(batch_start, batch_end):
                    row = data.iloc[index]
                    repo_url: str = row["repo_url"]  # type: ignore
                    repo_name = repo_url.split("/")[-1].replace(".git", "")
                    repo_path = os.path.join(repos_dir, repo_name)
                    issue_url: str = row["issue_url"]  # type: ignore
                    anchor = GitAnchor(
                        issue_url=issue_url,
                        git_repo_source=repo_path,
                        source_type=GitSourceType.LOCAL,
                    )
                    anchor.register_tools(GIT_TOOLS)
                    anchor.register_tools(CODE_TOOLS)
                    anchor.register_tools(ISSUE_TOOLS)
                    try:
                        logger.info(f"Processing {index}'th row...")
                        commit_hash, token_used = anchor.find_link()
                        all_token_used += token_used
                        if all_token_used > 200 * 1000:
                            logger.info(
                                "Token limit reached, cooling down for 30 seconds."
                            )
                            time.sleep(30)
                            all_token_used = 0

                        data.at[index, "result"] = commit_hash
                    except Exception as e:
                        logger.error(f"Error processing {issue_url}: {e}")
                        data.at[index, "error"] = str(e)
                data.to_csv(os.path.join(results_dir, csv_file), index=True)
                logger.info(f"Batch results saved for {batch_start}_{batch_end - 1}")
            logger.info(
                f"Benchmark results saved to {os.path.join(results_dir, csv_file)}"
            )


ensure_dataset_available()
ensure_repositories_cloned()
do_bench_mark()
