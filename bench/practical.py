import argparse
import logging
import os
import sys
import time

import pandas as pd

from src import issue_wrapper
from src.anchor.anchor import GitAnchor
from src.anchor.extractor import Extractor, GitSourceType
from src.anchor.metrics import Metrics
from src.schema.code import TOOLS as CODE_TOOLS
from src.schema.control import TOOLS as CONTROL_TOOLS
from src.schema.git import TOOLS as GIT_TOOLS
from src.schema.issue import TOOLS as ISSUE_TOOLS

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
repos_dir = os.path.join(data_dir, "practical", "repos")
csv_file = os.path.join(data_dir, "practical", "data.csv")
results_dir = os.path.join(data_dir, "practical", "results")


def ensure_dataset_available():
    if os.path.exists(os.path.join(data_dir, "practical", "data.csv")):
        logger.info("practical dataset available.")
        return

    raise ValueError(
        "practical dataset not available. Please prepare a dataset in <data/practical/data.csv>."
    )


def ensure_repositories_cloned():
    # Check if <data_dir>/practical/repos directory exists
    if os.path.exists(repos_dir):
        logger.info("target repositories already available.")
        return

    os.makedirs(repos_dir, exist_ok=True)
    data = pd.read_csv(csv_file)
    for repo_url in data["repo_url"].unique():
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        repo_path = os.path.join(repos_dir, repo_name)
        if not os.path.exists(repo_path):
            os.system(f"git clone {repo_url} {repo_path}")
            logger.info(f"Cloned {repo_name} to {repo_path}")
        else:
            logger.info(f"{repo_name} already cloned at {repo_path}")


def extractor_for_repo(repo_url: str, metrics: Metrics) -> Extractor:
    repo = repo_url.split("/")[-1].replace(".git", "")
    repo_dir = os.path.join(repos_dir, repo)
    logger.info(f"setting up extractor for {repo}...")
    e = Extractor.new_for_repo(
        repo_dir, source_type=GitSourceType.LOCAL, metrics=metrics
    )
    logger.info(f"setup extractor for {repo} completed")
    return e


def run_bench(count: int = 100):
    os.makedirs(results_dir, exist_ok=True)
    all_token_used = 0

    metrics = Metrics()
    extractors: dict[str, Extractor] = {}

    logger.info("Running practical benchmark")
    data = pd.read_csv(csv_file)
    for i, (index, row) in enumerate(data.iterrows()):
        if i > count:
            break
        tokens = bench_single_row(row, index, data, extractors, metrics)
        all_token_used += tokens

        data.to_csv(os.path.join(results_dir, csv_file), index=False)
        logger.info(f"results saved up to {index} rows")
        metrics.dump(os.path.join(results_dir, f"metrics-{csv_file}.json"))
        logger.info(f"metrics saved up to {index} rows")


def repair():
    all_token_used = 0
    metrics = Metrics()
    extractors: dict[str, Extractor] = {}

    for csv_file in os.listdir(results_dir):
        metrics.drop()

        if csv_file.endswith(".csv"):
            logger.info(f"Running repair for {csv_file}")
            data = pd.read_csv(os.path.join(results_dir, csv_file))
            for index, row in data.iterrows():
                if pd.isna(data.loc[index, "error"]):
                    continue

                logger.info(f"Repairing {index}'th row...")

                tokens = bench_single_row(row, index, data, extractors, metrics)
                all_token_used += tokens
                if all_token_used > 2000 * 1000:
                    logger.info("Token limit reached, cooling down for 30 seconds.")
                    time.sleep(30)
                    all_token_used = 0

            data.to_csv(os.path.join(results_dir, csv_file))
            logger.info(f"results saved to {os.path.join(results_dir, csv_file)}")


def bench_single_row(row, index, data, extractors, metrics) -> int:
    tokens = 0
    issue_url: str = row["issue_url"]  # type: ignore
    repo_url: str = row["repo_url"]  # type: ignore
    if repo_url not in extractors:
        extractors[repo_url] = extractor_for_repo(repo_url, metrics)

    extractor: Extractor = extractors.get(repo_url)  # type: ignore
    extractor.issue_wrapper = issue_wrapper.wrapper_for(issue_url)
    ga = GitAnchor(extractor)
    ga.register_tools(GIT_TOOLS)
    ga.register_tools(CODE_TOOLS)
    ga.register_tools(ISSUE_TOOLS)
    ga.register_tools(CONTROL_TOOLS)

    logger.info(f"Processing {index}'th row...")
    try:
        ga.extractor.issue_wrapper = issue_wrapper.wrapper_for(issue_url)
        commit_hash, tokens = ga.find_link()
        metrics.flush()

        data.at[index, "result"] = commit_hash
        data.at[index, "error"] = ""
    except Exception as e:
        logger.error(f"Error processing {issue_url}: {e}")
        data.at[index, "error"] = str(e)
    finally:
        metrics.reset()
    return tokens


parser = argparse.ArgumentParser(description="practical benchmark script")
parser.add_argument(
    "--repair", "-r", action="store_true", help="run repair on the benchmark"
)
parser.add_argument(
    "--count", "-c", type=int, help="number of rows to process", default=sys.maxsize
)
args = parser.parse_args()

ensure_dataset_available()
ensure_repositories_cloned()


if args.repair:
    # run repair twice to account for any rate limit issues posed by OpenAI API
    repair()
    repair()
else:
    run_bench(args.count)
