# NextCoder formatter

The filenames have been generated using a [AWQ quantized](https://huggingface.co/cpatonn/Qwen3-Coder-30B-A3B-Instruct-AWQ) version of the Qwen3-Coder-30B-A3B-Instruct model:

```bash
python scripts/get_file_names.py --base-url "http://localhost:8000" --model "cpatonn/Qwen3-Coder-30B-A3B-Instruct-AWQ" --output "data/filenames.jsonl"
```

# Cleaning the data

You can check [this notebook](./notebooks/01_clean_dataset.ipynb) for the cleaning process.
- Some rows contained LLM comments instead of real code
- Some rows had inconsistencies between the language and the code block

> A total of 14484 rows were removed from the dataset.

Final data distribution

|language    |unique count |
|--------------|-------|
|C++           |18667|
|Javascript    |15549|
|Go            |15048|
|Python        |14805|
|Rust          |13925|
|Java          |13522|
|Kotlin        |12733|
|C             |11713|