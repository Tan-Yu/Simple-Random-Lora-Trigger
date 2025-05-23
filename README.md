# ComfyUI Random LoRA with Trigger Text Nodes

A ComfyUI custom node package that enables random LoRA selection with associated trigger text generation. Perfect for dynamic prompt enhancement and automated LoRA workflows.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![ComfyUI](https://img.shields.io/badge/ComfyUI-Compatible-green.svg)

## 🌟 Features

- **Random LoRA Selection**: Dynamically choose 1-10 LoRAs from your collection
- **Trigger Text Integration**: Automatically concatenate associated trigger texts
- **ComfyRoll Compatibility**: Full compatibility with ComfyRoll's LoRA stack system
- **Easy Configuration**: UI-based LoRA configuration with the Config Manager node
- **Advanced Controls**: Stride system, seed control, and force randomization
- **Flexible Weights**: Individual model/clip weights per LoRA

## 🚀 Quick Start

### Installation

#### Method 1: Git Clone (Recommended)
```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/yourusername/ComfyUI-Random-LoRA-Trigger.git
```

#### Method 2: Manual Download
1. Download the repository as ZIP
2. Extract to `ComfyUI/custom_nodes/ComfyUI-Random-LoRA-Trigger/`

#### Method 3: ComfyUI Manager
```
Install via ComfyUI Manager: Search for "Random LoRA Trigger"
```

### Post-Installation
1. Restart ComfyUI
2. Find nodes under: **Custom → LoRA**

## 📋 Nodes Included

### 1. Random LoRA with Trigger
Randomly selects LoRAs and outputs their concatenated trigger texts.

**Inputs:**
- `num_loras_to_select`: Number of LoRAs to randomly choose (1-10)
- `exclusive_mode`: Ensure different selections each generation
- `stride`: Generations before re-randomizing
- `seed`: Random seed for reproducible results
- `lora_stack`: Optional input LoRA stack

**Outputs:**
- `LORA_STACK`: Compatible with ComfyRoll's LoRA system
- `trigger_text`: Concatenated trigger texts
- `show_help`: Status and selection information

### 2. LoRA Config Manager
Easy configuration interface for setting up LoRAs and their trigger texts.

**Inputs:**
- `lora_name`: Select from available LoRAs
- `trigger_text`: Associated prompt text
- `model_weight`/`clip_weight`: LoRA strength settings
- `enabled`: Enable/disable LoRA for selection
- `action`: Update or remove configuration

## 🎯 Basic Usage

### Step 1: Configure Your LoRAs
1. Add a **LoRA Config Manager** node
2. Select a LoRA from the dropdown
3. Enter the trigger text (e.g., "anime style, cel shading")
4. Set weights and enable status
5. Click "Update Config"
6. Repeat for all your LoRAs

### Step 2: Use Random Selection
1. Add **Random LoRA with Trigger** node
2. Set `num_loras_to_select` (how many to choose)
3. Configure other parameters as needed
4. Connect outputs to your workflow

### Step 3: Connect to Workflow
```
[Random LoRA with Trigger] → [Apply LoRA Stack] → [Model]
          ↓
[trigger_text] → [Text Concatenation] → [CLIP Text Encode]
```

## 📁 Configuration File

The nodes automatically create `lora_trigger_config.json`:

```json
{
    "anime_style_v1.safetensors": {
        "trigger_text": "anime style, cel shading",
        "model_weight": 1.0,
        "clip_weight": 1.0,
        "enabled": true
    },
    "photorealistic_v2.safetensors": {
        "trigger_text": "photorealistic, detailed skin texture",
        "model_weight": 0.8,
        "clip_weight": 0.8,
        "enabled": true
    }
}
```

## 🔧 Advanced Features

### Stride System
Prevents re-randomization on every generation:
- `stride = 1`: Randomize every generation
- `stride = 5`: Randomize every 5 generations

### Force Randomization
Ensures different selections when `stride` expires and multiple options are available.

### Seed Control
Use the same seed for reproducible LoRA selections across sessions.

## 🤝 Compatibility

- **ComfyUI**: Latest version
- **ComfyRoll Custom Nodes**: Full compatibility with LoRA stack system
- **Python**: 3.8+

## 📸 Examples

See the `examples/` folder for:
- Sample workflow JSON files
- Configuration examples
- Screenshots of node interfaces

## 🐛 Troubleshooting

### Nodes Don't Appear
- Check directory structure: `custom_nodes/ComfyUI-Random-LoRA-Trigger/`
- Restart ComfyUI completely
- Check console for error messages

### No LoRAs Available
- Use LoRA Config Manager to add LoRAs
- Verify LoRA files exist in `models/loras/`
- Check LoRAs are enabled in configuration

### Empty Trigger Text
- Configure trigger texts using LoRA Config Manager
- Verify `lora_trigger_config.json` exists and has correct format

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- ComfyUI team for the amazing framework
- ComfyRoll developers for LoRA stack inspiration
- Community feedback and contributions

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/ComfyUI-Random-LoRA-Trigger/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ComfyUI-Random-LoRA-Trigger/discussions)

---

⭐ **If this project helps you, please give it a star!** ⭐