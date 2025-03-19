#!/usr/bin/env python3
"""
Debug script to understand the behavior of the count_till_limit function.
"""

import sys

from rs_bpe import openai


def main():
    """Test the tokenizer's count_till_limit function."""
    print("Testing count_till_limit behavior:")
    
    tokenizer = openai.cl100k_base()
    sample_text = "Hello, world!"
    
    # Get normal count for reference
    normal_count = tokenizer.count(sample_text)
    tokens = tokenizer.encode(sample_text)
    print(f"Normal count: {normal_count}")
    print(f"Tokens: {tokens}")
    print(f"Number of tokens: {len(tokens)}")
    
    # Test with various limits
    for limit in [1, 2, 3, 4, 5, 10]:
        result = tokenizer.count_till_limit(sample_text, limit)
        print(f"limit={limit}: result={result}")
    
    # More tests with longer text
    longer_text = "This is a longer piece of text that will have more tokens than our simple Hello World example."
    long_count = tokenizer.count(longer_text)
    long_tokens = tokenizer.encode(longer_text)
    print(f"\nLonger text count: {long_count}")
    print(f"Longer text tokens: {long_tokens}")
    print(f"Number of tokens: {len(long_tokens)}")
    
    for limit in [5, 10, 15, 20, long_count, long_count + 1]:
        result = tokenizer.count_till_limit(longer_text, limit)
        print(f"limit={limit}: result={result}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
