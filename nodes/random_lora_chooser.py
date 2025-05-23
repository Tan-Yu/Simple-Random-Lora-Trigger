import os
import random
import json
import folder_paths

class RandomLoraChooser:
    @classmethod
    def INPUT_TYPES(cls):
        max_lora_num = 20
        
        inputs = {
            "required": {
                "num_loras": ("INT", {"default": 3, "min": 1, "max": max_lora_num}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "randomize_seed": ("BOOLEAN", {"default": True}),
            },
            "optional": {}
        }
        
        # Add dynamic LoRA inputs
        for i in range(1, max_lora_num + 1):
            inputs["optional"][f"lora_{i}_name"] = (
                ["None"] + folder_paths.get_filename_list("loras"), 
                {"default": "None"}
            )
            inputs["optional"][f"lora_{i}_trigger"] = (
                "STRING", 
                {"default": "", "multiline": False, "placeholder": f"Trigger word for LoRA {i}"}
            )
            inputs["optional"][f"lora_{i}_weight"] = (
                "FLOAT", 
                {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.01}
            )
            
        return inputs
    
    RETURN_TYPES = ("STRING", "STRING", "FLOAT", "LORA_STACK", "STRING")
    RETURN_NAMES = ("selected_lora", "trigger_word", "lora_weight", "lora_stack", "debug_info")
    
    FUNCTION = "choose_random_lora"
    CATEGORY = "Random LoRA Chooser"
    
    def choose_random_lora(self, num_loras, seed, randomize_seed, **kwargs):
        # Set random seed
        if randomize_seed:
            random.seed()
        else:
            random.seed(seed)
        
        # Collect available LoRAs from the inputs
        available_loras = []
        
        for i in range(1, num_loras + 1):
            lora_name = kwargs.get(f"lora_{i}_name", "None")
            trigger_word = kwargs.get(f"lora_{i}_trigger", "")
            weight = kwargs.get(f"lora_{i}_weight", 1.0)
            
            if lora_name and lora_name != "None":
                available_loras.append({
                    "name": lora_name,
                    "trigger": trigger_word,
                    "weight": weight,
                    "index": i
                })
        
        # Debug info
        debug_info = f"Total configured LoRAs: {num_loras}\n"
        debug_info += f"Available LoRAs: {len(available_loras)}\n"
        debug_info += f"Seed: {seed}\n"
        debug_info += f"Randomize: {randomize_seed}\n\n"
        
        if not available_loras:
            empty_stack = []
            return ("None", "", 0.0, empty_stack, debug_info + "No LoRAs available!")
        
        # Choose random LoRA
        chosen_lora = random.choice(available_loras)
        
        debug_info += f"Chosen LoRA: {chosen_lora['name']}\n"
        debug_info += f"Trigger Word: {chosen_lora['trigger']}\n"
        debug_info += f"Weight: {chosen_lora['weight']}\n"
        debug_info += f"Index: {chosen_lora['index']}"
        
        # Create LoRA stack with the chosen LoRA
        lora_stack = [(chosen_lora["name"], chosen_lora["weight"], chosen_lora["weight"])]
        
        return (
            chosen_lora["name"],
            chosen_lora["trigger"],
            chosen_lora["weight"],
            lora_stack,
            debug_info
        )
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # Force re-execution when randomize_seed is True
        if kwargs.get("randomize_seed", False):
            return float("NaN")
        return kwargs.get("seed", 0)

# Alternative version with LoRA Stack input/output
class RandomLoraChooserAdvanced:
    @classmethod
    def INPUT_TYPES(cls):
        max_lora_num = 20
        
        inputs = {
            "required": {
                "num_loras": ("INT", {"default": 3, "min": 1, "max": max_lora_num}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "randomize_seed": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "input_lora_stack": ("LORA_STACK",),
            }
        }
        
        # Add dynamic LoRA inputs
        for i in range(1, max_lora_num + 1):
            inputs["optional"][f"lora_{i}_name"] = (
                ["None"] + folder_paths.get_filename_list("loras"), 
                {"default": "None"}
            )
            inputs["optional"][f"lora_{i}_trigger"] = (
                "STRING", 
                {"default": "", "multiline": False, "placeholder": f"Trigger word for LoRA {i}"}
            )
            inputs["optional"][f"lora_{i}_model_weight"] = (
                "FLOAT", 
                {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.01}
            )
            inputs["optional"][f"lora_{i}_clip_weight"] = (
                "FLOAT", 
                {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.01}
            )
            
        return inputs
    
    RETURN_TYPES = ("STRING", "STRING", "FLOAT", "FLOAT", "LORA_STACK", "STRING")
    RETURN_NAMES = ("selected_lora", "trigger_word", "model_weight", "clip_weight", "lora_stack", "debug_info")
    
    FUNCTION = "choose_random_lora_advanced"
    CATEGORY = "Random LoRA Chooser"
    
    def choose_random_lora_advanced(self, num_loras, seed, randomize_seed, input_lora_stack=None, **kwargs):
        # Set random seed
        if randomize_seed:
            random.seed()
        else:
            random.seed(seed)
        
        # Collect available LoRAs from the inputs
        available_loras = []
        
        # Add LoRAs from input stack if provided
        if input_lora_stack:
            for lora_data in input_lora_stack:
                available_loras.append({
                    "name": lora_data[0],
                    "trigger": "",  # LoRA stacks don't typically include trigger words
                    "model_weight": lora_data[1],
                    "clip_weight": lora_data[2],
                    "source": "stack"
                })
        
        # Add LoRAs from widget inputs
        for i in range(1, num_loras + 1):
            lora_name = kwargs.get(f"lora_{i}_name", "None")
            trigger_word = kwargs.get(f"lora_{i}_trigger", "")
            model_weight = kwargs.get(f"lora_{i}_model_weight", 1.0)
            clip_weight = kwargs.get(f"lora_{i}_clip_weight", 1.0)
            
            if lora_name and lora_name != "None":
                available_loras.append({
                    "name": lora_name,
                    "trigger": trigger_word,
                    "model_weight": model_weight,
                    "clip_weight": clip_weight,
                    "source": "widget",
                    "index": i
                })
        
        # Debug info
        debug_info = f"Total configured LoRAs: {num_loras}\n"
        debug_info += f"Available LoRAs: {len(available_loras)}\n"
        debug_info += f"From stack: {sum(1 for l in available_loras if l['source'] == 'stack')}\n"
        debug_info += f"From widgets: {sum(1 for l in available_loras if l['source'] == 'widget')}\n"
        debug_info += f"Seed: {seed}\n"
        debug_info += f"Randomize: {randomize_seed}\n\n"
        
        if not available_loras:
            empty_stack = []
            return ("None", "", 0.0, 0.0, empty_stack, debug_info + "No LoRAs available!")
        
        # Choose random LoRA
        chosen_lora = random.choice(available_loras)
        
        debug_info += f"Chosen LoRA: {chosen_lora['name']}\n"
        debug_info += f"Trigger Word: {chosen_lora['trigger']}\n"
        debug_info += f"Model Weight: {chosen_lora['model_weight']}\n"
        debug_info += f"Clip Weight: {chosen_lora['clip_weight']}\n"
        debug_info += f"Source: {chosen_lora['source']}"
        
        # Create output LoRA stack
        output_stack = [(chosen_lora["name"], chosen_lora["model_weight"], chosen_lora["clip_weight"])]
        
        return (
            chosen_lora["name"],
            chosen_lora["trigger"],
            chosen_lora["model_weight"],
            chosen_lora["clip_weight"],
            output_stack,
            debug_info
        )
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # Force re-execution when randomize_seed is True
        if kwargs.get("randomize_seed", False):
            return float("NaN")
        return kwargs.get("seed", 0)

# Export both classes
NODE_CLASS_MAPPINGS = {
    "RandomLoraChooser": RandomLoraChooser,
    "RandomLoraChooserAdvanced": RandomLoraChooserAdvanced,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RandomLoraChooser": "Random LoRA Chooser",
    "RandomLoraChooserAdvanced": "Random LoRA Chooser (Advanced)",
}