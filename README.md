# NextCoder formatter

The filenames have been generated using a [AWQ quantized](https://huggingface.co/cpatonn/Qwen3-Coder-30B-A3B-Instruct-AWQ) version of the Qwen3-Coder-30B-A3B-Instruct model:

```bash
python scripts/get_file_names.py --base-url "http://localhost:8000" --model "cpatonn/Qwen3-Coder-30B-A3B-Instruct-AWQ" --output "data/filenames.jsonl"
```

## Cleaning the data

You can check [this notebook](./notebooks/01_clean_dataset.ipynb) for the cleaning process.
- Some rows contained LLM comments instead of real code
- Some rows had inconsistencies between the language and the code block
- Some rows had completions with more than one code block
- Some rows had invalid code blocks. We used tree-sitter to validate them

> A total of 67038 rows were removed from the dataset.

### Final data distribution

|language    |unique count |
|--------------|-------|
|C++           |14621|
|Python        |13969|
|Javascript    |13541|
|Rust          |13010|
|Java          |12129|
|Go            |11269|
|Kotlin        |10738|
|C             | 9711|

- **Total Unique Code Blocks**: 98998
- **Total Examples**: 314085

## Columns

```
language: (str) - Programming language of the code block.
code_block: (str) - The code block content.
file_path: (str) - Generated file path for the code block.
system_prompt: (str) - System prompt used for generation.
instruction: (str) - Instructions for code modification.
completion_code_block: (str) - Final generated code block.
```