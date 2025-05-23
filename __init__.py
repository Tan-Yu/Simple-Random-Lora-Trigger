"""
ComfyUI Random LoRA with Trigger Text Nodes

A ComfyUI custom node package that enables random LoRA selection with 
associated trigger text generation. Perfect for dynamic prompt enhancement 
and automated LoRA workflows.

Author: [Your Name]
GitHub: https://github.com/yourusername/ComfyUI-Random-LoRA-Trigger
License: MIT
Version: 1.0.0
"""

import os
import sys

# Add the nodes directory to the path
current_dir = os.path.dirname(os.path.realpath(__file__))
nodes_dir = os.path.join(current_dir, "nodes")
if nodes_dir not in sys.path:
    sys.path.append(nodes_dir)

# Import from nodes directory
try:
    from nodes.random_lora_trigger import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
except ImportError:
    # Fallback to current directory import for simpler installations
    try:
        from random_lora_trigger import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
    except ImportError as e:
        print(f"Error importing Random LoRA Trigger nodes: {e}")
        NODE_CLASS_MAPPINGS = {}
        NODE_DISPLAY_NAME_MAPPINGS = {}

# Export the mappings
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

# Package metadata
__version__ = "1.0.0"
__author__ = "[Your Name]"
__email__ = "[your.email@example.com]"
__description__ = "Random LoRA selection with trigger text for ComfyUI"
__url__ = "https://github.com/yourusername/ComfyUI-Random-LoRA-Trigger"

# Print startup message
print(f"🎲 Random LoRA with Trigger Text Nodes v{__version__} loaded successfully!")
print(f"📁 Found {len(NODE_CLASS_MAPPINGS)} custom nodes")

# Optional: Check for dependencies
def check_dependencies():
    """Check if required dependencies are available"""
    missing = []
    
    try:
        import folder_paths
    except ImportError:
        missing.append("folder_paths (ComfyUI core)")
    
    if missing:
        print(f"⚠️ Warning: Missing dependencies: {', '.join(missing)}")
        print("Please ensure ComfyUI is properly installed")
    
    return len(missing) == 0

# Run dependency check
check_dependencies()