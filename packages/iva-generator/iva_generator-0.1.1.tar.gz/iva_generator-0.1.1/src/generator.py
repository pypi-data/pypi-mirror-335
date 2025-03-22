import os
import glob
from langchain_core.output_parsers import PydanticOutputParser
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from .models.schemas import DirectoryStructure
from .templates.prompts import creation_template, bug_fix_template
from dotenv import load_dotenv

load_dotenv()
# Create the LLM
llm = ChatGroq(
    model="qwen-2.5-coder-32b",
    temperature=0.2,
)

# Create the parser
parser = PydanticOutputParser(pydantic_object=DirectoryStructure)

# Create the prompts
creation_prompt = ChatPromptTemplate.from_template(
    template=creation_template,
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

bug_fix_prompt = ChatPromptTemplate.from_template(
    template=bug_fix_template,
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

class AIFileGenerator:
    def __init__(self, llm=llm, creation_prompt=creation_prompt, bug_fix_prompt=bug_fix_prompt, parser=parser):
        self.llm = llm
        self.creation_prompt = creation_prompt
        self.bug_fix_prompt = bug_fix_prompt
        self.parser = parser
        
    def generate_structure(self, user_request):
        """Generate a directory structure based on user request"""
        chain = self.creation_prompt | self.llm | self.parser
        return chain.invoke({"user_request": user_request})
    
    def fix_bugs(self, user_request, file_paths, base_dir="."):
        """Generate bug fixes for the specified files"""
        # Read the contents of the files
        file_contents = ""
        for file_path in file_paths:
            full_path = os.path.join(base_dir, file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r') as f:
                    content = f.read()
                file_contents += f"FILE: {file_path}\n```\n{content}\n```\n\n"
            else:
                file_contents += f"FILE: {file_path} (NOT FOUND)\n\n"
        
        # Generate bug fixes
        chain = self.bug_fix_prompt | self.llm | self.parser
        return chain.invoke({
            "user_request": user_request,
            "file_contents": file_contents
        })
    
    def implement_structure(self, structure, base_dir="."):
        """Create the actual directories and files from the structure"""
        # Create directories
        for directory in structure.directories:
            dir_path = os.path.join(base_dir, directory)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                print(f"Created directory: {dir_path}")
        
        # Create or modify files
        for file_info in structure.files:
            # Ensure the directory exists
            file_path = os.path.join(base_dir, file_info.path)
            file_dir = os.path.dirname(file_path)
            if file_dir and not os.path.exists(file_dir):
                os.makedirs(file_dir)
            
            # Handle different file operations
            if file_info.operation == "create":
                if os.path.exists(file_path):
                    print(f"Warning: File already exists, skipping: {file_path}")
                    continue
                with open(file_path, 'w') as f:
                    f.write(file_info.content)
                print(f"Created file: {file_path}")
            
            elif file_info.operation == "modify":
                if not os.path.exists(file_path):
                    print(f"Creating new file (modify operation but file didn't exist): {file_path}")
                else:
                    print(f"Replacing file content: {file_path}")
                with open(file_path, 'w') as f:
                    f.write(file_info.content)
            
            elif file_info.operation == "append":
                if not os.path.exists(file_path):
                    print(f"Creating new file (append operation but file didn't exist): {file_path}")
                    with open(file_path, 'w') as f:
                        f.write(file_info.content)
                else:
                    print(f"Appending to file: {file_path}")
                    with open(file_path, 'a') as f:
                        f.write("\n" + file_info.content)
                        
            elif file_info.operation == "patch":
                if not os.path.exists(file_path):
                    print(f"Error: Cannot patch non-existent file: {file_path}")
                    continue
                with open(file_path, 'r') as f:
                    original_content = f.read()
                with open(file_path, 'w') as f:
                    f.write(file_info.content)
                print(f"Patched file: {file_path}")
        
        # Apply bug fixes
        for bug_fix in structure.bug_fixes:
            file_path = os.path.join(base_dir, bug_fix.file_path)
            if not os.path.exists(file_path):
                print(f"Error: Cannot fix bugs in non-existent file: {file_path}")
                continue
                
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Replace the buggy code with the fixed code
            if bug_fix.original_code in content:
                new_content = content.replace(bug_fix.original_code, bug_fix.fixed_code)
                with open(file_path, 'w') as f:
                    f.write(new_content)
                print(f"Fixed bug in: {file_path}")
                print(f"Bug explanation: {bug_fix.explanation}")
            else:
                print(f"Warning: Could not find the exact bug code in {file_path}")
        
        print("\nExplanation:")
        print(structure.explanation)
        if structure.is_full_project:
            print("Created a complete project structure.")
        else:
            print("Created/modified specific files as requested.")
    
    def find_files(self, pattern, base_dir="."):
        """Find files matching the given pattern"""
        matches = glob.glob(os.path.join(base_dir, pattern))
        return [os.path.relpath(match, base_dir) for match in matches]
    
    def read_file(self, file_path, base_dir="."):
        """Read the content of an existing file"""
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            with open(full_path, 'r') as f:
                return f.read()
        return None
    
    def analyze_request(self, user_request):
        """Determine if this is a bug-fixing request or a file creation request"""
        bug_related_terms = ['bug', 'fix', 'issue', 'error', 'problem', 'debug', 'not working', 'broken']
        return any(term in user_request.lower() for term in bug_related_terms)
    
    def run(self, user_request, base_dir="."):
        """Generate and implement the structure based on user request"""
        print(f"Analyzing request: {user_request}")
        
        # Determine if this is a bug-fixing request
        if self.analyze_request(user_request):
            # Simple heuristic to find potentially mentioned files
            words = user_request.split()
            potential_files = [word for word in words if '.' in word and not word.endswith('.') and not word.startswith(('http://', 'https://'))]
            
            # If no specific files mentioned, ask the user
            if not potential_files:
                file_input = input("Which file(s) need fixing? (comma-separated or use wildcards): ")
                if ',' in file_input:
                    file_patterns = [pattern.strip() for pattern in file_input.split(',')]
                else:
                    file_patterns = [file_input.strip()]
                
                all_files = []
                for pattern in file_patterns:
                    matches = self.find_files(pattern, base_dir)
                    all_files.extend(matches)
            else:
                all_files = []
                for file in potential_files:
                    if os.path.exists(os.path.join(base_dir, file)):
                        all_files.append(file)
            
            if not all_files:
                print("No files found to fix. Please check the file paths.")
                return None
                
            print(f"Fixing bugs in: {', '.join(all_files)}")
            structure = self.fix_bugs(user_request, all_files, base_dir)
        else:
            # Regular file creation/modification
            structure = self.generate_structure(user_request)
            
        self.implement_structure(structure, base_dir)
        return structure