from anchor.anchor import GitAnchor
from schema.git import TOOLS as GIT_TOOLS

ga = GitAnchor("nobari","git@github.com:pallets/flask.git")

ga.register_tools(GIT_TOOLS)

print("##############")
print(ga.find_link())
