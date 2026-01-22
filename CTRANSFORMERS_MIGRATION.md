# CTransformers Migration Guide

## Overview

This project has been migrated from `llama-cpp-python` to `ctransformers>=0.2.27` for GGUF model support. CTransformers provides pure Python bindings for GGUF models with better compatibility and easier installation.

## What Changed

### 1. Dependencies (requirements.txt)

**Before:**
```python
llama-cpp-python>=0.2.27
```

**After:**
```python
ctransformers>=0.2.27
```

### 2. AI Draft Generator (core/ai_draft_generator.py)

**Before (llama-cpp-python):**
```python
from llama_cpp import Llama

llm = Llama(
    model_path=str(model_path),
    n_ctx=4096,
    n_threads=4,
    n_gpu_layers=0,
    verbose=False
)

output = self.llm(
    prompt,
    max_tokens=512,
    temperature=0.7,
    top_p=0.9,
    stop=["</s>", "[/INST]"],
    echo=False
)
generated_text = output['choices'][0]['text']
```

**After (ctransformers):**
```python
from ctransformers import AutoModelForCausalLM

llm = AutoModelForCausalLM.from_pretrained(
    str(model_path),
    model_type='mistral',
    context_length=4096,
    threads=4,
    gpu_layers=0
)

generated_text = self.llm(
    prompt,
    max_new_tokens=512,
    temperature=0.7,
    top_p=0.9,
    stop=["</s>", "[/INST]"],
    stream=False
)
```

## Key Differences

| Feature | llama-cpp-python | ctransformers |
|---------|------------------|---------------|
| Import | `from llama_cpp import Llama` | `from ctransformers import AutoModelForCausalLM` |
| Model Loading | `Llama(model_path=...)` | `AutoModelForCausalLM.from_pretrained(...)` |
| Context Window | `n_ctx` | `context_length` |
| CPU Threads | `n_threads` | `threads` |
| GPU Layers | `n_gpu_layers` | `gpu_layers` |
| Max Tokens | `max_tokens` | `max_new_tokens` |
| Echo Param | `echo` | Not needed |
| Output Format | `output['choices'][0]['text']` | Direct string return |
| Stream Support | Limited | `stream=True/False` |

## Installation

### Clean Install

```bash
# Remove old llama-cpp-python (if installed)
pip uninstall llama-cpp-python -y

# Install ctransformers
pip install ctransformers>=0.2.27

# Or install all dependencies
pip install -r requirements.txt
```

### GPU Support (Optional)

For CUDA GPU acceleration:

```bash
pip install ctransformers[cuda]
```

For Apple Metal (M1/M2/M3):

```bash
CT_METAL=1 pip install ctransformers --no-binary ctransformers
```

## Advantages of CTransformers

### 1. **Easier Installation**
- Pure Python package
- No C++ compiler required
- Pre-built wheels for most platforms
- Faster pip installation

### 2. **Better Compatibility**
- Works on Python 3.8-3.12+
- Cross-platform (Windows, Linux, macOS)
- No build system issues
- ARM and x86 support

### 3. **Enhanced Performance**
- Optimized C bindings
- Lower memory footprint
- Faster inference on CPU
- Better thread management

### 4. **More Features**
- Auto model type detection
- Built-in tokenizer
- Stream generation support
- Better error handling

### 5. **HuggingFace Integration**
- Compatible with HF model hub
- Auto-download support
- Standard model naming

## Supported Model Types

CTransformers supports various GGUF model architectures:

- **Mistral** (what we use)
- LLaMA / LLaMA 2
- Falcon
- MPT
- StarCoder
- GPT-2
- GPT-J
- GPT-NeoX
- And more...

## Usage Examples

### Basic Text Generation

```python
from ctransformers import AutoModelForCausalLM

# Load model
llm = AutoModelForCausalLM.from_pretrained(
    'models/TheBloke_Mistral-7B-Instruct-v0.2-GGUF/mistral-7b-instruct-v0.2.Q4_K_M.gguf',
    model_type='mistral'
)

# Generate
text = llm('Write a news article about AI:', max_new_tokens=256)
print(text)
```

### Streaming Generation

```python
# Stream tokens as they're generated
for token in llm('Write a story:', stream=True, max_new_tokens=100):
    print(token, end='', flush=True)
```

### Advanced Configuration

```python
llm = AutoModelForCausalLM.from_pretrained(
    'model.gguf',
    model_type='mistral',
    context_length=4096,      # Context window
    threads=8,                 # CPU threads
    gpu_layers=50,             # GPU layers (0 for CPU only)
    temperature=0.7,           # Default temperature
    top_p=0.9,                 # Default top-p
    top_k=40,                  # Default top-k
    repetition_penalty=1.1,    # Prevent repetition
    batch_size=512,            # Batch size
    reset=True                 # Reset context between calls
)
```

## Configuration Parameters

