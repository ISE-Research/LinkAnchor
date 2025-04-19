from anchor.anchor import GitAnchor
from schema.git import TOOLS as GIT_TOOLS
from schema.code import TOOLS as CODE_TOOLS
from schema.issue import TOOLS as ISSUE_TOOLS
from term import Color
import term

import logging
import argparse
import os


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Git Anchor - Link issues to commits")

    parser.add_argument(
        "--git", help="Link of the git repository", type=str, required=True
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

    ga = GitAnchor(args.issue, args.git)

    ga.register_tools(GIT_TOOLS)
    ga.register_tools(CODE_TOOLS)
    ga.register_tools(ISSUE_TOOLS)

    logger.info("Finding link between issue and code...")
    result = ga.find_link()

    if args.interactive:
        term.log(Color.GREEN, f"Resolving commit is: {result}")
    else:
        print(result)


if __name__ == "__main__":
    main()
