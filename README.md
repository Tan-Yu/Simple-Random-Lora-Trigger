# ComfyUI Random LoRA Chooser

A dynamic LoRA selection system for ComfyUI that randomly chooses from configured LoRAs with trigger word support. Features a dynamic UI that shows only the number of slots you need, just like EasyUse nodes.

## Features

- **Dynamic UI**: Shows only the number of LoRA slots you specify (1-10 slots)
- **Random Selection**: Multiple selection modes (random, weighted, all configured)
- **Trigger Words**: Automatically outputs combined trigger words from selected LoRAs
- **Auto Population**: Can automatically fill slots with random LoRAs
- **Reproducible**: Seed-based selection for consistent results
- **Stack Integration**: Works with existing LoRA stacks

## Installation

1. Clone or download this repository to your ComfyUI custom nodes directory:
```bash
cd ComfyUI/custom_nodes/
git clone <this-repo-url> comfyui-random-lora-chooser
```

2. Restart ComfyUI

3. The nodes will appear under `loaders/lora` category

## Nodes

### 🎯 Dynamic Random LoRA Chooser

The full-featured node with comprehensive options:

**Key Parameters:**
- `num_loras`: Number of LoRA slots to show (1-10)
- `selection_mode`: How to choose LoRAs
  - `random`: Random selection from configured slots
  - `weighted`: Weighted selection based on weight values
  - `all_configured`: Use all configured LoRAs
- `min_random`/`max_random`: Range of how many LoRAs to select
- `auto_populate`: Automatically fill empty slots with random LoRAs

**Per-LoRA Settings:**
- `lora_X_name`: LoRA file ("None", "Auto", or specific LoRA)
- `lora_X_min_strength`/`lora_X_max_strength`: Strength range for random selection
- `lora_X_weight`: Weight for weighted selection mode
- `lora_X_trigger_words`: Comma-separated trigger words

**Outputs:**
- `lora_stack`: LoRA stack compatible with other nodes
- `trigger_words`: Combined trigger words from selected LoRAs
- `chosen_loras_info`: List of selected LoRAs with strengths
- `debug_info`: Selection information

### ⚡ Simple Random LoRA Chooser

Simplified version with essential features only:

**Key Parameters:**
- `num_loras`: Number of LoRA slots (1-8)
- `min_select`/`max_select`: How many LoRAs to randomly select
- `min_strength`/`max_strength`: Global strength range
- `auto_fill`: Auto-populate empty slots

**Per-LoRA Settings:**
- `lora_X`: LoRA file selection
- `triggers_X`: Trigger words for this LoRA

## How the Dynamic UI Works

**🔥 NOW WITH TRUE DYNAMIC UI LIKE EASYUSE! 🔥**

This implementation uses the same technique as EasyUse to create a truly dynamic interface:

1. **Backend**: The node defines all possible slots (1-10) in Python
2. **Frontend**: JavaScript extension dynamically shows/hides inputs based on `num_loras`
3. **Smart processing**: The node only processes the visible/active slots

**Dynamic Behavior:**
- Set `num_loras = 3` → **Only see 3 LoRA input groups in the UI**
- Set `num_loras = 7` → **UI expands to show 7 LoRA input groups**
- Change `num_loras` → **UI instantly updates without restart**

**Technical Implementation:**
- **Frontend JavaScript** (`web/js/dynamic_lora_chooser.js`) handles UI visibility
- **Backend Python** processes only the first `num_loras` slots
- **Real-time updates** when you change the `num_loras` parameter
- **Identical behavior** to EasyUse's dynamic LoRA stack

## Usage Examples

### Basic Random Selection

1. Set `num_loras = 4` to show 4 LoRA slots
2. Configure 2-3 LoRAs in the visible slots
3. Set `selection_mode = "random"`
4. Set `min_random = 1`, `max_random = 2`
5. Add trigger words to each LoRA

Result: Randomly selects 1-2 LoRAs from your configured options

### Auto Population

1. Set `num_loras = 5`
2. Enable `auto_populate = "Random Fill"`
3. Set strength ranges
4. Leave LoRA slots empty or set to "Auto"

Result: Automatically fills slots with random LoRAs from your collection

### Weighted Selection

1. Configure multiple LoRAs with different weights
2. Set `selection_mode = "weighted"`
3. LoRAs with higher weights are more likely to be selected

### Integration with Workflows

Connect the outputs to your loader:

```
Random LoRA Chooser → EasyLoader
├── lora_stack → optional_lora_stack
├── trigger_words → Add to positive prompt
└── chosen_loras_info → For logging/debugging
```

## Tips

- **Reproducible Results**: Use the same seed value for consistent LoRA selection
- **Trigger Words**: Use descriptive trigger words for each LoRA to improve generation quality
- **Strength Ranges**: Set realistic strength ranges (0.5-1.0 is usually good)
- **Testing**: Use debug_info output to see what was selected
- **Performance**: Start with fewer slots and expand as needed

## Project Structure

```
comfyui-random-lora-chooser/
├── __init__.py                     # Package initialization
├── README.md                       # This file
├── pyproject.toml                  # Project configuration
├── nodes/
│   └── random_lora_chooser.py     # Main node implementation
└── web/                           # Future: Custom frontend assets
```

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this node.

## License

MIT License - Feel free to use and modify as needed.

## Changelog

### v1.0.0
- Initial release
- Dynamic UI implementation
- Random selection with multiple modes
- Trigger word support
- Auto population feature
- Integration with LoRA stacks