from anchor.anchor import GitAnchor
from schema.git import TOOLS as GIT_TOOLS
from schema.code import TOOLS as CODE_TOOLS
from schema.code import TOOLS as ISSUE_TOOLS
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
# silence httpx logging
logging.getLogger("httpx").setLevel(logging.WARNING)

ga = GitAnchor("https://github.com/pallets/flask/issues/5472", "git@github.com:pallets/flask.git")

ga.register_tools(GIT_TOOLS)
ga.register_tools(CODE_TOOLS)
ga.register_tools(ISSUE_TOOLS)

print("##############")
print(ga.find_link())
