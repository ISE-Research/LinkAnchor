from pydantic import BaseModel, Field
from anchor.extractor import Extractor


class FetchFunctionDefinition(BaseModel):
    """Fetch function definition from the codebase"""

    name: str = Field(
        ...,
        description="in a format of '<TYPE>.<FUNCTION>()' for methods or '<FUNCTION>()' for standalone functions",
    )
    commit: str = Field(
        ..., description="commit hash of the commit to fetch the function from"
    )
    file_path: str = Field(
        ..., description="file path of the file in repo to fetch the function from"
    )

    def __call__(self, anchor: Extractor) -> str:
        return anchor.fetch_definition(self.name, self.commit, self.file_path)


class FetchFunctionDocumentation(BaseModel):
    """Fetch function documentation from the codebase"""

    name: str = Field(
        ...,
        description="in a format of '<TYPE>.<FUNCTION>()' for methods or '<FUNCTION>()' for standalone functions",
    )
    commit: str = Field(
        ..., description="commit hash of the commit to fetch the function from"
    )
    file_path: str = Field(
        ..., description="file path of the file in repo to fetch the function from"
    )

    def __call__(self, anchor: Extractor) -> str:
        return anchor.fetch_documentation(
            self.name, self.commit, self.file_path
        )


class FetchClassDefinition(BaseModel):
    """Fetch class definition from the codebase"""

    name: str = Field(
        ...,
        description="name of the type, struct, or class to fetch the definition of",
    )
    commit: str = Field(
        ..., description="commit hash of the commit to fetch the class from"
    )
    file_path: str = Field(
        ..., description="file path of the file in repo to fetch the class from"
    )

    def __call__(self, anchor: Extractor) -> str:
        return anchor.fetch_definition(self.name, self.commit, self.file_path)


class FetchClassDocumentation(BaseModel):
    """Fetch class documentation from the codebase"""

    name: str = Field(
        ...,
        description="name of the type, struct, or class to fetch the documentation of",
    )
    commit: str = Field(
        ..., description="commit hash of the commit to fetch the class from"
    )
    file_path: str = Field(
        ..., description="file path of the file in repo to fetch the class from"
    )

    def __call__(self, anchor: Extractor) -> str:
        return anchor.fetch_documentation(self.name, self.commit, self.file_path)


class FetchLinesOfFile(BaseModel):
    """Fetch lines of file from the codebase"""

    commit: str = Field(
        ..., description="commit hash of the commit to fetch the lines in file from"
    )
    file_path: str = Field(
        ..., description="file path of the file in repo to fetch the lines from"
    )
    start: int = Field(..., description="start line number")
    end: int = Field(..., description="end line number")

    def __call__(self, anchor: Extractor) -> str:
        return anchor.fetch_lines_of_file(
            self.commit, self.file_path, self.start, self.end
        )


TOOLS = [
    FetchFunctionDefinition,
    FetchFunctionDocumentation,
    FetchClassDefinition,
    FetchClassDocumentation,
    FetchLinesOfFile,
]
