from src.anchor.anchor import GitAnchor
from src.anchor.extractor import GitSourceType
from src.schema.git import TOOLS as GIT_TOOLS
from src.schema.code import TOOLS as CODE_TOOLS
from src.schema.issue import TOOLS as ISSUE_TOOLS
from src.term import Color
from src import term

import logging
import argparse
import os


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Git Anchor - Link issues to commits")

    # Create a mutually exclusive group for repository source
    repo_group = parser.add_mutually_exclusive_group(required=True)
    repo_group.add_argument("--git", help="Link of the git repository", type=str)
    repo_group.add_argument(
        "--from-local", help="Path to local git repository", type=str
    )

    parser.add_argument("--issue", help="Link of the issue", type=str, required=True)

    parser.add_argument("--debug", help="Enable debug mode", action="store_true")

    parser.add_argument("--interactive", help="Show advanced UI", action="store_true")

    return parser.parse_args()


def main():
    args = parse_arguments()

    # Configure logging based on debug flag
    log_level = logging.INFO if args.debug else logging.WARNING

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    # silence httpx logging
    logging.getLogger("httpx").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)

    if args.debug:
        logger.info("Debug mode enabled")

    if args.interactive:
        os.environ["GIT_ANCHOR_INTERACTIVE"] = "TRUE"
        logger.info("Interactive mode enabled")

    if args.from_local:
        ga = GitAnchor(args.issue, args.from_local, source_type=GitSourceType.LOCAL)
    else:
        ga = GitAnchor(args.issue, args.git, source_type=GitSourceType.REMOTE)

    ga.register_tools(GIT_TOOLS)
    ga.register_tools(CODE_TOOLS)
    ga.register_tools(ISSUE_TOOLS)

    logger.info("Finding link between issue and code...")
    (result, token_used) = ga.find_link()

    if args.interactive:
        term.log(
            Color.GREEN, f"found resolving commit: {result} with {token_used} tokens"
        )
    else:
        print(result)
        print(token_used)


if __name__ == "__main__":
    main()
