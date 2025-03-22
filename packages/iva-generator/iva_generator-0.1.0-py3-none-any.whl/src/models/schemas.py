from pydantic import BaseModel, Field
from typing import List, Dict, Literal

class FileContent(BaseModel):
    path: str = Field(description="The path where the file should be created or modified, including filename")
    content: str = Field(description="The content to write to the file")
    operation: Literal["create", "modify", "append", "patch"] = Field(
        description="Whether to create a new file, completely replace an existing file, append to an existing file, or apply patches"
    )

class FilePatch(BaseModel):
    path: str = Field(description="The path to the file that needs patching")
    patches: List[Dict[str, str]] = Field(description="List of patches with 'original' and 'replacement' text")

class BugFix(BaseModel):
    file_path: str = Field(description="Path to the file with the bug")
    original_code: str = Field(description="The buggy code snippet")
    fixed_code: str = Field(description="The fixed code snippet")
    explanation: str = Field(description="Explanation of what the bug was and how it was fixed")

class DirectoryStructure(BaseModel):
    directories: List[str] = Field(description="List of directories to create", default=[])
    files: List[FileContent] = Field(description="List of files to create or modify with their content", default=[])
    bug_fixes: List[BugFix] = Field(description="List of bug fixes applied", default=[])
    is_full_project: bool = Field(description="Whether this is a full project structure or just specific files")
    explanation: str = Field(description="A brief explanation of the generated structure or modifications")
