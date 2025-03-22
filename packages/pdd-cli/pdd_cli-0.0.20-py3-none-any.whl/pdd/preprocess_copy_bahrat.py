from rich import print as rprint
import re
import os
import subprocess
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List, Optional

def get_file_path(file_name: str) -> str:
    """
    Resolves a file path using the current directory as the base path.
    
    Args:
        file_name: The name of the file to resolve
        
    Returns:
        The full path to the file
    """
    path = Path(file_name)
    
    # If it's an absolute path, return it as is
    if path.is_absolute():
        return str(path)
        
    # If path already exists relative to cwd, use it directly
    if path.exists():
        return str(path.resolve())
    
    # Check if the path exists relative to PDD_PATH
    if 'PDD_PATH' in os.environ:
        pdd_path = Path(os.environ['PDD_PATH'])
        if (pdd_path / path).exists():
            return str(pdd_path / path)
            
    # If the path has pdd in it, try removing one level
    parts = list(path.parts)
    if 'pdd' in parts:
        if len(parts) > 1 and parts[0] == 'pdd':
            adjusted_path = Path(*parts[1:])
            if adjusted_path.exists():
                return str(adjusted_path.resolve())
    
    # If we got here, use the original path resolution logic
    if 'PDD_PATH' in os.environ:
        base_path = Path(os.environ['PDD_PATH'])
    else:
        base_path = Path.cwd()
    
    # Get the project root - if we're in a directory named 'pdd' and we're including a file that might also have 'pdd' in its path
    # Make sure we don't add 'pdd' twice
    full_path = base_path / file_name
    
    # Check if base_path already ends with 'pdd' and file_name starts with 'pdd/'
    if base_path.name == 'pdd' and isinstance(file_name, str) and file_name.startswith('pdd/'):
        # Remove the 'pdd/' prefix from file_name to avoid duplication
        file_name_without_pdd = file_name[4:]  # Skip 'pdd/'
        full_path = base_path / file_name_without_pdd
        
    return str(full_path)

