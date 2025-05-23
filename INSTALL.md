# Installation Instructions

## Method 1: Git Clone (Recommended)

1. **Navigate to ComfyUI custom nodes directory:**
```bash
cd /path/to/ComfyUI/custom_nodes/
```

2. **Clone this repository:**
```bash
git clone https://github.com/yourusername/comfyui-random-lora-chooser.git
```

3. **Restart ComfyUI**

## Method 2: Manual Download

1. **Download the repository** as a ZIP file from GitHub
2. **Extract** the ZIP file
3. **Copy** the extracted folder to `ComfyUI/custom_nodes/`
4. **Rename** the folder to `comfyui-random-lora-chooser` (remove any version suffixes)
5. **Restart ComfyUI**

## Method 3: ComfyUI Manager (if available)

1. Open ComfyUI Manager
2. Search for "Random LoRA Chooser"
3. Click Install
4. Restart ComfyUI

## Verification

After installation, you can verify everything works:

### Quick Test
1. **Run the test script:**
```bash
cd ComfyUI/custom_nodes/comfyui-random-lora-chooser/
python test_installation.py
```

2. **Check for nodes in ComfyUI:**
   - **Category:** `loaders/lora`
   - **Nodes:** 
     - 🎯 Dynamic Random LoRA Chooser
     - ⚡ Simple Random LoRA Chooser

### Test Dynamic UI
1. **Add a Dynamic Random LoRA Chooser node**
2. **Change `num_loras` parameter** (try values 1, 3, 5, 8)
3. **Watch the UI update in real-time** - input fields should appear/disappear instantly
4. **If it's not dynamic**: The JavaScript extension may not be loaded properly

**Expected Behavior:**
- `num_loras = 1` → Only 1 set of LoRA inputs visible
- `num_loras = 5` → 5 sets of LoRA inputs visible
- Changes happen **instantly** without restarting ComfyUI

## Troubleshooting

### Node doesn't appear in ComfyUI

1. **Check the installation path:**
   ```
   ComfyUI/custom_nodes/comfyui-random-lora-chooser/
   ├── __init__.py
   ├── nodes/
   │   └── random_lora_chooser.py
   └── README.md
   ```

2. **Check ComfyUI console** for any error messages during startup

3. **Verify Python path**: Make sure the `nodes` folder is in the right place

4. **Restart ComfyUI completely** (not just refresh)

### Import errors

If you see import errors, make sure:
- ComfyUI is properly installed
- You're using a compatible Python version (3.8+)
- All ComfyUI dependencies are satisfied

### LoRA files not showing

- Make sure your LoRA files are in the `ComfyUI/models/loras/` directory
- Supported formats: `.safetensors`, `.ckpt`, `.pt`
- Restart ComfyUI after adding new LoRA files

## Uninstalling

To remove the node:
1. Delete the `comfyui-random-lora-chooser` folder from `custom_nodes/`
2. Restart ComfyUI

## Getting Help

If you encounter issues:
1. Check the GitHub Issues page
2. Make sure you're using the latest version
3. Provide error messages and your setup details when reporting issues