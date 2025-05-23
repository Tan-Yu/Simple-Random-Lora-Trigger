import random
import folder_paths

class EasyUseDynamicLoraStack:
    """
    TRUE Dynamic LoRA Stack using EasyUse's EXACT method.
    Uses dynamic widget manipulation exactly like EasyUse does.
    """
    
    def __init__(self):
        pass

    @classmethod  
    def INPUT_TYPES(cls):
        loras = ["None"] + folder_paths.get_filename_list("loras")
        
        # EasyUse uses max 10 slots
        MAX_LORA_NUM = 10
        
        inputs = {
            "required": {
                "toggle": ("BOOLEAN", {"label_on": "enabled", "label_off": "disabled"}),
                "mode": (["simple", "advanced"], {"default": "simple"}),
                "num_loras": ("INT", {"default": 1, "min": 1, "max": MAX_LORA_NUM}),
            },
            "optional": {
                "optional_lora_stack": ("LORA_STACK",),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "selection_mode": (["random", "all_configured", "weighted"], {"default": "all_configured"}),
                "min_random": ("INT", {"default": 1, "min": 1, "max": MAX_LORA_NUM}),
                "max_random": ("INT", {"default": 3, "min": 1, "max": MAX_LORA_NUM}),
            }
        }
        
        # Pre-define ALL possible slots (EasyUse method)
        # JavaScript will dynamically show/hide these based on num_loras
        for i in range(1, MAX_LORA_NUM + 1):
            inputs["optional"][f"lora_{i}_name"] = (
                ["None"] + loras, {"default": "None"}
            )
            inputs["optional"][f"lora_{i}_strength"] = (
                "FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}
            )
            inputs["optional"][f"lora_{i}_model_strength"] = (
                "FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}
            )
            inputs["optional"][f"lora_{i}_clip_strength"] = (
                "FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}
            )

        return inputs

    RETURN_TYPES = ("LORA_STACK", "STRING", "STRING")
    RETURN_NAMES = ("LORA_STACK", "chosen_loras", "debug_info")
    FUNCTION = "stack"
    CATEGORY = "EasyUse/Loaders"

    def stack(self, toggle, mode, num_loras, optional_lora_stack=None, seed=0, 
              selection_mode="all_configured", min_random=1, max_random=3, **kwargs):
        
        if toggle in [False, None, "False"]:
            return (None, "", "Node disabled")

        if seed is not None:
            random.seed(seed)

        available_loras = folder_paths.get_filename_list("loras")
        
        # Initialize lora stack
        lora_list = []
        if optional_lora_stack is not None:
            lora_list.extend([l for l in optional_lora_stack if l[0] != "None"])

        # KEY: Only process the first num_loras slots (EasyUse method)
        lora_configs = []
        
        for i in range(1, num_loras + 1):
            lora_name = kwargs.get(f"lora_{i}_name")
            
            if not lora_name or lora_name == "None":
                continue
            
            if lora_name not in available_loras:
                continue
            
            if mode == "simple":
                strength = float(kwargs.get(f"lora_{i}_strength", 1.0))
                model_strength = strength
                clip_strength = strength
            else:  # advanced
                model_strength = float(kwargs.get(f"lora_{i}_model_strength", 1.0))
                clip_strength = float(kwargs.get(f"lora_{i}_clip_strength", 1.0))
            
            lora_configs.append({
                "name": lora_name,
                "model_strength": model_strength,
                "clip_strength": clip_strength,
                "slot": i
            })
        
        if not lora_configs:
            return (lora_list, "", f"No LoRAs configured in {num_loras} active slots")

        # Select LoRAs based on mode
        if selection_mode == "all_configured":
            selected_loras = lora_configs
        else:
            # Random selection
            min_select = min(min_random, len(lora_configs))
            max_select = min(max_random, len(lora_configs))
            max_select = max(min_select, max_select)
            
            num_to_select = random.randint(min_select, max_select)
            selected_loras = random.sample(lora_configs, num_to_select)
        
        # Add selected LoRAs to stack
        chosen_names = []
        for config in selected_loras:
            model_str = config['model_strength']
            clip_str = config['clip_strength']
            lora_list.append((config['name'], model_str, clip_str))
            chosen_names.append(f"{config['name']}:{model_str:.2f}")

        chosen_str = ', '.join(chosen_names)
        debug_info = f"Active slots: {num_loras}, Selected: {len(selected_loras)} ({selection_mode})"

        return (lora_list, chosen_str, debug_info)


NODE_CLASS_MAPPINGS = {
    "EasyUse Dynamic LoRA Stack": EasyUseDynamicLoraStack,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "EasyUse Dynamic LoRA Stack": "🎯 Dynamic LoRA Stack",
}
