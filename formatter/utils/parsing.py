import re
import requests
import difflib
from typing import List, Tuple,  Dict, Any, Set, Optional
from .file_path_prompt import system_prompt, few_shot_examples
import json
import os
import concurrent.futures

def parse_code_block(md_code_block: str) -> List[str]:
    # Extract code block and language (everything between ``` markers)
    code_pattern = r'```(\w+)?\n(.*?)```'
    code_match = re.search(code_pattern, md_code_block, re.DOTALL)
    language = code_match.group(1) if code_match and code_match.group(1) else ""
    code_block = code_match.group(2).strip() if code_match else ""
    
    return {
        'code_block': code_block,
        'language': language
    }

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
    
    parsed_code_block = parse_code_block(prompt)
    code_block = parsed_code_block['code_block']
    language = parsed_code_block['language']
    
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
    
def get_file_path(code_block: str, language: str,  model="qwen/qwen3-coder-30b", temperature=0.7, stream=False,
    base_url="http://localhost:8000", api_key="no-key", print_assistant_message=False):
    url = f"{base_url}/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    messages = [
        {"role": "system", "content": system_prompt},
        *few_shot_examples,
        {"role": "user", "content": f"```{language}\n{code_block}\n```"}
    ]
    
    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "stream": stream
    }
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    
    resp = response.json()
    assistant_message = resp['choices'][0]['message']['content']

    if print_assistant_message:
        print(assistant_message)

    file_path = next(re.finditer(r"<file_path>(.*?)</file_path>", assistant_message, re.DOTALL)).group(1)
    
    return file_path.strip()

def get_file_paths_parallel(
    code_blocks: List[Tuple[str, str, int]], 
    model="qwen/qwen3-coder-30b", 
    temperature=0.7, 
    stream=False,
    base_url="http://localhost:8000",
    api_key="no-key", 
    print_assistant_message=False,
    max_workers=5
) -> List[Optional[str]]:
    """
    Process multiple code blocks in parallel to get file paths.
    
    Args:
        code_blocks: List of tuples (code_block, language, id)
        max_workers: Maximum number of parallel workers
        Other args: Same as original get_file_path function
    
    Returns:
        List of file paths corresponding to each code block
    """
    
    def process_single_block(code_block_data):
        code_block, language, i = code_block_data
        try:
            return (i, get_file_path(
                code_block=code_block,
                language=language,
                model=model,
                temperature=temperature,
                stream=stream,
                base_url=base_url,
                api_key=api_key,
                print_assistant_message=print_assistant_message
            ))
        except Exception as e:
            print(f"Error processing code id={i} block: {e}")
            return None
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_index = {
            executor.submit(process_single_block, code_block_data): i 
            for i, code_block_data in enumerate(code_blocks)
        }
        
        # Initialize results list with None values
        results = [None] * len(code_blocks)
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_index):
            index = future_to_index[future]
            try:
                results[index] = future.result()
            except Exception as e:
                print(f"Error in future {index}: {e}")
                results[index] = None
    
    return results

def load_existing_ids(jsonl_path: str) -> Set[str]:
    existing_ids = set()
    if os.path.exists(jsonl_path):
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    if 'id' in data:
                        existing_ids.add(data['id'])
                except json.JSONDecodeError:
                    continue
    return existing_ids

def process_dataset_to_jsonl(dataset, output_path: str, model="qwen/qwen3-coder-30b", base_url: str = "http://localhost:8000"):
    """
    Process the entire dataset and generate JSONL file with file paths using parallel processing.
    Skips entries where id already exists in the output file.
    
    Args:
        dataset: The dataset containing prompts
        output_path: Path to the output JSONL file
        base_url: Base URL for file path generation
    """
    # Load existing file paths to avoid duplicates
    existing_ids = load_existing_ids(output_path)
    print(f"Found {len(existing_ids)} existing file ids in {output_path}")
    
    processed_count = 0
    skipped_count = 0
    error_count = 0
    batch_size = 16  # Process in batches for better memory management
    
    # Open file in append mode
    with open(output_path, 'a', encoding='utf-8') as f:
        for batch_start in range(0, len(dataset), batch_size):
            batch_end = min(batch_start + batch_size, len(dataset))
            batch_data = []
            
            # Prepare batch of data
            for i in range(batch_start, batch_end):
                if i in existing_ids:
                    skipped_count += 1
                    continue
                    
                try:
                    parsed = parse_prompt(dataset['prompt'][i])
                    batch_data.append((parsed['code_block'], parsed['language'], i))
                except Exception as e:
                    error_count += 1
                    print(f"Error parsing entry {i}: {str(e)}")
                    continue
            
            if not batch_data:
                continue
                
            # Process batch in parallel
            results = get_file_paths_parallel(
                batch_data,
                base_url=base_url,
                model=model,
                max_workers=8
            )
            
            # Write results
            for result in results:
                if result is not None:
                    i, file_path = result
                    entry = {
                        "id": i,
                        "file_path": file_path
                    }
                    f.write(json.dumps(entry) + '\n')
                    f.flush()  # Ensure data is written immediately
                    processed_count += 1
                else:
                    error_count += 1
            
            # Progress indicator
            print(f"Processed {batch_end}/{len(dataset)} entries. Added: {processed_count}, Skipped: {skipped_count}, Errors: {error_count}")
    
    print(f"\nProcessing complete!")
    print(f"Total entries processed: {len(dataset)}")
    print(f"New entries added: {processed_count}")
    print(f"Entries skipped (duplicates): {skipped_count}")
    print(f"Errors encountered: {error_count}")
