import random
import folder_paths
import comfy.sd
import comfy.utils

import random
import folder_paths
import comfy.sd
import comfy.utils
from typing import Dict, Any, List, Tuple


class DynamicRandomLoraStack:
    """
    Fully dynamic LoRA stack with no fixed slot limitations.
    Creates input slots dynamically based on available LoRAs and user configuration.
    """
    
    def __init__(self):
        self._cached_loras = None
        self._last_lora_count = 0

    @classmethod  
    def INPUT_TYPES(cls):
        # Get all available LoRAs
        loras = ["None"] + folder_paths.get_filename_list("loras")
        
        # Base required inputs
        inputs = {
            "required": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "max_slots": ("INT", {"default": len(loras), "min": 1, "max": len(loras)}),
                "min_random": ("INT", {"default": 1, "min": 1, "max": len(loras)}),
                "max_random": ("INT", {"default": 3, "min": 1, "max": len(loras)}),
                "auto_populate": (["Disabled", "Enabled"], {"default": "Disabled"}),
                "refresh_slots": (["No", "Yes"], {"default": "No"}),
            }
        }
        
        # Create dynamic slots based on max_slots or all available LoRAs
        # We'll create slots for all available LoRAs to be fully dynamic
        for i, lora in enumerate(loras[1:], 1):  # Skip "None" and start from 1
            inputs["required"][f"lora_{i}"] = (["None", "Auto"] + loras[1:], {"default": "Auto" if i <= 5 else "None"})
            inputs["required"][f"min_str_{i}"] = ("FLOAT", {"default": 0.5, "min": -10.0, "max": 10.0, "step": 0.01})
            inputs["required"][f"max_str_{i}"] = ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01})
            inputs["required"][f"trigger_words_{i}"] = ("STRING", {"multiline": False, "default": ""})

        inputs["optional"] = {
            "lora_stack": ("LORA_STACK",)
        }

        return inputs

    RETURN_TYPES = ("LORA_STACK", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("LORA_STACK", "trigger_words", "chosen_loras", "debug_info")
    FUNCTION = "load_lora_stack"
    CATEGORY = "unwdef/lora"

    def get_available_loras(self) -> List[str]:
        """Get list of available LoRAs, cached for performance"""
        current_loras = folder_paths.get_filename_list("loras")
        if self._cached_loras is None or len(current_loras) != self._last_lora_count:
            self._cached_loras = current_loras
            self._last_lora_count = len(current_loras)
        return self._cached_loras

    def auto_populate_loras(self, available_loras: List[str], max_slots: int) -> Dict[str, Any]:
        """Auto-populate LoRA configurations when auto_populate is enabled"""
        auto_config = {}
        
        # Randomly select LoRAs for auto-population
        selected_loras = random.sample(available_loras, min(max_slots, len(available_loras)))
        
        for i, lora in enumerate(selected_loras, 1):
            auto_config[f"lora_{i}"] = lora
            # Set random strength ranges
            base_min = random.uniform(0.3, 0.7)
            base_max = random.uniform(base_min + 0.1, 1.5)
            auto_config[f"min_str_{i}"] = base_min
            auto_config[f"max_str_{i}"] = base_max
            auto_config[f"trigger_words_{i}"] = ""  # Leave empty for user to fill
            
        return auto_config

    def load_lora_stack(self, seed, max_slots, min_random, max_random, auto_populate, refresh_slots, lora_stack=None, **kwargs):
        if seed is not None:
            random.seed(seed)

        available_loras = self.get_available_loras()
        
        # Debug information
        debug_info = f"Available LoRAs: {len(available_loras)}, Max slots: {max_slots}"
        
        # Auto-populate if enabled
        if auto_populate == "Enabled":
            auto_config = self.auto_populate_loras(available_loras, max_slots)
            # Merge auto config with user input, prioritizing user input
            for key, value in auto_config.items():
                if key not in kwargs or kwargs.get(key) in ["None", "Auto", ""]:
                    kwargs[key] = value

        # Initialize list to hold lora configurations
        lora_configs = []

        # Initialize lora stack list
        lora_list = list()
        if lora_stack is not None:
            lora_list.extend([l for l in lora_stack if l[0] != "None"])

        # Process all potential slots dynamically
        processed_loras = set()  # Track processed LoRAs to avoid duplicates
        
        # First pass: collect all explicitly configured LoRAs
        for i in range(1, len(available_loras) + 1):
            lora_name = kwargs.get(f"lora_{i}")
            min_str = kwargs.get(f"min_str_{i}", 0.5)
            max_str = kwargs.get(f"max_str_{i}", 1.0)
            trigger_words = kwargs.get(f"trigger_words_{i}", "")

            if lora_name and lora_name not in ["None", "Auto"] and lora_name not in processed_loras:
                if lora_name in available_loras:  # Ensure LoRA actually exists
                    processed_trigger_words = ', '.join([s.strip() for s in trigger_words.strip().split(',') if s.strip()]) if trigger_words else ""
                    lora_configs.append({
                        "name": lora_name,
                        "min_str": float(min_str),
                        "max_str": float(max_str),
                        "trigger_words": processed_trigger_words,
                        "slot": i
                    })
                    processed_loras.add(lora_name)

        # Second pass: handle "Auto" selections from remaining LoRAs
        remaining_loras = [lora for lora in available_loras if lora not in processed_loras]
        auto_slots = []
        
        for i in range(1, len(available_loras) + 1):
            lora_name = kwargs.get(f"lora_{i}")
            if lora_name == "Auto" and remaining_loras:
                auto_slots.append(i)
        
        # Fill auto slots with random LoRAs from remaining pool
        if auto_slots and remaining_loras:
            auto_loras = random.sample(remaining_loras, min(len(auto_slots), len(remaining_loras)))
            for slot_idx, auto_lora in zip(auto_slots, auto_loras):
                min_str = kwargs.get(f"min_str_{slot_idx}", 0.5)
                max_str = kwargs.get(f"max_str_{slot_idx}", 1.0)
                trigger_words = kwargs.get(f"trigger_words_{slot_idx}", "")
                
                processed_trigger_words = ', '.join([s.strip() for s in trigger_words.strip().split(',') if s.strip()]) if trigger_words else ""
                lora_configs.append({
                    "name": auto_lora,
                    "min_str": float(min_str),
                    "max_str": float(max_str),
                    "trigger_words": processed_trigger_words,
                    "slot": slot_idx
                })

        # Limit configurations to max_slots
        if len(lora_configs) > max_slots:
            lora_configs = lora_configs[:max_slots]

        # Initialize return strings
        chosen_str = ""
        debug_info += f", Configured LoRAs: {len(lora_configs)}"

        # Check if no loras are selected
        if len(lora_configs) == 0:
            return (lora_list, "", chosen_str, debug_info + " - No LoRAs configured")

        # Cap min_random and max_random to length of lora configs
        min_random = min(min_random, len(lora_configs))
        max_random = min(max_random, len(lora_configs))
        max_random = max(min_random, max_random)

        # Randomly choose some of these loras
        num_to_choose = random.randint(min_random, max_random)
        chosen_loras = random.sample(lora_configs, num_to_choose)

        # Track all trigger words
        all_trigger_words = set()
        chosen_lora_names = []

        for lora in chosen_loras:
            # Randomly determine a value between min_str and max_str
            strength = random.uniform(lora['min_str'], lora['max_str'])

            # Add to the stack
            lora_list.append((lora['name'], strength, strength))

            # Track chosen LoRA names
            chosen_lora_names.append(f"{lora['name']}:{strength:.2f}")

            # Append the current lora and its value to the string
            chosen_str += f"<lora:{lora['name'].split('.')[0]}:{strength:.2f}>, "

            # Collect trigger words
            if lora['trigger_words']:
                trigger_word_list = [word.strip() for word in lora['trigger_words'].split(',') if word.strip()]
                all_trigger_words.update(trigger_word_list)

        # Combine all trigger words
        chosen_trigger_words = ', '.join(sorted(all_trigger_words))

        # Remove the last comma from chosen_str
        chosen_str = chosen_str.rstrip(', ')
        
        # Update debug info
        debug_info += f", Chosen: {len(chosen_loras)} ({', '.join(chosen_lora_names)})"

        return (lora_list, chosen_trigger_words, chosen_str, debug_info)


class UltraDynamicLoraStack:
    """
    Ultra-dynamic version that creates slots on-the-fly based on JSON configuration
    Similar to the config-based approach but with dynamic slot generation
    """
    
    def __init__(self):
        self.config_file = "dynamic_lora_config.json"
        self.load_config()

    def load_config(self):
        """Load or create configuration file"""
        import json
        import os
        
        config_path = os.path.join(os.path.dirname(__file__), self.config_file)
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except:
                self.config = {}
        else:
            # Create default config with all available LoRAs
            self.config = {}
            available_loras = folder_paths.get_filename_list("loras")
            for lora in available_loras[:10]:  # Limit to first 10 as example
                self.config[lora] = {
                    "enabled": False,
                    "min_strength": 0.5,
                    "max_strength": 1.0,
                    "trigger_words": "",
                    "weight": 1.0  # For selection probability
                }
            self.save_config()

    def save_config(self):
        """Save configuration to file"""
        import json
        import os
        
        try:
            config_path = os.path.join(os.path.dirname(__file__), self.config_file)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "min_random": ("INT", {"default": 1, "min": 1, "max": 50}),
                "max_random": ("INT", {"default": 3, "min": 1, "max": 50}),
                "reload_config": (["No", "Yes"], {"default": "No"}),
                "selection_mode": (["Random", "Weighted", "Sequential"], {"default": "Random"}),
            },
            "optional": {
                "lora_stack": ("LORA_STACK",)
            }
        }

    RETURN_TYPES = ("LORA_STACK", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("LORA_STACK", "trigger_words", "chosen_loras", "config_status")
    FUNCTION = "process_dynamic_loras"
    CATEGORY = "unwdef/lora"

    def process_dynamic_loras(self, seed, min_random, max_random, reload_config, selection_mode, lora_stack=None):
        if reload_config == "Yes":
            self.load_config()
        
        if seed is not None:
            random.seed(seed)

        # Get enabled LoRAs from config
        enabled_loras = {name: config for name, config in self.config.items() 
                        if config.get("enabled", False)}

        # Initialize lora stack
        lora_list = list()
        if lora_stack is not None:
            lora_list.extend([l for l in lora_stack if l[0] != "None"])

        if not enabled_loras:
            return (lora_list, "", "", f"No enabled LoRAs in config. Edit {self.config_file}")

        # Select LoRAs based on mode
        available_names = list(enabled_loras.keys())
        num_to_select = random.randint(min_random, min(max_random, len(available_names)))

        if selection_mode == "Weighted":
            # Weighted selection based on weight values
            weights = [enabled_loras[name].get("weight", 1.0) for name in available_names]
            selected_names = random.choices(available_names, weights=weights, k=num_to_select)
            # Remove duplicates while preserving order
            selected_names = list(dict.fromkeys(selected_names))
        elif selection_mode == "Sequential":
            # Sequential selection (useful for deterministic results)
            selected_names = available_names[:num_to_select]
        else:  # Random
            selected_names = random.sample(available_names, num_to_select)

        # Process selected LoRAs
        all_trigger_words = set()
        chosen_info = []

        for lora_name in selected_names:
            config = enabled_loras[lora_name]
            min_str = config.get("min_strength", 0.5)
            max_str = config.get("max_strength", 1.0)
            strength = random.uniform(min_str, max_str)

            # Add to stack
            lora_list.append((lora_name, strength, strength))
            chosen_info.append(f"{lora_name}:{strength:.2f}")

            # Collect trigger words
            trigger_words = config.get("trigger_words", "")
            if trigger_words:
                words = [w.strip() for w in trigger_words.split(',') if w.strip()]
                all_trigger_words.update(words)

        # Combine results
        combined_trigger_words = ', '.join(sorted(all_trigger_words))
        chosen_str = ', '.join([f"<lora:{name.split('.')[0]}:{info.split(':')[1]}>" 
                               for name, info in zip(selected_names, chosen_info)])
        
        config_status = f"Processed {len(selected_names)} of {len(enabled_loras)} enabled LoRAs"

        return (lora_list, combined_trigger_words, chosen_str, config_status)


class SimpleRandomLoraStack:
    """
    Simplified version that works more like your original but with variable slots
    This one should definitely work in ComfyUI
    """
    
    def __init__(self):
        pass

    @classmethod  
    def INPUT_TYPES(cls):
        loras = ["None"] + folder_paths.get_filename_list("loras")
        
        # Create inputs for maximum slots, but we'll only use what's needed
        inputs = {
            "required": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "active_slots": ("INT", {"default": 5, "min": 1, "max": 15}),
                "min_random": ("INT", {"default": 1, "min": 1, "max": 15}),
                "max_random": ("INT", {"default": 3, "min": 1, "max": 15}),
            }
        }
        
        # Always create 15 slots, but only the first 'active_slots' will be used
        for i in range(1, 16):  # Create 15 slots maximum
            inputs["required"][f"lora_{i}"] = (loras,)
            inputs["required"][f"min_str_{i}"] = ("FLOAT", {"default": 0.5, "min": -10.0, "max": 10.0, "step": 0.01})
            inputs["required"][f"max_str_{i}"] = ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01})
            inputs["required"][f"trigger_words_{i}"] = ("STRING", {"multiline": False, "default": ""})

        inputs["optional"] = {
            "lora_stack": ("LORA_STACK",)
        }

        return inputs

    RETURN_TYPES = ("LORA_STACK", "STRING", "STRING")
    RETURN_NAMES = ("LORA_STACK", "trigger_words", "chosen_loras")
    FUNCTION = "load_lora_stack"
    CATEGORY = "unwdef/lora"

    def load_lora_stack(self, seed, active_slots, min_random, max_random, lora_stack=None, **kwargs):
        if seed is not None:
            random.seed(seed)

        # Initialize list to hold lora configurations
        lora_configs = []

        # Initialize lora stack list
        lora_list = list()
        if lora_stack is not None:
            lora_list.extend([l for l in lora_stack if l[0] != "None"])

        # Only process the active slots
        for i in range(1, active_slots + 1):
            lora_name = kwargs.get(f"lora_{i}")
            min_str = kwargs.get(f"min_str_{i}")
            max_str = kwargs.get(f"max_str_{i}")
            trigger_words = kwargs.get(f"trigger_words_{i}")

            if lora_name and lora_name != "None" and not any(config['name'] == lora_name for config in lora_configs):
                processed_trigger_words = ', '.join([s.strip() for s in trigger_words.strip().split(',') if s.strip()]) if trigger_words else ""
                lora_configs.append({
                    "name": lora_name,
                    "min_str": min_str,
                    "max_str": max_str,
                    "trigger_words": processed_trigger_words
                })

        # Initialize return strings
        chosen_str = ""

        # Check if no loras are selected
        if len(lora_configs) == 0:
            return (lora_list, "", chosen_str)

        # Cap min_random and max_random to length of lora configs and active_slots
        min_random = min(min_random, len(lora_configs), active_slots)
        max_random = min(max_random, len(lora_configs), active_slots)
        max_random = max(min_random, max_random)

        # Randomly choose some of these loras
        chosen_loras = random.sample(lora_configs, random.randint(min_random, max_random))

        # Track all trigger words
        all_trigger_words = set()

        for lora in chosen_loras:
            # Randomly determine a value between min_str and max_str
            strength = random.uniform(lora['min_str'], lora['max_str'])

            # Add to the stack
            lora_list.append((lora['name'], strength, strength))

            # Append the current lora and its value to the string
            chosen_str += f"<lora:{lora['name'].split('.')[0]}:{strength:.2f}>, "

            # Collect trigger words
            if lora['trigger_words']:
                trigger_word_list = [word.strip() for word in lora['trigger_words'].split(',') if word.strip()]
                all_trigger_words.update(trigger_word_list)

        # Combine all trigger words
        chosen_trigger_words = ', '.join(sorted(all_trigger_words))

        # Remove the last comma from chosen_str
        chosen_str = chosen_str.rstrip(', ')

        return (lora_list, chosen_trigger_words, chosen_str)

