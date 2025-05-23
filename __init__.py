"""
ComfyUI Dynamic Random LoRA with Trigger Text Nodes

A comprehensive ComfyUI custom node package offering two approaches for 
random LoRA selection with trigger text generation:

1. Dynamic Slots Approach - Familiar dropdown interface with variable slots
2. Configuration-Based Approach - JSON config for large LoRA collections

Author: [Your Name]
GitHub: https://github.com/yourusername/ComfyUI-Dynamic-Random-LoRA-Trigger
License: MIT
Version: 2.0.0
"""

import os
import sys

# Add the nodes directory to the path
current_dir = os.path.dirname(os.path.realpath(__file__))
nodes_dir = os.path.join(current_dir, "nodes")
if nodes_dir not in sys.path:
    sys.path.append(nodes_dir)

# Initialize mappings
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# Import dynamic nodes (dropdown-style interface)
try:
    from nodes.dynamic_random_lora import NODE_CLASS_MAPPINGS as DYNAMIC_MAPPINGS
    from nodes.dynamic_random_lora import NODE_DISPLAY_NAME_MAPPINGS as DYNAMIC_DISPLAY_MAPPINGS
    NODE_CLASS_MAPPINGS.update(DYNAMIC_MAPPINGS)
    NODE_DISPLAY_NAME_MAPPINGS.update(DYNAMIC_DISPLAY_MAPPINGS)
    print("✅ Dynamic LoRA nodes loaded successfully")
except ImportError as e:
    print(f"⚠️ Could not load dynamic LoRA nodes: {e}")

# Import config-based nodes (JSON configuration)
try:
    from nodes.config_based_lora import NODE_CLASS_MAPPINGS as CONFIG_MAPPINGS
    from nodes.config_based_lora import NODE_DISPLAY_NAME_MAPPINGS as CONFIG_DISPLAY_MAPPINGS
    NODE_CLASS_MAPPINGS.update(CONFIG_MAPPINGS)
    NODE_DISPLAY_NAME_MAPPINGS.update(CONFIG_DISPLAY_MAPPINGS)
    print("✅ Configuration-based LoRA nodes loaded successfully")
except ImportError as e:
    print(f"⚠️ Could not load configuration-based LoRA nodes: {e}")

# Fallback: try loading from current directory (for simple installations)
if not NODE_CLASS_MAPPINGS:
    try:
        from dynamic_random_lora import NODE_CLASS_MAPPINGS as FALLBACK_MAPPINGS
        from dynamic_random_lora import NODE_DISPLAY_NAME_MAPPINGS as FALLBACK_DISPLAY_MAPPINGS
        NODE_CLASS_MAPPINGS.update(FALLBACK_MAPPINGS)
        NODE_DISPLAY_NAME_MAPPINGS.update(FALLBACK_DISPLAY_MAPPINGS)
        print("✅ Fallback node loading successful")
    except ImportError as e:
        print(f"❌ Failed to load any LoRA nodes: {e}")

# Export the mappings
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

# Package metadata
__version__ = "2.0.0"
__author__ = "[Your Name]"
__email__ = "[your.email@example.com]"
__description__ = "Dynamic Random LoRA selection with trigger text for ComfyUI"
__url__ = "https://github.com/yourusername/ComfyUI-Dynamic-Random-LoRA-Trigger"

# Print startup message
print("🎲 Dynamic Random LoRA with Trigger Text Nodes")
print(f"📦 Version {__version__} loaded successfully!")
print(f"🔧 Found {len(NODE_CLASS_MAPPINGS)} custom nodes:")

# List loaded nodes by category
dynamic_nodes = [name for name in NODE_CLASS_MAPPINGS.keys() if "Dynamic" in name or "Simple" in name]
config_nodes = [name for name in NODE_CLASS_MAPPINGS.keys() if "Config" in name or "Random LoRA with Trigger" in name]

if dynamic_nodes:
    print("   📋 Dynamic Slots Nodes:")
    for node in dynamic_nodes:
        print(f"      • {node}")

if config_nodes:
    print("   📁 Configuration-Based Nodes:")
    for node in config_nodes:
        print(f"      • {node}")

print("\n💡 Choose your preferred approach:")
print("   🎯 Dynamic Slots: Familiar dropdown interface")
print("   📚 Config-Based: JSON configuration for large collections")

# Optional: Check for dependencies
def check_dependencies():
    """Check if required dependencies are available"""
    missing = []
    
    try:
        import folder_paths
    except ImportError:
        missing.append("folder_paths (ComfyUI core)")
    
    try:
        import comfy.sd
        import comfy.utils
    except ImportError:
        missing.append("comfy (ComfyUI core)")
    
    if missing:
        print(f"⚠️ Warning: Missing dependencies: {', '.join(missing)}")
        print("Please ensure ComfyUI is properly installed")
    
    return len(missing) == 0

# Run dependency check
check_dependencies()

# Optional: Display helpful tips
def show_usage_tips():
    """Show quick usage tips"""
    if len(NODE_CLASS_MAPPINGS) > 0:
        print("\n🚀 Quick Start Tips:")
        print("   1. Find nodes under: Custom → LoRA or unwdef → lora")
        print("   2. For few LoRAs: Use Dynamic/Simple nodes")
        print("   3. For many LoRAs: Use Config Manager + Random LoRA with Trigger")
        print("   4. Check examples/ folder for sample workflows")

show_usage_tips()