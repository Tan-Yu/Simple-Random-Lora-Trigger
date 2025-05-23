#!/usr/bin/env python3
"""
Installation helper for ComfyUI Random LoRA with Trigger Text Nodes

This script helps verify the installation and sets up the initial configuration.
"""

import os
import sys
import json
import shutil
from pathlib import Path

def find_comfyui_path():
    """Try to find ComfyUI installation path"""
    current_path = Path(__file__).parent.absolute()
    
    # Check if we're already in custom_nodes
    if "custom_nodes" in str(current_path):
        # Navigate up to find ComfyUI root
        parts = current_path.parts
        try:
            custom_nodes_index = parts.index("custom_nodes")
            comfyui_path = Path(*parts[:custom_nodes_index])
            return comfyui_path
        except ValueError:
            pass
    
    # Common installation locations
    possible_paths = [
        current_path.parent.parent,  # If in custom_nodes/this_repo/
        Path.home() / "ComfyUI",
        Path("/opt/ComfyUI"),
        Path("C:/ComfyUI") if os.name == 'nt' else None,
    ]
    
    for path in possible_paths:
        if path and path.exists() and (path / "main.py").exists():
            return path
    
    return None

def check_installation():
    """Check if the installation is correct"""
    print("🔍 Checking installation...")
    
    current_path = Path(__file__).parent.absolute()
    
    # Check required files
    required_files = [
        "__init__.py",
        "nodes/random_lora_trigger.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not (current_path / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files found")
    return True

def create_example_config():
    """Create example configuration file"""
    config_path = Path(__file__).parent / "lora_trigger_config.json"
    
    if config_path.exists():
        print("📁 Configuration file already exists")
        return
    
    example_config = {
        "example_lora_1.safetensors": {
            "trigger_text": "example trigger 1, artistic style",
            "model_weight": 1.0,
            "clip_weight": 1.0,
            "enabled": True
        },
        "example_lora_2.safetensors": {
            "trigger_text": "example trigger 2, photorealistic",
            "model_weight": 0.8,
            "clip_weight": 0.8,
            "enabled": True
        }
    }
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(example_config, f, indent=4, ensure_ascii=False)
        print("✅ Created example configuration file")
    except Exception as e:
        print(f"❌ Failed to create configuration file: {e}")

def verify_comfyui_integration():
    """Verify integration with ComfyUI"""
    comfyui_path = find_comfyui_path()
    
    if not comfyui_path:
        print("⚠️ Could not automatically detect ComfyUI installation")
        print("Please ensure you've placed this in ComfyUI/custom_nodes/")
        return False
    
    print(f"✅ Found ComfyUI at: {comfyui_path}")
    
    # Check if we're in the right location
    current_path = Path(__file__).parent.absolute()
    expected_path = comfyui_path / "custom_nodes"
    
    if not str(current_path).startswith(str(expected_path)):
        print(f"⚠️ This should be installed in: {expected_path}")
        print(f"Current location: {current_path}")
        return False
    
    print("✅ Correct installation location")
    return True

def main():
    """Main installation verification"""
    print("🎲 ComfyUI Random LoRA with Trigger Text Nodes")
    print("🔧 Installation Verification")
    print("=" * 50)
    
    # Check basic installation
    if not check_installation():
        print("\n❌ Installation check failed!")
        sys.exit(1)
    
    # Verify ComfyUI integration
    verify_comfyui_integration()
    
    # Create example config
    create_example_config()
    
    print("\n" + "=" * 50)
    print("✅ Installation verification complete!")
    print("\nNext steps:")
    print("1. Restart ComfyUI")
    print("2. Look for nodes under 'Custom → LoRA'")
    print("3. Use 'LoRA Config Manager' to set up your LoRAs")
    print("4. Use 'Random LoRA with Trigger' in your workflows")
    print("\n📚 For more help, see: README.md")

if __name__ == "__main__":
    main()