import random
import folder_paths
import comfy.sd
import comfy.utils
from typing import Dict, Any, List, Tuple


class DynamicRandomLoraStack:
    """
    Truly dynamic LoRA stack that shows/hides slots based on max_slots parameter.
    Uses JavaScript frontend to achieve the same behavior as EasyUse LoRA Stack.
    """
    
    def __init__(self):
        pass

    @classmethod  
    def INPUT_TYPES(cls):
        loras = ["None"] + folder_paths.get_filename_list("loras")
        
        # Create a generous maximum number of slots that will be controlled by frontend
        MAX_POSSIBLE_SLOTS = 50  # Increased to handle large collections
        
        inputs = {
            "required": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "max_slots": ("INT", {"default": 5, "min": 1, "max": MAX_POSSIBLE_SLOTS}),
                "min_random": ("INT", {"default": 1, "min": 1, "max": MAX_POSSIBLE_SLOTS}),
                "max_random": ("INT", {"default": 3, "min": 1, "max": MAX_POSSIBLE_SLOTS}),
                "auto_populate": (["Disabled", "Enabled"], {"default": "Disabled"}),
            }
        }
        
        # Create ALL possible slots - frontend JavaScript will control visibility
        for i in range(1, MAX_POSSIBLE_SLOTS + 1):
            inputs["required"][f"lora_{i}"] = (["None", "Auto"] + loras[1:], {"default": "Auto" if i <= 5 else "None"})
            inputs["required"][f"min_str_{i}"] = ("FLOAT", {"default": 0.5, "min": -10.0, "max": 10.0, "step": 0.01})
            inputs["required"][f"max_str_{i}"] = ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01})
            inputs["required"][f"trigger_words_{i}"] = ("STRING", {"multiline": False, "default": ""})

        inputs["optional"] = {
            "lora_stack": ("LORA_STACK",)
        }

        return inputs

    RETURN_TYPES = ("LORA_STACK", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("LORA_STACK", "trigger_words", "chosen_loras", "debug_info")
    FUNCTION = "load_lora_stack"
    CATEGORY = "unwdef/lora"

    def load_lora_stack(self, seed, max_slots, min_random, max_random, auto_populate, lora_stack=None, **kwargs):
        if seed is not None:
            random.seed(seed)

        available_loras = folder_paths.get_filename_list("loras")
        
        # Debug information
        debug_info = f"Processing {max_slots} slots from {len(available_loras)} available LoRAs"
        
        # Initialize list to hold lora configurations
        lora_configs = []

        # Initialize lora stack list
        lora_list = list()
        if lora_stack is not None:
            lora_list.extend([l for l in lora_stack if l[0] != "None"])

        # Auto-populate if enabled - only for the active slots
        if auto_populate == "Enabled":
            if available_loras:
                selected_loras = random.sample(available_loras, min(max_slots, len(available_loras)))
                for i, lora in enumerate(selected_loras, 1):
                    if i <= max_slots:
                        kwargs[f"lora_{i}"] = lora
                        # Set random strength ranges
                        base_min = random.uniform(0.3, 0.7)
                        base_max = random.uniform(base_min + 0.1, 1.5)
                        kwargs[f"min_str_{i}"] = base_min
                        kwargs[f"max_str_{i}"] = base_max

        # Process only the first max_slots slots
        processed_loras = set()
        
        # First pass: collect explicitly configured LoRAs (only up to max_slots)
        for i in range(1, max_slots + 1):
            lora_name = kwargs.get(f"lora_{i}")
            min_str = kwargs.get(f"min_str_{i}", 0.5)
            max_str = kwargs.get(f"max_str_{i}", 1.0)
            trigger_words = kwargs.get(f"trigger_words_{i}", "")

            if lora_name and lora_name not in ["None", "Auto"] and lora_name not in processed_loras:
                if lora_name in available_loras:
                    processed_trigger_words = ', '.join([s.strip() for s in trigger_words.strip().split(',') if s.strip()]) if trigger_words else ""
                    lora_configs.append({
                        "name": lora_name,
                        "min_str": float(min_str),
                        "max_str": float(max_str),
                        "trigger_words": processed_trigger_words,
                        "slot": i
                    })
                    processed_loras.add(lora_name)

        # Second pass: handle "Auto" selections from remaining LoRAs
        remaining_loras = [lora for lora in available_loras if lora not in processed_loras]
        auto_slots = []
        
        for i in range(1, max_slots + 1):
            lora_name = kwargs.get(f"lora_{i}")
            if lora_name == "Auto" and remaining_loras:
                auto_slots.append(i)
        
        # Fill auto slots with random LoRAs from remaining pool
        if auto_slots and remaining_loras:
            auto_loras = random.sample(remaining_loras, min(len(auto_slots), len(remaining_loras)))
            for slot_idx, auto_lora in zip(auto_slots, auto_loras):
                min_str = kwargs.get(f"min_str_{slot_idx}", 0.5)
                max_str = kwargs.get(f"max_str_{slot_idx}", 1.0)
                trigger_words = kwargs.get(f"trigger_words_{slot_idx}", "")
                
                processed_trigger_words = ', '.join([s.strip() for s in trigger_words.strip().split(',') if s.strip()]) if trigger_words else ""
                lora_configs.append({
                    "name": auto_lora,
                    "min_str": float(min_str),
                    "max_str": float(max_str),
                    "trigger_words": processed_trigger_words,
                    "slot": slot_idx
                })

        # Update debug info
        debug_info += f", Configured: {len(lora_configs)}"

        # Check if no loras are selected
        if len(lora_configs) == 0:
            return (lora_list, "", "", debug_info + " - No LoRAs configured in active slots")

        # Cap min_random and max_random
        min_random = min(min_random, len(lora_configs), max_slots)
        max_random = min(max_random, len(lora_configs), max_slots)
        max_random = max(min_random, max_random)

        # Randomly choose some of these loras
        num_to_choose = random.randint(min_random, max_random)
        chosen_loras = random.sample(lora_configs, num_to_choose)

        # Track all trigger words
        all_trigger_words = set()
        chosen_lora_names = []

        for lora in chosen_loras:
            # Randomly determine a value between min_str and max_str
            strength = random.uniform(lora['min_str'], lora['max_str'])

            # Add to the stack
            lora_list.append((lora['name'], strength, strength))

            # Track chosen LoRA names
            chosen_lora_names.append(f"{lora['name']}:{strength:.2f}")

        # Combine all trigger words
        for lora in chosen_loras:
            if lora['trigger_words']:
                trigger_word_list = [word.strip() for word in lora['trigger_words'].split(',') if word.strip()]
                all_trigger_words.update(trigger_word_list)

        chosen_trigger_words = ', '.join(sorted(all_trigger_words))
        
        # Create chosen string
        chosen_str = ', '.join([f"<lora:{lora['name'].split('.')[0]}:{random.uniform(lora['min_str'], lora['max_str']):.2f}>" 
                               for lora in chosen_loras])
        
        # Update debug info
        debug_info += f", Selected: {len(chosen_loras)} ({', '.join([lora['name'] for lora in chosen_loras])})"

        return (lora_list, chosen_trigger_words, chosen_str, debug_info)


import random
import folder_paths
import comfy.sd
import comfy.utils
from typing import Dict, Any, List, Tuple


class TrulyDynamicRandomLoraStack:
    """
    Dynamic Random LoRA Stack inspired by EasyUse approach.
    Creates fixed maximum slots but only processes/displays up to max_slots parameter.
    """
    
    def __init__(self):
        pass

    @classmethod  
    def INPUT_TYPES(cls):
        loras = ["None"] + folder_paths.get_filename_list("loras")
        
        # Set a reasonable maximum number of slots (like EasyUse does)
        MAX_LORA_NUM = 15
        
        inputs = {
            "required": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "max_slots": ("INT", {"default": 5, "min": 1, "max": MAX_LORA_NUM}),
                "min_random": ("INT", {"default": 1, "min": 1, "max": MAX_LORA_NUM}),
                "max_random": ("INT", {"default": 3, "min": 1, "max": MAX_LORA_NUM}),
                "auto_populate": (["Disabled", "Enabled"], {"default": "Disabled"}),
            },
            "optional": {
                "lora_stack": ("LORA_STACK",),
            }
        }
        
        # Create maximum possible slots (following EasyUse pattern)
        for i in range(1, MAX_LORA_NUM + 1):
            # Use default "None" for slots beyond typical usage
            default_lora = "Auto" if i <= 5 else "None"
            inputs["optional"][f"lora_{i}_name"] = (
                ["None", "Auto"] + loras[1:], {"default": default_lora}
            )
            inputs["optional"][f"lora_{i}_min_str"] = (
                "FLOAT", {"default": 0.5, "min": -10.0, "max": 10.0, "step": 0.01}
            )
            inputs["optional"][f"lora_{i}_max_str"] = (
                "FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}
            )
            inputs["optional"][f"lora_{i}_trigger_words"] = (
                "STRING", {"multiline": False, "default": ""}
            )

        return inputs

    RETURN_TYPES = ("LORA_STACK", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("LORA_STACK", "trigger_words", "chosen_loras", "debug_info")
    FUNCTION = "load_lora_stack"
    CATEGORY = "unwdef/lora"

    def load_lora_stack(self, seed, max_slots, min_random, max_random, auto_populate, lora_stack=None, **kwargs):
        if seed is not None:
            random.seed(seed)

        available_loras = folder_paths.get_filename_list("loras")
        
        # Debug information
        debug_info = f"Processing {max_slots} slots from {len(available_loras)} available LoRAs"
        
        # Initialize lora stack list
        lora_list = list()
        if lora_stack is not None:
            lora_list.extend([l for l in lora_stack if l[0] != "None"])

        # Auto-populate if enabled - only for active slots
        if auto_populate == "Enabled":
            if available_loras:
                selected_loras = random.sample(available_loras, min(max_slots, len(available_loras)))
                for i, lora in enumerate(selected_loras, 1):
                    if i <= max_slots:
                        kwargs[f"lora_{i}_name"] = lora
                        # Set random strength ranges
                        base_min = random.uniform(0.3, 0.7)
                        base_max = random.uniform(base_min + 0.1, 1.5)
                        kwargs[f"lora_{i}_min_str"] = base_min
                        kwargs[f"lora_{i}_max_str"] = base_max

        # Initialize list to hold lora configurations
        lora_configs = []
        processed_loras = set()

        # CRITICAL: Only process up to max_slots (this is the key!)
        for i in range(1, max_slots + 1):
            lora_name = kwargs.get(f"lora_{i}_name")
            min_str = kwargs.get(f"lora_{i}_min_str", 0.5)
            max_str = kwargs.get(f"lora_{i}_max_str", 1.0)
            trigger_words = kwargs.get(f"lora_{i}_trigger_words", "")

            if lora_name and lora_name not in ["None"] and lora_name not in processed_loras:
                if lora_name == "Auto":
                    # Handle auto selection from remaining LoRAs
                    remaining_loras = [lora for lora in available_loras if lora not in processed_loras]
                    if remaining_loras:
                        lora_name = random.choice(remaining_loras)
                    else:
                        continue
                
                if lora_name in available_loras:
                    processed_trigger_words = ', '.join([s.strip() for s in trigger_words.strip().split(',') if s.strip()]) if trigger_words else ""
                    lora_configs.append({
                        "name": lora_name,
                        "min_str": float(min_str),
                        "max_str": float(max_str),
                        "trigger_words": processed_trigger_words,
                        "slot": i
                    })
                    processed_loras.add(lora_name)

        debug_info += f", Configured: {len(lora_configs)}"

        # Check if no loras are configured
        if len(lora_configs) == 0:
            return (lora_list, "", "", debug_info + " - No LoRAs configured in active slots")

        # Cap min_random and max_random
        min_random = min(min_random, len(lora_configs), max_slots)
        max_random = min(max_random, len(lora_configs), max_slots)
        max_random = max(min_random, max_random)

        # Randomly choose some of these loras
        num_to_choose = random.randint(min_random, max_random)
        chosen_loras = random.sample(lora_configs, num_to_choose)

        # Track all trigger words
        all_trigger_words = set()
        chosen_lora_names = []

        for lora in chosen_loras:
            # Randomly determine strength between min_str and max_str
            strength = random.uniform(lora['min_str'], lora['max_str'])

            # Add to the stack
            lora_list.append((lora['name'], strength, strength))
            chosen_lora_names.append(f"{lora['name']}:{strength:.2f}")

            # Collect trigger words
            if lora['trigger_words']:
                trigger_word_list = [word.strip() for word in lora['trigger_words'].split(',') if word.strip()]
                all_trigger_words.update(trigger_word_list)

        # Combine results
        chosen_trigger_words = ', '.join(sorted(all_trigger_words))
        chosen_str = ', '.join([f"<lora:{lora['name'].split('.')[0]}:{random.uniform(lora['min_str'], lora['max_str']):.2f}>" 
                               for lora in chosen_loras])
        
        debug_info += f", Selected: {len(chosen_loras)} ({', '.join([lora['name'] for lora in chosen_loras])})"

        return (lora_list, chosen_trigger_words, chosen_str, debug_info)


class EasyStyleDynamicLoraStack:
    """
    Alternative implementation that more closely mimics EasyUse's exact approach
    with toggle functionality and mode selection.
    """
    
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        max_lora_num = 10
        loras = ["None"] + folder_paths.get_filename_list("loras")
        
        inputs = {
            "required": {
                "toggle": ("BOOLEAN", {"label_on": "enabled", "label_off": "disabled"}),
                "mode": (["simple", "advanced", "random"],),
                "num_loras": ("INT", {"default": 1, "min": 1, "max": max_lora_num}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "optional_lora_stack": ("LORA_STACK",),
                # Random mode specific
                "min_random": ("INT", {"default": 1, "min": 1, "max": max_lora_num}),
                "max_random": ("INT", {"default": 3, "min": 1, "max": max_lora_num}),
                "auto_populate": (["Disabled", "Enabled"], {"default": "Disabled"}),
            },
        }

        # Create slots like EasyUse does
        for i in range(1, max_lora_num + 1):
            inputs["optional"][f"lora_{i}_name"] = (
                ["None", "Auto"] + loras[1:], {"default": "None"}
            )
            inputs["optional"][f"lora_{i}_strength"] = (
                "FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}
            )
            inputs["optional"][f"lora_{i}_min_strength"] = (
                "FLOAT", {"default": 0.5, "min": -10.0, "max": 10.0, "step": 0.01}
            )
            inputs["optional"][f"lora_{i}_max_strength"] = (
                "FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}
            )
            inputs["optional"][f"lora_{i}_model_strength"] = (
                "FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}
            )
            inputs["optional"][f"lora_{i}_clip_strength"] = (
                "FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}
            )
            inputs["optional"][f"lora_{i}_trigger_words"] = (
                "STRING", {"multiline": False, "default": ""}
            )

        return inputs

    RETURN_TYPES = ("LORA_STACK", "STRING", "STRING")
    RETURN_NAMES = ("LORA_STACK", "trigger_words", "debug_info")
    FUNCTION = "stack"
    CATEGORY = "unwdef/lora"

    def stack(self, toggle, mode, num_loras, seed, optional_lora_stack=None, min_random=1, max_random=3, auto_populate="Disabled", **kwargs):
        if toggle in [False, None, "False"]:
            return (None, "", "Toggle disabled")

        if seed is not None:
            random.seed(seed)

        loras = []
        available_loras = folder_paths.get_filename_list("loras")

        # Import existing stack values
        if optional_lora_stack is not None:
            loras.extend([l for l in optional_lora_stack if l[0] != "None"])

        # Auto-populate if enabled (only for random mode)
        if mode == "random" and auto_populate == "Enabled":
            if available_loras:
                selected_loras = random.sample(available_loras, min(num_loras, len(available_loras)))
                for i, lora in enumerate(selected_loras, 1):
                    if i <= num_loras:
                        kwargs[f"lora_{i}_name"] = lora
                        kwargs[f"lora_{i}_min_strength"] = random.uniform(0.3, 0.7)
                        kwargs[f"lora_{i}_max_strength"] = random.uniform(0.8, 1.5)

        # Collect configured LoRAs from slots (only up to num_loras)
        lora_configs = []
        processed_loras = set()
        all_trigger_words = set()

        for i in range(1, num_loras + 1):  # Only process num_loras slots!
            lora_name = kwargs.get(f"lora_{i}_name")
            
            if not lora_name or lora_name == "None":
                continue

            # Handle Auto selection
            if lora_name == "Auto":
                remaining_loras = [lora for lora in available_loras if lora not in processed_loras]
                if remaining_loras:
                    lora_name = random.choice(remaining_loras)
                else:
                    continue

            if lora_name in processed_loras:
                continue

            # Get trigger words
            trigger_words = kwargs.get(f"lora_{i}_trigger_words", "")
            if trigger_words:
                words = [w.strip() for w in trigger_words.split(',') if w.strip()]
                all_trigger_words.update(words)

            if mode == "simple":
                lora_strength = float(kwargs.get(f"lora_{i}_strength", 1.0))
                lora_configs.append((lora_name, lora_strength, lora_strength))
            elif mode == "advanced":
                model_strength = float(kwargs.get(f"lora_{i}_model_strength", 1.0))
                clip_strength = float(kwargs.get(f"lora_{i}_clip_strength", 1.0))
                lora_configs.append((lora_name, model_strength, clip_strength))
            elif mode == "random":
                min_str = float(kwargs.get(f"lora_{i}_min_strength", 0.5))
                max_str = float(kwargs.get(f"lora_{i}_max_strength", 1.0))
                strength = random.uniform(min_str, max_str)
                lora_configs.append((lora_name, strength, strength))

            processed_loras.add(lora_name)

        # For random mode, randomly select from configured LoRAs
        if mode == "random" and lora_configs:
            min_select = min(min_random, len(lora_configs))
            max_select = min(max_random, len(lora_configs))
            max_select = max(min_select, max_select)
            num_to_select = random.randint(min_select, max_select)
            lora_configs = random.sample(lora_configs, num_to_select)

        # Add to final lora list
        loras.extend(lora_configs)

        # Combine trigger words
        combined_trigger_words = ', '.join(sorted(all_trigger_words))
        
        debug_info = f"Mode: {mode}, Processed: {len(lora_configs)} LoRAs from {num_loras} slots"

        return (loras, combined_trigger_words, debug_info)

# WEB_DIRECTORY points to the web folder containing our JavaScript
WEB_DIRECTORY = "./web"

# Node mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "Truly Dynamic Random LoRA Stack": TrulyDynamicRandomLoraStack,
    "EasyStyle Dynamic LoRA Stack": EasyStyleDynamicLoraStack,
    "Dynamic Random LoRA Stack": DynamicRandomLoraStack,
    "Ultra Dynamic LoRA Stack": UltraDynamicLoraStack,
    "Simple Random LoRA Stack": SimpleRandomLoraStack,  # Keep original
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Truly Dynamic Random LoRA Stack": "🎯 Truly Dynamic Random LoRA Stack",
    "EasyStyle Dynamic LoRA Stack": "🎲 EasyStyle Dynamic LoRA Stack",
    "Dynamic Random LoRA Stack": "🎲 Dynamic Random LoRA Stack (No Limits)",
    "Ultra Dynamic LoRA Stack": "🚀 Ultra Dynamic LoRA Stack (Config-Based)",
    "Simple Random LoRA Stack": "Simple Random LoRA Stack (Variable Slots)",
}
