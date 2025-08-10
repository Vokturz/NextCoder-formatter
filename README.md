# NextCoder formatter

The filenames have been generated using a [AWQ quantized](https://huggingface.co/cpatonn/Qwen3-Coder-30B-A3B-Instruct-AWQ) version of the Qwen3-Coder-30B-A3B-Instruct model:

```bash
python scripts/get_file_names.py --base-url "http://localhost:8000" --model "cpatonn/Qwen3-Coder-30B-A3B-Instruct-AWQ" --output "data/filenames.jsonl"
```

# Cleaning the data

You can check [this notebook](./notebooks/01_clean_dataset.ipynb) for the cleaning process.
- Some rows contained LLM comments instead of real code
- Some rows had inconsistencies between the language and the code block
- (NEW) Some rows had completions with more than one code block

> A total of ~14484~ 27005 rows were removed from the dataset.

Final data distribution

|language    |unique count |
|--------------|-------|
|C++           |17415|
|Javascript    |14753|
|Python        |14738|
|Go            |14359|
|Rust          |13552|
|Java          |13433|
|Kotlin        |12388|
|C             |11345|