"""
Random LoRA Chooser - ComfyUI Custom Node
Dynamic LoRA selection with trigger words support, implementing EasyUse-style behavior
"""

import random
import folder_paths
from typing import Dict, Any, List, Tuple, Optional


class DynamicRandomLoraChooser:
    """
    Dynamic Random LoRA Chooser with trigger words support.
    Implements EasyUse-style "dynamic" behavior: all slots visible, but only first num_loras processed.
    """
    
    def __init__(self):
        pass

    @classmethod  
    def INPUT_TYPES(cls):
        loras = ["None"] + folder_paths.get_filename_list("loras")
        
        # Maximum number of LoRA slots (like EasyUse)
        MAX_LORA_NUM = 10
        
        inputs = {
            "required": {
                "toggle": ("BOOLEAN", {"label_on": "enabled", "label_off": "disabled", "default": True}),
                "num_loras": ("INT", {"default": 3, "min": 1, "max": MAX_LORA_NUM}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "selection_mode": (["random", "all_configured", "weighted"], {"default": "random"}),
                "min_random": ("INT", {"default": 1, "min": 1, "max": MAX_LORA_NUM}),
                "max_random": ("INT", {"default": 2, "min": 1, "max": MAX_LORA_NUM}),
                "global_min_strength": ("FLOAT", {"default": 0.5, "min": -10.0, "max": 10.0, "step": 0.01}),
                "global_max_strength": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                "auto_populate": (["Disabled", "Random Fill"], {"default": "Disabled"}),
            },
            "optional": {
                "optional_lora_stack": ("LORA_STACK",),
            }
        }
        
        # Create ALL possible slots (EasyUse approach: all slots always visible)
        for i in range(1, MAX_LORA_NUM + 1):
            inputs["optional"][f"lora_{i}_name"] = (
                ["None", "Auto"] + loras[1:], {"default": "None"}
            )
            inputs["optional"][f"lora_{i}_min_strength"] = (
                "FLOAT", {"default": 0.5, "min": -10.0, "max": 10.0, "step": 0.01}
            )
            inputs["optional"][f"lora_{i}_max_strength"] = (
                "FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}
            )
            inputs["optional"][f"lora_{i}_weight"] = (
                "FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.1}
            )
            inputs["optional"][f"lora_{i}_trigger_words"] = (
                "STRING", {"multiline": False, "default": "", "placeholder": "cute, detailed, masterpiece"}
            )

        return inputs

    RETURN_TYPES = ("LORA_STACK", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("lora_stack", "trigger_words", "chosen_loras_info", "debug_info")
    FUNCTION = "choose_random_loras"
    CATEGORY = "loaders/lora"

    def choose_random_loras(self, toggle, num_loras, seed, selection_mode, min_random, max_random, 
                           global_min_strength, global_max_strength, auto_populate, 
                           optional_lora_stack=None, **kwargs):
        """
        Main function to randomly choose LoRAs from configured slots.
        KEY: Only processes the first num_loras slots, ignoring the rest (EasyUse behavior).
        """
        
        if toggle in [False, None, "False"]:
            return (None, "", "", "Node disabled via toggle")

        if seed is not None:
            random.seed(seed)

        available_loras = folder_paths.get_filename_list("loras")
        
        # Initialize lora stack list
        lora_list = []
        if optional_lora_stack is not None:
            lora_list.extend([l for l in optional_lora_stack if l[0] != "None"])

        # Auto-populate if enabled
        if auto_populate == "Random Fill" and available_loras:
            self._auto_populate_slots(kwargs, available_loras, num_loras, global_min_strength, global_max_strength)

        # *** KEY INSIGHT: Only process the first num_loras slots (EasyUse behavior) ***
        lora_configs = self._collect_lora_configs(kwargs, num_loras, available_loras)
        
        debug_info = f"Processing slots 1-{num_loras} of 10 total, Configured: {len(lora_configs)}, Available LoRAs: {len(available_loras)}"

        if not lora_configs:
            return (lora_list, "", "", debug_info + " - No LoRAs configured in active slots")

        # Clamp min_random and max_random to valid ranges
        min_random = max(1, min(min_random, num_loras, len(lora_configs)))
        max_random = max(min_random, min(max_random, num_loras, len(lora_configs)))

        # Select LoRAs based on mode
        selected_loras = self._select_loras(lora_configs, selection_mode, min_random, max_random)
        
        # Process selected LoRAs and build outputs
        all_trigger_words = []
        chosen_lora_names = []
        chosen_lora_details = []

        for lora_config in selected_loras:
            # Generate random strength within the specified range
            strength = random.uniform(lora_config['min_strength'], lora_config['max_strength'])
            
            # Add to LoRA stack (model_strength, clip_strength)
            lora_list.append((lora_config['name'], strength, strength))
            
            # Track for output info
            lora_short_name = lora_config['name'].split('.')[0]  # Remove file extension
            chosen_lora_names.append(f"<lora:{lora_short_name}:{strength:.2f}>")
            chosen_lora_details.append(f"{lora_config['name']} @ {strength:.2f}")
            
            # Collect trigger words
            if lora_config['trigger_words']:
                words = [w.strip() for w in lora_config['trigger_words'].split(',') if w.strip()]
                all_trigger_words.extend(words)

        # Combine and format results
        trigger_words_str = ', '.join(all_trigger_words) if all_trigger_words else ""
        chosen_loras_str = ', '.join(chosen_lora_names)
        debug_info += f" | Selected: {len(selected_loras)} LoRAs ({selection_mode} mode)"

        return (lora_list, trigger_words_str, chosen_loras_str, debug_info)

    def _auto_populate_slots(self, kwargs: dict, available_loras: list, num_loras: int, 
                           min_strength: float, max_strength: float):
        """Auto-populate empty slots with random LoRAs and settings"""
        used_loras = set()
        
        # First, collect already configured LoRAs to avoid duplicates
        for i in range(1, num_loras + 1):  # Only check first num_loras slots
            lora_name = kwargs.get(f"lora_{i}_name")
            if lora_name and lora_name not in ["None", "Auto"]:
                used_loras.add(lora_name)
        
        # Get remaining LoRAs for auto-population
        remaining_loras = [lora for lora in available_loras if lora not in used_loras]
        random.shuffle(remaining_loras)  # Shuffle for randomness
        
        # Fill empty/Auto slots in the ACTIVE range only
        fill_index = 0
        for i in range(1, num_loras + 1):  # Only fill first num_loras slots
            lora_name = kwargs.get(f"lora_{i}_name")
            
            if (not lora_name or lora_name in ["None", "Auto"]) and fill_index < len(remaining_loras):
                # Set random LoRA and parameters
                kwargs[f"lora_{i}_name"] = remaining_loras[fill_index]
                kwargs[f"lora_{i}_min_strength"] = random.uniform(min_strength, min_strength + 0.2)
                kwargs[f"lora_{i}_max_strength"] = random.uniform(max_strength - 0.2, max_strength)
                kwargs[f"lora_{i}_weight"] = random.uniform(0.5, 2.0)
                fill_index += 1

    def _collect_lora_configs(self, kwargs: dict, num_loras: int, available_loras: list) -> List[Dict]:
        """
        Collect LoRA configurations from the first num_loras slots ONLY.
        This is the core of EasyUse's "dynamic" behavior - ignore slots beyond num_loras.
        """
        lora_configs = []
        processed_loras = set()
        
        # *** CRITICAL: Only process the first num_loras slots ***
        for i in range(1, num_loras + 1):
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
            
            # Skip if already processed or doesn't exist
            if lora_name in processed_loras or lora_name not in available_loras:
                continue
            
            # Get configuration parameters
            min_strength = float(kwargs.get(f"lora_{i}_min_strength", 0.5))
            max_strength = float(kwargs.get(f"lora_{i}_max_strength", 1.0))
            weight = float(kwargs.get(f"lora_{i}_weight", 1.0))
            trigger_words = kwargs.get(f"lora_{i}_trigger_words", "")
            
            # Ensure min <= max
            if min_strength > max_strength:
                min_strength, max_strength = max_strength, min_strength
            
            lora_configs.append({
                "name": lora_name,
                "min_strength": min_strength,
                "max_strength": max_strength,
                "weight": weight,
                "trigger_words": trigger_words.strip(),
                "slot": i
            })
            
            processed_loras.add(lora_name)
        
        return lora_configs

    def _select_loras(self, lora_configs: List[Dict], selection_mode: str, 
                     min_random: int, max_random: int) -> List[Dict]:
        """Select LoRAs based on the selection mode"""
        if not lora_configs:
            return []
        
        if selection_mode == "all_configured":
            return lora_configs
        
        # Cap the random selection to available configs
        min_select = min(min_random, len(lora_configs))
        max_select = min(max_random, len(lora_configs))
        max_select = max(min_select, max_select)  # Ensure max >= min
        
        num_to_select = random.randint(min_select, max_select)
        
        if selection_mode == "weighted":
            # Weighted selection based on weight values
            weights = [config['weight'] for config in lora_configs]
            selected_configs = random.choices(lora_configs, weights=weights, k=num_to_select)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_selected = []
            for config in selected_configs:
                if config['name'] not in seen:
                    unique_selected.append(config)
                    seen.add(config['name'])
                if len(unique_selected) >= num_to_select:
                    break
            return unique_selected
        
        else:  # random selection
            return random.sample(lora_configs, num_to_select)


class SimpleRandomLoraChooser:
    """
    Simplified version with cleaner interface, implementing EasyUse-style behavior
    """
    
    def __init__(self):
        pass

    @classmethod  
    def INPUT_TYPES(cls):
        loras = ["None"] + folder_paths.get_filename_list("loras")
        MAX_LORA_NUM = 8
        
        inputs = {
            "required": {
                "toggle": ("BOOLEAN", {"label_on": "enabled", "label_off": "disabled", "default": True}),
                "num_loras": ("INT", {"default": 3, "min": 1, "max": MAX_LORA_NUM}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "min_select": ("INT", {"default": 1, "min": 1, "max": MAX_LORA_NUM}),
                "max_select": ("INT", {"default": 2, "min": 1, "max": MAX_LORA_NUM}),
                "min_strength": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 2.0, "step": 0.01}),
                "max_strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.01}),
                "auto_fill": (["Disabled", "Random Fill"], {"default": "Disabled"}),
            },
            "optional": {
                "optional_lora_stack": ("LORA_STACK",),
            }
        }
        
        # Create ALL slots (EasyUse approach: all slots always visible)
        for i in range(1, MAX_LORA_NUM + 1):
            inputs["optional"][f"lora_{i}"] = (
                ["None", "Auto"] + loras[1:], {"default": "None"}
            )
            inputs["optional"][f"triggers_{i}"] = (
                "STRING", {"multiline": False, "default": "", "placeholder": "trigger words"}
            )

        return inputs

    RETURN_TYPES = ("LORA_STACK", "STRING", "STRING")
    RETURN_NAMES = ("lora_stack", "trigger_words", "debug_info")
    FUNCTION = "choose_loras"
    CATEGORY = "loaders/lora"

    def choose_loras(self, toggle, num_loras, seed, min_select, max_select, 
                    min_strength, max_strength, auto_fill, optional_lora_stack=None, **kwargs):
        
        if toggle in [False, None, "False"]:
            return (None, "", "Disabled")

        if seed is not None:
            random.seed(seed)

        available_loras = folder_paths.get_filename_list("loras")
        
        # Initialize lora stack
        lora_list = []
        if optional_lora_stack is not None:
            lora_list.extend([l for l in optional_lora_stack if l[0] != "None"])

        # Auto fill if enabled
        if auto_fill == "Random Fill" and available_loras:
            self._auto_fill_slots(kwargs, available_loras, num_loras)

        # *** KEY: Only collect valid LoRAs from the first num_loras slots ***
        valid_loras = []
        all_triggers = set()
        
        for i in range(1, num_loras + 1):  # Only process first num_loras slots
            lora_name = kwargs.get(f"lora_{i}")
            triggers = kwargs.get(f"triggers_{i}", "")
            
            if not lora_name or lora_name == "None":
                continue
                
            if lora_name == "Auto" and available_loras:
                lora_name = random.choice(available_loras)
            
            if lora_name in available_loras:
                valid_loras.append((lora_name, triggers))
                
                # Collect triggers
                if triggers:
                    trigger_list = [t.strip() for t in triggers.split(',') if t.strip()]
                    all_triggers.update(trigger_list)

        if not valid_loras:
            return (lora_list, "", f"No valid LoRAs in first {num_loras} slots")

        # Clamp selection values
        min_sel = max(1, min(min_select, len(valid_loras)))
        max_sel = max(min_sel, min(max_select, len(valid_loras)))
        
        num_to_select = random.randint(min_sel, max_sel)
        selected = random.sample(valid_loras, num_to_select)

        # Add to stack with random strengths
        for lora_name, _ in selected:
            strength = random.uniform(min_strength, max_strength)
            lora_list.append((lora_name, strength, strength))

        combined_triggers = ', '.join(sorted(all_triggers))
        debug_info = f"Selected {len(selected)} from {len(valid_loras)} valid LoRAs (processing slots 1-{num_loras})"

        return (lora_list, combined_triggers, debug_info)

    def _auto_fill_slots(self, kwargs, available_loras, num_loras):
        """Auto fill empty slots with random LoRAs - only first num_loras slots"""
        if not available_loras:
            return
            
        fill_loras = random.sample(available_loras, min(num_loras, len(available_loras)))
        
        for i in range(1, num_loras + 1):  # Only fill first num_loras slots
            if not kwargs.get(f"lora_{i}") or kwargs.get(f"lora_{i}") == "None":
                if i <= len(fill_loras):
                    kwargs[f"lora_{i}"] = fill_loras[i-1]


# Node mappings for ComfyUI to discover
NODE_CLASS_MAPPINGS = {
    "DynamicRandomLoraChooser": DynamicRandomLoraChooser,
    "SimpleRandomLoraChooser": SimpleRandomLoraChooser,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DynamicRandomLoraChooser": "🎯 Dynamic Random LoRA Chooser",
    "SimpleRandomLoraChooser": "⚡ Simple Random LoRA Chooser",
}