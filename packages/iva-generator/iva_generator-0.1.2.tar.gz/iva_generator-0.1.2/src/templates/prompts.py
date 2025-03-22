from langchain_core.prompts import ChatPromptTemplate

creation_template = """
You are a code generation assistant that creates file structures and code based on user requirements.
Given the following user request, determine whether the user wants a full project structure or just specific files.

USER REQUEST: {user_request}

If the user specifically asks for a full project or a complete application, generate a complete directory structure with all necessary files.
Otherwise, create or modify only the specific files needed to fulfill the request.

For each file, specify whether it should be created from scratch, completely replaced, or appended to.

{format_instructions}
"""

bug_fix_template = """
You are a code debugging assistant that analyzes and fixes bugs in code.
The user has requested a bug fix with the following details:

USER REQUEST: {user_request}

Here is the content of the relevant file(s):

{file_contents}

Carefully analyze the code, identify any bugs or issues, and provide fixes.
Make your changes minimal and focused on fixing the specific issues.

{format_instructions}
"""
