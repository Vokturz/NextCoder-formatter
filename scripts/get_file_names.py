#!/usr/bin/env python3
"""
Script to process NextCoderDataset and convert to JSONL format.
"""

import argparse
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datasets import load_dataset
from formatter.utils.parsing import process_dataset_to_jsonl


def main():
    parser = argparse.ArgumentParser(
        description="Process NextCoderDataset and convert to JSONL format"
    )
    
    parser.add_argument(
        "--base-url",
        required=True,
        help="Base URL for the API endpoint"
    )
    
    parser.add_argument(
        "--model",
        required=True,
        help="Model name to use for processing"
    )
    
    parser.add_argument(
        "--output",
        required=True,
        help="Output JSONL file name"
    )
    
    parser.add_argument(
        "--num-samples",
        type=int,
        default=-1,
        help="Number of samples to process (default: 240)"
    )
    
    parser.add_argument(
        "--split",
        default="train",
        help="Dataset split to use (default: train)"
    )
    
    args = parser.parse_args()
    
    print(f"Loading dataset split: {args.split}")
    dataset = load_dataset("microsoft/NextCoderDataset", split=args.split)
    
    print(f"Processing {args.num_samples} samples...")

    subset = dataset.select(range(args.num_samples)) if args.num_samples > 0 else dataset
    process_dataset_to_jsonl(
        subset,
        args.output,
        base_url=args.base_url,
        model=args.model
    )
    
    print(f"Processing complete. Output saved to: {args.output}")


if __name__ == "__main__":
    main()
