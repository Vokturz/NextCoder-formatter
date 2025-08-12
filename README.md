# NextCoder formatter

The idea of this repo is to parse the [microsoft/NextCoderDataset](https://huggingface.co/datasets/microsoft/NextCoderDataset) dataset so you can tuples (`instruction`, `whole_code`, `whole_edited_code`).

The filenames have been generated using a [AWQ quantized](https://huggingface.co/cpatonn/Qwen3-Coder-30B-A3B-Instruct-AWQ) version of the Qwen3-Coder-30B-A3B-Instruct model:

```bash
python scripts/get_file_names.py --base-url "http://localhost:8000" --model "cpatonn/Qwen3-Coder-30B-A3B-Instruct-AWQ" --output "data/filenames.jsonl"
```

## Cleaning the data

We make some assumptions and generalizations:
1. To get the filename of each example, the **first** code block from the prompt was considered the whole code.
2. Since we want a 1 to 1 relation per example, we discard all examples that contains more than one code block.

You can check [this notebook](./notebooks/01_clean_dataset.ipynb) for the cleaning process.
- Some rows contained LLM comments instead of real code
- Some rows had inconsistencies between the language and the code block
- Some rows had completions with more than one code block
- Some rows had invalid code blocks. We used tree-sitter to validate them

> A total of 90927 rows were removed from the dataset.

### Final data distribution

|language    |unique count |
|--------------|-------|
|C++           |14326|
|Python        |13773|
|Javascript    |13299|
|Rust          |12661|
|Java          |11837|
|Go            |11106|
|Kotlin        |10437|
|C             | 9630|

- **Total Unique Code Blocks**: 97069
- **Total Examples**: 297376

## Columns

```
language: (str) - Programming language of the code block.
code_block: (str) - The code block content.
file_path: (str) - Generated file path for the code block.
system_prompt: (str) - System prompt used for generation.
instruction: (str) - Instructions for code modification.
completion_code_block: (str) - Final generated code block.
```