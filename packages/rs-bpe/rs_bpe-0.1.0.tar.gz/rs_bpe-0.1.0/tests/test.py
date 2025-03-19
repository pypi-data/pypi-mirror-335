#!/usr/bin/env python3

# Test direct imports in the style requested
print("Testing direct imports...")
from rs_bpe import BytePairEncoding, openai

# Use the tokenizer
tok = openai.cl100k_base()

# Test encoding
enc = tok.encode("Hello, world!")
print(f"Encoded tokens: {enc}")

# Test counting
cnt = tok.count("Hello, world!")
print(f"Token count: {cnt}")

# Test decoding
dec = tok.decode(enc)
print(f"Decoded text: {dec}")

# Test BPE
bpe = tok.bpe()
print(f"BPE object: {bpe}")
print(f"BPE type: {type(bpe)}")
print(f"Is BytePairEncoding: {isinstance(bpe, BytePairEncoding)}")

# Test convenience imports from package level
print("\nTesting package-level imports...")
try:
    import rs_bpe
    print(f"rs_bpe.__version__: {rs_bpe.__version__}")
    
    # Try using the re-exported openai module
    if hasattr(rs_bpe, 'openai'):
        print("Package has openai attribute")
        tokenizer = rs_bpe.openai.cl100k_base()
        print(f"Tokenizer from package import: {tokenizer}")
        
    # Try using the bpe module
    if hasattr(rs_bpe, 'bpe'):
        print("Package has bpe attribute")
        print(f"bpe module: {rs_bpe.bpe}")
except ImportError as e:
    print(f"Package-level import failed: {e}")

print("\nAll tests completed successfully!")
