from anchor.anchor import GitAnchor
from schema.git import TOOLS as GIT_TOOLS
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logging.getLogger("httpx").setLevel(logging.WARNING)

ga = GitAnchor("nobari", "git@github.com:pallets/flask.git")

ga.register_tools(GIT_TOOLS)

print("##############")
print(ga.find_link())
