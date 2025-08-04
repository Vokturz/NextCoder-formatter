import re
import difflib
from typing import List, Tuple
from .file_path_prompt import file_path_prompt


def parse_prompt(prompt: str) -> dict:
    """
    Parse a prompt to extract the initial part, instruction, and code block.
    
    Args:
        prompt (str): The input prompt string
        
    Returns:
        dict: Dictionary containing 'initial_part', 'instruction', 'code_block', and 'language'
    """
    # Extract initial part (everything up to "following instruction.")
    initial_match = re.search(r'^(.*?following instruction\.)', prompt, re.DOTALL)
    initial_part = initial_match.group(1).strip() if initial_match else ""
    
    # Extract instruction (from after "following instruction." to before code block)
    instruction_pattern = r'following instruction\.(.*?)```'
    instruction_match = re.search(instruction_pattern, prompt, re.DOTALL)
    instruction = instruction_match.group(1).strip() if instruction_match else ""
    
    # Extract code block and language (everything between ``` markers)
    code_pattern = r'```(\w+)?\n(.*?)```'
    code_match = re.search(code_pattern, prompt, re.DOTALL)
    language = code_match.group(1) if code_match and code_match.group(1) else ""
    code_block = code_match.group(2).strip() if code_match else ""
    
    return {
        'initial_part': initial_part,
        'instruction': instruction,
        'code_block': code_block,
        'language': language
    }



def get_code_edit_patches(code_block: str, edited_block: str) -> List[Tuple[str, str]]:
    """
    Generates patches that transform code_block into edited_block.

    This function identifies changes and creates patches containing the
    original and edited code sections. If changes are close enough to share
    context, they are automatically merged into a single patch.

    Args:
        code_block (str): The original string of code.
        edited_block (str): The edited string of code.

    Returns:
        A list of tuples. Each tuple represents a patch and contains:
        (original_section: str, edited_section: str)
    """
    # Split code into lines, preserving line endings for accurate reconstruction
    original_lines = code_block.splitlines(keepends=True)
    edited_lines = edited_block.splitlines(keepends=True)

    # difflib will automatically merge nearby changes into a single hunk.
    diff_generator = difflib.unified_diff(
        original_lines,
        edited_lines,
        fromfile='original',
        tofile='edited',
        n=3,
    )

    patches = []
    current_original_hunk = []
    current_edited_hunk = []

    # Iterate over the diff, skipping the initial file headers
    for line in diff_generator:
        if line.startswith('---') or line.startswith('+++'):
            continue

        if line.startswith('@@'):
            # This '@@' line indicates the start of a new hunk (a new patch).
            # If we have content from a previous hunk, save it as a patch.
            if current_original_hunk or current_edited_hunk:
                original_patch = "".join(current_original_hunk)
                edited_patch = "".join(current_edited_hunk)
                patches.append((original_patch, edited_patch))
            
            # Reset for the new hunk
            current_original_hunk = []
            current_edited_hunk = []
        elif line.startswith('-'):
            # This line was removed, add it to the original hunk section.
            current_original_hunk.append(line[1:])
        elif line.startswith('+'):
            # This line was added, add it to the edited hunk section.
            current_edited_hunk.append(line[1:])
        elif line.startswith(' '):
            # This is a context line, present in both versions. Add to both.
            content = line[1:]
            current_original_hunk.append(content)
            current_edited_hunk.append(content)

    # After the loop, there might be a final hunk that hasn't been saved yet.
    if current_original_hunk or current_edited_hunk:
        original_patch = "".join(current_original_hunk)
        edited_patch = "".join(current_edited_hunk)
        patches.append((original_patch, edited_patch))

    return patches
    

import requests
import json

def get_file_path(code_block: str, language: str,  model="qwen/qwen3-coder-30b", temperature=0.7, max_tokens=-1, stream=False, base_url="http://localhost:1234", api_key="no-key"):
    url = f"{base_url}/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    messages = [
        {"role": "system", "content": file_path_prompt},
        {"role": "user", "content": f"<language>\n{language}\n</language>\n<code>\n{code_block}\n</code>"}
    ]
    
    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": stream
    }
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    
    resp = response.json()
    assistant_message = resp['choices'][0]['message']['content']

    file_path = next(re.finditer(r"<file_path>\n(.*?)\n</file_path>", assistant_message, re.DOTALL)).group(1)
    
    return file_path.strip()