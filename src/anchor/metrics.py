import json

from pydantic import BaseModel


class Pattern(BaseModel):
    tools: list[str]

    def __hash__(self):
        return hash(tuple(self.tools))

    def __str__(self):
        return f"{self.tools}"


class Metrics:
    def __init__(self):
        self.patterns: dict[Pattern, int] = {}
        self.tools: dict[str, int] = {}
        self.current_pattern: Pattern = Pattern(tools=[])

    def reset(self):
        self.current_pattern = Pattern(tools=[])

    def flush(self):
        # increment tool call count
        for tool in self.current_pattern.tools:
            if tool not in self.tools:
                self.tools[tool] = 0
            self.tools[tool] += 1

        # increment pattern call count
        key = self.current_pattern
        if key not in self.patterns:
            self.patterns[key] = 0
        self.patterns[key] += 1

        self.reset()

    def call(self, tool: str):
        self.current_pattern.tools.append(tool)

    def report_tools(self) -> dict[str, int]:
        return self.tools

    def report_patterns(self) -> dict[Pattern, int]:
        return self.patterns

    def dump(self, dst: str):
        # dump the metrics to a file
        with open(dst, "w") as f:
            json.dump(
                {
                    "call_count": sum(self.patterns.values()),
                    "patterns": {
                        str(pattern): val for pattern, val in self.patterns.items()
                    },
                    "tools": self.tools,
                },
                f,
                indent=4,
            )
