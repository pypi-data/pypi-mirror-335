#!/usr/bin/env python3

print("=== Testing Import Patterns ===")

# Test 1: Import the bpe module directly
try:
    print("\nTest 1: from rs_bpe import bpe")
    from rs_bpe import bpe
    print(f"✅ Success! bpe module imported: {bpe}")
    print(f"bpe module attributes: {dir(bpe)}")
except ImportError as e:
    print(f"❌ Failed: {e}")

# Test 2: Import from bpe.openai
try:
    print("\nTest 2: from rs_bpe.bpe import openai")
    from rs_bpe.bpe import openai
    print(f"✅ Success! openai module imported: {openai}")
    print(f"openai attributes: {dir(openai)}")
except ImportError as e:
    print(f"❌ Failed: {e}")

# Test 3: Import openai directly from package
try:
    print("\nTest 3: from rs_bpe import openai")
    from rs_bpe import openai
    print(f"✅ Success! openai module imported: {openai}")
    print(f"openai attributes: {dir(openai)}")
except ImportError as e:
    print(f"❌ Failed: {e}")

# Test 4: Import BytePairEncoding
try:
    print("\nTest 4: from rs_bpe import BytePairEncoding")
    from rs_bpe import BytePairEncoding
    print(f"✅ Success! BytePairEncoding imported: {BytePairEncoding}")
except ImportError as e:
    print(f"❌ Failed: {e}")

# Test 5: Full package usage
try:
    print("\nTest 5: Full package usage")
    import rs_bpe
    tokenizer = rs_bpe.openai.cl100k_base()
    tokens = tokenizer.encode("Hello, world!")
    bpe_obj = tokenizer.bpe()
    
    print("✅ Success! Full package usage works")
    print(f"  - Tokens: {tokens}")
    print(f"  - BPE object: {bpe_obj}")
    print(f"  - rs_bpe.__all__: {rs_bpe.__all__}")  # type: ignore
except (ImportError, AttributeError) as e:
    print(f"❌ Failed: {e}")

print("\n=== Test Complete ===")
