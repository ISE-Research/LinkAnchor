from anchor.anchor import GitAnchor
from schema.git import TOOLS as GIT_TOOLS

ga = GitAnchor("mamad","nobari")

ga.register_tools(GIT_TOOLS)

print(ga.find_link())
