import argparse

import pandas as pd


def is_success(row) -> bool:
    result = row.get("result")
    commit_hash = row.get("commit_hash")
    issue_key_present = row.get("issue_key_present")
    ancestral_distance = row.get("ancestral_distance")

    if pd.notna(result) and pd.notna(commit_hash):
        if str(commit_hash).startswith(str(result)):
            return True

    if pd.notna(issue_key_present) and bool(issue_key_present):
        return True

    if pd.notna(ancestral_distance) and int(ancestral_distance) < 5:
        return True

    return False


def dedup_success(group: pd.DataFrame) -> bool:
    if any(is_success(row) for _, row in group.iterrows()):
        return True

    commit_hashes = set(str(v) for v in group["commit_hash"].dropna())
    results = set(str(v) for v in group["result"].dropna())
    if any(ch.startswith(r) for ch in commit_hashes for r in results):
        return True

    return False


def evaluate(csv_path: str, count: int) -> float:
    data = pd.read_csv(csv_path)
    rows = data.head(count)

    successes = 0
    total = 0

    for issue_url, group in rows.groupby("issue_url", sort=False):
        success = dedup_success(group)
        old = pd.notna(group.iloc[0].get("old")) and bool(group.iloc[0].get("old"))

        if old and not success:
            continue

        total += 1
        if success:
            successes += 1

    if total == 0:
        return 0.0

    score = successes / total
    print(f"Score: {successes}/{total} = {score:.4f} ({score * 100:.2f}%)")
    return score


parser = argparse.ArgumentParser(
    description="Evaluate benchmark results from a CSV file."
)
parser.add_argument("csv", help="Path to the results CSV file")
parser.add_argument(
    "-c", "--count", type=int, required=True, help="Number of rows to evaluate"
)
args = parser.parse_args()

evaluate(args.csv, args.count)
