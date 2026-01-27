import re

def fix_lambda_closures(filename):
    """Fix all lambda closure issues in a file"""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern: lambda: func(str(e)) -> lambda err=str(e): func(err)
    pattern = r'lambda:\s+self\.(\w+)\(str\(e\)\)'
    replacement = r'lambda err=str(e): self.\1(err)'
    fixed_content = re.sub(pattern, replacement, content)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"✅ Fixed lambda closures in {filename}")

def fix_translator_warnings():
    """Fix translation generation warnings"""
    filename = 'core/translator.py'
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the generate call
    old_code = """translated_tokens = self.translator.generate(
            **inputs,
            forced_bos_token_id=self.tokenizer.convert_tokens_to_ids(target_code),
            max_length=512,
            temperature=0.7,
            top_p=0.9
        )"""
    
    new_code = """translated_tokens = self.translator.generate(
            **inputs,
            forced_bos_token_id=self.tokenizer.convert_tokens_to_ids(target_code),
            max_length=512,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            num_beams=1
        )"""
    
    fixed_content = content.replace(old_code, new_code)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"✅ Fixed translation warnings in {filename}")

# Run fixes
print("Applying fixes...")
fix_lambda_closures('main.py')
fix_translator_warnings()
print("✅ All fixes applied!")
