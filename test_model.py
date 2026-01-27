#!/usr/bin/env python3
"""
Diagnostic Tool - Test GGUF Model Generation
Tests if the AI model can generate text at all
"""

import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_model():
    """Test if GGUF model generates any text"""
    try:
        from ctransformers import AutoModelForCausalLM
        
        # Find model
        possible_paths = [
            Path('models/tinyllama-1.1b-chat-v1.0.Q8_0.gguf'),
            Path('models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf'),
        ]
        
        model_path = None
        for path in possible_paths:
            if path.exists():
                model_path = path
                break
        
        if not model_path:
            print("\n❌ ERROR: No model found!")
            print("Download model:")
            print("  wget https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q8_0.gguf")
            print("  Move to: models/")
            return
        
        print(f"\n✅ Found model: {model_path}")
        print(f"⏳ Loading model...")
        
        llm = AutoModelForCausalLM.from_pretrained(
            str(model_path),
            model_type='llama',
            context_length=2048,
            max_new_tokens=500,
            threads=4,
            gpu_layers=0
        )
        
        print(f"✅ Model loaded!\n")
        
        # Test 1: Very simple prompt
        print("="*60)
        print("TEST 1: Simple completion")
        print("="*60)
        
        simple_prompt = "The capital of France is"
        print(f"Prompt: '{simple_prompt}'")
        print(f"⏳ Generating...")
        
        result1 = llm(
            simple_prompt,
            max_new_tokens=50,
            temperature=0.1,
            stop=["."],
            stream=False
        )
        
        print(f"Result type: {type(result1)}")
        print(f"Result length: {len(str(result1)) if result1 else 0}")
        print(f"Result: '{result1}'")
        print()
        
        # Test 2: Chat format (how your app uses it)
        print("="*60)
        print("TEST 2: Chat format (like your app)")
        print("="*60)
        
        chat_prompt = """<s>[INST] Write a short 100-word news article about a new smartphone launch.

Title: Apple Launches iPhone 16
Summary: Apple unveiled the iPhone 16 with AI features.

Write the article:[/INST]"""
        
        print(f"⏳ Generating (20 seconds max)...")
        
        result2 = llm(
            chat_prompt,
            max_new_tokens=200,
            temperature=0.7,
            top_p=0.95,
            repetition_penalty=1.1,
            stop=["</s>", "[INST]"],
            stream=False
        )
        
        print(f"\nResult type: {type(result2)}")
        print(f"Result length: {len(str(result2)) if result2 else 0} chars")
        print(f"Word count: {len(str(result2).split()) if result2 else 0} words")
        print(f"\nGenerated text:")
        print("-" * 60)
        print(result2)
        print("-" * 60)
        
        # Verdict
        print("\n" + "="*60)
        print("DIAGNOSTIC RESULTS")
        print("="*60)
        
        if not result1 and not result2:
            print("❌ FAILED: Model generates NO text at all")
            print("   → Model file may be corrupted")
            print("   → Re-download the model")
        elif len(str(result2)) < 50:
            print("⚠️  WARNING: Model generates very little text")
            print(f"   → Only {len(str(result2))} characters")
            print("   → TinyLlama 1.1B is TOO SMALL for complex prompts")
            print("\n🔧 SOLUTION: Use a bigger model:")
            print("   1. Phi-2 (2.7B): https://huggingface.co/TheBloke/phi-2-GGUF")
            print("   2. Mistral-7B (7B): https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF")
        else:
            print("✅ SUCCESS: Model generates text!")
            print(f"   → Generated {len(str(result2).split())} words")
            print("   → Model is working correctly")
            
            if len(str(result2).split()) < 50:
                print("\n⚠️  But text is short. For better results:")
                print("   → Use Phi-2 (2.7B) or Mistral-7B (7B) model")
        
        print()
        
    except ImportError:
        print("\n❌ ERROR: ctransformers not installed")
        print("Install: pip install ctransformers")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("\n" + "="*60)
    print("GGUF MODEL DIAGNOSTIC TEST")
    print("="*60)
    test_model()