def preprocess(
    prompt: str,
    recursive: bool = True,
    double_curly_brackets: bool = True,
    exclude_keys: Optional[List[str]] = None
) -> str:
    """
    Preprocess a prompt string for an LLM by handling specific XML-like tags.
    
    Args:
        prompt: The prompt string to preprocess
        recursive: Whether to recursively process includes in the prompt
        double_curly_brackets: Whether to double curly brackets in the prompt
        exclude_keys: List of keys to exclude from curly bracket doubling
        
    Returns:
        The preprocessed prompt string
    """
    if not prompt:
        rprint("[bold red]Error:[/bold red] No prompt provided.")
        return ""

    if exclude_keys is None:
        exclude_keys = []

    try:
        # Replace separate regex calls with a unified tag processing approach
        def process_tags(prompt):
            # Define a function to handle different tag types
            def tag_handler(match):
                pre_whitespace = match.group(1)
                tag_type = match.group(2)
                content = match.group(3) if match.group(3) else ""
                post_whitespace = match.group(4)
                
                # Skip processing if it looks like an example (contains backticks or is in code format)
                if '`' in pre_whitespace or '`' in post_whitespace:
                    return match.group(0)  # Return unchanged
                    
                if tag_type == 'pdd':
                    return pre_whitespace + post_whitespace  # Remove pdd comments
                elif tag_type == 'shell':
                    # Process shell commands
                    command = content.strip()
                    try:
                        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
                        return pre_whitespace + result.stdout + post_whitespace
                    except Exception as e:
                        # Return the original tag on error (critical for regression tests)
                        return match.group(0)
                elif tag_type == 'web':
                    # Process web content
                    url = content.strip()
                    try:
                        response = requests.get(url)
                        response.raise_for_status()
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Remove scripts, styles, and navigation elements
                        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                            element.decompose()
                        
                        # Extract meaningful content
                        main_content = soup.find('main') or soup.find('article') or soup.find('div', {'id': 'content'})
                        
                        if main_content:
                            result_content = main_content.get_text(strip=True)
                        else:
                            # Fallback to body content
                            result_content = soup.body.get_text(strip=True)
                        return pre_whitespace + result_content + post_whitespace
                    except Exception as e:
                        # Return the original tag on error
                        return match.group(0)
                elif tag_type == 'include':
                    # Process file includes
                    file_name = content.strip()
                    # Skip if it contains invalid characters or looks like an example
                    if len(file_name) > 255 or any(c in file_name for c in '<>"\'|*?'):
                        return match.group(0)  # Return unchanged
                        
                    try:
                        file_path = get_file_path(file_name)
                        with open(file_path, 'r', encoding='utf-8') as file:
                            included_content = file.read()
                            if recursive:
                                # Recursive processing
                                included_content = preprocess(
                                    included_content,
                                    recursive=True,
                                    double_curly_brackets=double_curly_brackets,
                                    exclude_keys=exclude_keys
                                )
                            return pre_whitespace + included_content + post_whitespace
                    except Exception as e:
                        # Return the original tag on error
                        return match.group(0)
                
            # Use a more specific regex pattern that properly handles tag structure
            pattern = r'(\s*)<(include|pdd|shell|web)(?:\s+[^>]*)?(?:>(.*?)</\2>|/|>)(\s*)'
            return re.sub(pattern, tag_handler, prompt, flags=re.DOTALL)

        # Apply the unified tag processing approach
        prompt = process_tags(prompt)

        # Process angle brackets in triple backticks
        def triple_backtick_include(match):
            full_content = match.group(0)  # The entire match including the backticks
            backtick_content = match.group(1)  # Just the content between backticks
            
            # Find angle brackets within the backtick content
            def angle_bracket_replace(inner_match):
                file_name = inner_match.group(1)
                try:
                    file_path = get_file_path(file_name)
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        if recursive:
                            return preprocess(
                                content,
                                recursive=True,
                                double_curly_brackets=double_curly_brackets,
                                exclude_keys=exclude_keys
                            )
                        return content
                except FileNotFoundError:
                    rprint(f"[bold red]File not found:[/bold red] {file_name}")
                    return f"<{file_name}>"
                except Exception as e:
                    rprint(f"[bold red]Error including file {file_name}:[/bold red] {e}")
                    return f"<{file_name}>"
            
            # Replace angle brackets in backtick content
            processed_content = re.sub(r"<([^>]+)>", angle_bracket_replace, backtick_content)
            return f"```{processed_content}```"
        
        prompt = re.sub(r'```(.*?)```', triple_backtick_include, prompt, flags=re.DOTALL)
        
        # Double curly brackets if needed
        if double_curly_brackets:
            # Initialize exclude_keys if it's None
            exclude_keys = exclude_keys or []
            
            # Handle simple cases first with character-by-character approach
            if "\n" not in prompt and "```" not in prompt:
                # Simple case: Character-by-character replacement
                output = ""
                i = 0
                while i < len(prompt):
                    if prompt[i] == '{':
                        # Check if this is part of an excluded key
                        excluded = False
                        for key in exclude_keys:
                            if i + 1 + len(key) + 1 <= len(prompt) and prompt[i+1:i+1+len(key)] == key and prompt[i+1+len(key)] == '}':
                                output += '{' + key + '}'
                                i += 2 + len(key)  # Skip the key and both braces
                                excluded = True
                                break
                        if not excluded:
                            output += '{{'
                            i += 1
                    elif prompt[i] == '}':
                        output += '}}'
                        i += 1
                    else:
                        output += prompt[i]
                        i += 1
                return output.rstrip() if prompt.rstrip() == prompt else output
            
            # More complex case: Use regex for structured text
            # Step 1: Create a function to handle the pattern replacement
            def replacer(match):
                # Extract the content inside the curly braces
                content = match.group(1)
                
                # If the content is empty or in the exclude_keys list, don't double it
                if not content:  # Handle empty braces: {}
                    return "{{}}"
                elif content in exclude_keys:
                    return f"{{{content}}}"
                else:
                    return f"{{{{{content}}}}}"
            
            # Step 2: Process code blocks and regular text separately
            # Split the text into code blocks and non-code blocks
            parts = re.split(r'(```.*?```)', prompt, flags=re.DOTALL)
            
            for i in range(len(parts)):
                if i % 2 == 0:  # Not in a code block
                    # Handle JSON-like structures and nested braces more carefully
                    if ":" in parts[i] and "{" in parts[i] and "}" in parts[i]:
                        # For JSON-like structures, first preserve excluded keys
                        for key in exclude_keys:
                            pattern = r'\{' + re.escape(key) + r'\}'
                            # Use a unique placeholder that won't appear in normal text
                            placeholder = f"__EXCLUDED_KEY_{key}_PLACEHOLDER__"
                            parts[i] = re.sub(pattern, placeholder, parts[i])
                        
                        # Then double all remaining braces
                        parts[i] = parts[i].replace("{", "{{").replace("}", "}}")
                        
                        # Finally, restore the excluded keys
                        for key in exclude_keys:
                            placeholder = f"__EXCLUDED_KEY_{key}_PLACEHOLDER__"
                            parts[i] = parts[i].replace(placeholder, '{' + key + '}')
                    else:
                        # For regular text, use the replacer for simpler patterns
                        parts[i] = re.sub(r'{([^{}]*)}', replacer, parts[i])
                else:  # Inside a code block
                    # Double all curly brackets in code blocks
                    code_block = parts[i]
                    # Split the code block into the opening, content and closing
                    code_match = re.match(r'```(.*?)?\n(.*?)```', code_block, re.DOTALL)
                    if code_match:
                        language = code_match.group(1) or ""
                        content = code_match.group(2)
                        # Double all curly brackets in code blocks
                        content = content.replace("{", "{{").replace("}", "}}").replace("{{}}", "{{}}")
                        parts[i] = f"```{language}\n{content}```"
            
            prompt = "".join(parts)
                
        return prompt  # Preserve whitespaces
    except Exception as e:
        rprint(f"[bold red]Error during prompt processing:[/bold red] {e}")
        return f"Error: {str(e)}"