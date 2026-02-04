#!/usr/bin/env python3
"""
Debug script to test Research Writer functionality
Run: python test_research.py
"""

import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("="*60)
print("🔬 RESEARCH WRITER DEBUG TEST")
print("="*60)

# Test 1: Import
print("\n[TEST 1] Importing ResearchWriter...")
try:
    from core.research_writer import ResearchWriter
    print("✅ Import successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Initialize
print("\n[TEST 2] Initializing ResearchWriter...")
try:
    research = ResearchWriter(
        db_path='nexuzy.db',
        cache_articles=True,
        model_name='models/mistral-7b-instruct-v0.2.Q4_K_M.gguf'
    )
    print("✅ Initialization successful")
except Exception as e:
    print(f"❌ Initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Check .model attribute
print("\n[TEST 3] Checking .model attribute...")
try:
    model = research.model
    print(f"✅ .model attribute exists: {model}")
except AttributeError as e:
    print(f"❌ .model attribute missing: {e}")
    print("\n🔍 Available attributes:")
    for attr in dir(research):
        if not attr.startswith('_'):
            print(f"  - {attr}")
    sys.exit(1)

# Test 4: Check .llm attribute
print("\n[TEST 4] Checking .llm attribute...")
try:
    llm = research.llm
    print(f"✅ .llm attribute exists: {llm}")
except AttributeError as e:
    print(f"❌ .llm attribute missing: {e}")
    sys.exit(1)

# Test 5: Simple research test (without internet)
print("\n[TEST 5] Testing research_and_generate (no internet)...")
try:
    result = research.research_and_generate(
        topic="Python Programming",
        source_urls=["https://www.python.org"],
        word_count=500,
        use_internet=False
    )
    
    if result.get('success'):
        print(f"✅ Research successful!")
        print(f"   - Word count: {result.get('word_count')}")
        print(f"   - Sources used: {result.get('sources_used')}")
        print(f"   - Quality score: {result.get('quality_score')}")
    else:
        print(f"⚠️ Research completed with error: {result.get('error')}")
        
except Exception as e:
    print(f"❌ Research test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("🎯 DIAGNOSIS COMPLETE")
print("="*60)
print("\nIf all tests passed, Research Writer is working correctly.")
print("If any test failed, check the error messages above.")
print("\nCommon fixes:")
print("1. Run: git pull origin main")
print("2. Restart your application")
print("3. Check if models/ directory exists with GGUF models")
print("="*60)