### Model Loading

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_path` | str | Required | Path to .gguf file |
| `model_type` | str | Required | Model architecture (mistral, llama, etc) |
| `context_length` | int | 512 | Maximum context window |
| `threads` | int | Auto | Number of CPU threads |
| `gpu_layers` | int | 0 | Number of layers on GPU |
| `batch_size` | int | 512 | Batch size for processing |
| `reset` | bool | True | Reset context between calls |

### Text Generation

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_new_tokens` | int | 256 | Maximum tokens to generate |
| `temperature` | float | 0.8 | Sampling temperature (0.0-2.0) |
| `top_p` | float | 0.95 | Nucleus sampling threshold |
| `top_k` | int | 40 | Top-k sampling |
| `repetition_penalty` | float | 1.1 | Penalty for repeating tokens |
| `stop` | List[str] | None | Stop sequences |
| `stream` | bool | False | Stream output token by token |

## Troubleshooting

### Installation Issues

**Problem:** `pip install ctransformers` fails

**Solution:**
```bash
# Try upgrading pip first
pip install --upgrade pip setuptools wheel

# Then install ctransformers
pip install ctransformers>=0.2.27
```

### Model Loading Errors

**Problem:** "Model type not recognized"

**Solution:** Explicitly specify model type:
```python
llm = AutoModelForCausalLM.from_pretrained(
    'model.gguf',
    model_type='mistral'  # Always specify this
)
```

### Memory Issues

**Problem:** Out of memory when loading model

**Solution:**
```python
# Reduce context length
llm = AutoModelForCausalLM.from_pretrained(
    'model.gguf',
    model_type='mistral',
    context_length=2048  # Reduce from 4096
)

# Or use GPU layers
llm = AutoModelForCausalLM.from_pretrained(
    'model.gguf',
    model_type='mistral',
    gpu_layers=32  # Offload to GPU
)
```

### Slow Generation

**Problem:** Text generation is slow

**Solution:**
```python
# Increase CPU threads
llm = AutoModelForCausalLM.from_pretrained(
    'model.gguf',
    model_type='mistral',
    threads=8  # Use more CPU cores
)

# Or enable GPU
llm = AutoModelForCausalLM.from_pretrained(
    'model.gguf',
    model_type='mistral',
    gpu_layers=50  # Use GPU acceleration
)
```

## Performance Tips

### CPU Optimization

1. **Set optimal thread count:**
   ```python
   import os
   threads = os.cpu_count() - 1  # Leave one core free
   ```

2. **Adjust batch size:**
   ```python
   llm = AutoModelForCausalLM.from_pretrained(
       'model.gguf',
       model_type='mistral',
       batch_size=1024  # Larger = faster but more RAM
   )
   ```

3. **Use appropriate quantization:**
   - Q4_K_M: Best balance (4.1GB)
   - Q5_K_M: Better quality (5GB)
   - Q2_K: Smallest (2.5GB)

### GPU Optimization

1. **Find optimal GPU layers:**
   ```python
   # Start with 0, increase gradually
   for layers in [0, 16, 32, 50]:
       llm = AutoModelForCausalLM.from_pretrained(
           'model.gguf',
           model_type='mistral',
           gpu_layers=layers
       )
       # Test speed
   ```

2. **Monitor VRAM usage:**
   - 4GB VRAM: gpu_layers=10-15
   - 8GB VRAM: gpu_layers=25-32
   - 12GB+ VRAM: gpu_layers=50+

## Migration Checklist

- [x] Updated requirements.txt
- [x] Updated core/ai_draft_generator.py
- [x] Changed import statements
- [x] Updated model loading code
- [x] Changed generation parameters
- [x] Updated output parsing
- [x] Tested with Mistral-7B GGUF
- [x] Verified CPU inference
- [x] Added documentation

## Testing

### Test Model Loading

```python
from ctransformers import AutoModelForCausalLM
from pathlib import Path

model_path = Path('models/TheBloke_Mistral-7B-Instruct-v0.2-GGUF/mistral-7b-instruct-v0.2.Q4_K_M.gguf')

if model_path.exists():
    llm = AutoModelForCausalLM.from_pretrained(
        str(model_path),
        model_type='mistral'
    )
    print("✓ Model loaded successfully")
    
    # Test generation
    output = llm("Hello, world!", max_new_tokens=50)
    print(f"✓ Generation works: {output}")
else:
    print(f"✗ Model not found at {model_path}")
```

### Test Draft Generation

```python
from core.ai_draft_generator import DraftGenerator

db_path = 'nexuzy.db'
generator = DraftGenerator(db_path)

# Test template mode
draft = generator._template_draft(
    "Test Headline",
    "Test summary",
    [('fact', 'Test fact')]
)
print("✓ Template generation works")

# Test with model (if loaded)
if generator.llm:
    print("✓ GGUF model loaded and ready")
else:
    print("⚠ Model not loaded, using template mode")
```

## References

- [CTransformers GitHub](https://github.com/marella/ctransformers)
- [CTransformers Documentation](https://github.com/marella/ctransformers#documentation)
- [GGUF Format Specification](https://github.com/ggerganov/ggml/blob/master/docs/gguf.md)
- [Model Type Reference](https://github.com/marella/ctransformers#supported-models)

## Support

If you encounter issues:

1. Check this migration guide
2. Verify ctransformers version: `pip show ctransformers`
3. Review model path and type
4. Check available RAM/VRAM
5. Test with simple example first
6. Open issue on GitHub with error details

## Version History

- **v1.0.0** - Initial release with llama-cpp-python
- **v1.1.0** - Migrated to ctransformers (current)

---

**Note:** All existing GGUF model files are compatible with ctransformers. You don't need to re-download models, just update the code!
