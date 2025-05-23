import os
import sys
import json
import random
import hashlib
import folder_paths
from typing import List, Tuple, Dict, Any

# Custom node class for random LoRA selection with trigger text
class RandomLoRAWithTrigger:
    """
    A custom ComfyUI node that randomly selects LoRAs and their associated trigger texts.
    Compatible with ComfyRoll's LoRA stack system.
    """
    
    def __init__(self):
        self.lora_config_file = os.path.join(os.path.dirname(__file__), "lora_trigger_config.json")
        self.load_lora_config()
    
    @classmethod
    def INPUT_TYPES(cls):
        loras = ["None"] + folder_paths.get_filename_list("loras")
        
        return {
            "required": {
                "num_loras_to_select": ("INT", {"default": 1, "min": 1, "max": 10, "step": 1}),
                "exclusive_mode": (["Off", "On"],),
                "stride": ("INT", {"default": 1, "min": 1, "max": 1000}),
                "force_randomize_after_stride": (["Off", "On"],),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "lora_stack": ("LORA_STACK",),
            }
        }
    
    RETURN_TYPES = ("LORA_STACK", "STRING", "STRING")
    RETURN_NAMES = ("LORA_STACK", "trigger_text", "show_help")
    FUNCTION = "random_lora_with_trigger"
    CATEGORY = "Custom/LoRA"
    
    # Class variables for stride management
    StridesMap = {}
    LastHashMap = {}
    LastSelectionMap = {}
    
    def load_lora_config(self):
        """Load LoRA configuration from JSON file"""
        if os.path.exists(self.lora_config_file):
            try:
                with open(self.lora_config_file, 'r', encoding='utf-8') as f:
                    self.lora_config = json.load(f)
            except Exception as e:
                print(f"Error loading LoRA config: {e}")
                self.lora_config = {}
        else:
            self.lora_config = {}
            self.create_default_config()
    
    def create_default_config(self):
        """Create a default configuration file with example LoRAs"""
        default_config = {
            "example_lora_1.safetensors": {
                "trigger_text": "example trigger 1",
                "model_weight": 1.0,
                "clip_weight": 1.0,
                "enabled": True
            },
            "example_lora_2.safetensors": {
                "trigger_text": "example trigger 2",
                "model_weight": 0.8,
                "clip_weight": 0.8,
                "enabled": True
            }
        }
        
        try:
            with open(self.lora_config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
            print(f"Created default LoRA config at: {self.lora_config_file}")
            print("Please edit this file to add your LoRAs and their trigger texts.")
            self.lora_config = default_config
        except Exception as e:
            print(f"Error creating default config: {e}")
            self.lora_config = {}
    
    def get_available_loras(self) -> List[str]:
        """Get list of available LoRAs from the configuration that are enabled"""
        available_loras = []
        loras_folder = folder_paths.get_filename_list("loras")
        
        for lora_name in loras_folder:
            if lora_name in self.lora_config and self.lora_config[lora_name].get("enabled", True):
                available_loras.append(lora_name)
        
        return available_loras
    
    def get_id_hash(self, num_loras: int, available_loras: List[str], seed: int) -> str:
        """Generate a unique hash for the current configuration"""
        lora_str = "_".join(sorted(available_loras))
        hash_string = f"{num_loras}_{lora_str}_{seed}"
        return hashlib.sha256(hash_string.encode('utf-8')).hexdigest()
    
    @classmethod
    def IS_CHANGED(cls, num_loras_to_select, exclusive_mode, stride, force_randomize_after_stride, seed, lora_stack=None):
        """ComfyUI method to determine if the node should be re-executed"""
        # Create a simple hash based on parameters
        param_str = f"{num_loras_to_select}_{exclusive_mode}_{stride}_{force_randomize_after_stride}_{seed}"
        id_hash = hashlib.sha256(param_str.encode('utf-8')).hexdigest()
        
        if id_hash not in cls.StridesMap:
            cls.StridesMap[id_hash] = 0
        
        cls.StridesMap[id_hash] += 1
        
        # Handle stride logic
        if stride > 1 and cls.StridesMap[id_hash] < stride and id_hash in cls.LastHashMap:
            return cls.LastHashMap[id_hash]
        else:
            cls.StridesMap[id_hash] = 0
        
        # Generate new hash with current timestamp for randomization
        import time
        current_hash = f"{id_hash}_{time.time()}_{random.random()}"
        cls.LastHashMap[id_hash] = current_hash
        
        return current_hash
    
    def select_random_loras(self, num_loras: int, available_loras: List[str], seed: int, force_randomize: bool, id_hash: str) -> List[str]:
        """Select random LoRAs from available list"""
        if not available_loras:
            return []
        
        # Set random seed for reproducibility
        random.seed(seed)
        
        # Get last selection if exists
        last_selection = self.LastSelectionMap.get(id_hash, [])
        
        # Select random LoRAs
        num_to_select = min(num_loras, len(available_loras))
        selected_loras = random.sample(available_loras, num_to_select)
        
        # Force different selection if requested and possible
        if force_randomize and last_selection and len(available_loras) > num_to_select:
            attempts = 0
            while selected_loras == last_selection and attempts < 10:
                selected_loras = random.sample(available_loras, num_to_select)
                attempts += 1
        
        # Store current selection
        self.LastSelectionMap[id_hash] = selected_loras
        
        return selected_loras
    
    def random_lora_with_trigger(self, num_loras_to_select, exclusive_mode, stride, force_randomize_after_stride, seed, lora_stack=None):
        """Main function to execute random LoRA selection with trigger text"""
        
        # Reload config in case it was updated
        self.load_lora_config()
        
        # Get available LoRAs
        available_loras = self.get_available_loras()
        
        if not available_loras:
            show_help = "No enabled LoRAs found in configuration. Please check lora_trigger_config.json"
            return ([], "", show_help)
        
        # Generate ID hash for stride management
        id_hash = self.get_id_hash(num_loras_to_select, available_loras, seed)
        
        # Select random LoRAs
        selected_loras = self.select_random_loras(
            num_loras_to_select, 
            available_loras, 
            seed, 
            force_randomize_after_stride == "On",
            id_hash
        )
        
        # Initialize LoRA list
        lora_list = []
        if lora_stack is not None:
            lora_list.extend([l for l in lora_stack if l[0] != "None"])
        
        # Build trigger text
        trigger_texts = []
        
        # Process selected LoRAs
        for lora_name in selected_loras:
            if lora_name in self.lora_config:
                config = self.lora_config[lora_name]
                model_weight = config.get("model_weight", 1.0)
                clip_weight = config.get("clip_weight", 1.0)
                trigger_text = config.get("trigger_text", "")
                
                # Add to LoRA stack
                lora_list.append((lora_name, model_weight, clip_weight))
                
                # Add trigger text if it exists
                if trigger_text.strip():
                    trigger_texts.append(trigger_text.strip())
        
        # Combine trigger texts
        combined_trigger_text = ", ".join(trigger_texts)
        
        show_help = f"Selected {len(selected_loras)} LoRA(s): {', '.join(selected_loras)}"
        
        return (lora_list, combined_trigger_text, show_help)


# Configuration manager node for easier LoRA setup
class LoRAConfigManager:
    """
    A helper node to manage LoRA configurations more easily through the UI
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "lora_name": (folder_paths.get_filename_list("loras"),),
                "trigger_text": ("STRING", {"multiline": True, "default": ""}),
                "model_weight": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                "clip_weight": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                "enabled": (["True", "False"],),
                "action": (["Update Config", "Remove from Config"],),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)
    FUNCTION = "manage_config"
    CATEGORY = "Custom/LoRA"
    
    def manage_config(self, lora_name, trigger_text, model_weight, clip_weight, enabled, action):
        """Manage LoRA configuration"""
        config_file = os.path.join(os.path.dirname(__file__), "lora_trigger_config.json")
        
        # Load existing config
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except:
                config = {}
        else:
            config = {}
        
        if action == "Update Config":
            config[lora_name] = {
                "trigger_text": trigger_text,
                "model_weight": model_weight,
                "clip_weight": clip_weight,
                "enabled": enabled == "True"
            }
            status = f"Updated configuration for {lora_name}"
        elif action == "Remove from Config":
            if lora_name in config:
                del config[lora_name]
                status = f"Removed {lora_name} from configuration"
            else:
                status = f"{lora_name} not found in configuration"
        
        # Save config
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            status = f"Error saving config: {e}"
        
        return (status,)


# Node mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "Random LoRA with Trigger": RandomLoRAWithTrigger,
    "LoRA Config Manager": LoRAConfigManager,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Random LoRA with Trigger": "Random LoRA with Trigger Text",
    "LoRA Config Manager": "LoRA Configuration Manager",
}