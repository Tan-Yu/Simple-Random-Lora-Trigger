import random
from nodes import LoraLoader
import folder_paths

class RandomizeLoras:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        loras = ["None"] + folder_paths.get_filename_list("loras")
        inputs = {
            "required": {
                "model": ("MODEL",),
                "clip": ("CLIP", ),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "min_random": ("INT", {"default": 1, "min": 1, "max": 50}),
                "max_random": ("INT", {"default": 50, "min": 1, "max": 50}),
            }
        }
        for i in range(1, 51):  # Changed from 21 to 51 for 50 LoRAs
            inputs["required"][f"lora_{i}"] = (loras,)
            inputs["required"][f"min_str_{i}"] = ("FLOAT", {"default": 0.5, "min": -10.0, "max": 10.0, "step": 0.01})
            inputs["required"][f"max_str_{i}"] = ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01})
            inputs["required"][f"trigger_words_{i}"] = ("STRING", { "multiline": False, "default": "" })

        return inputs
  
    RETURN_TYPES = ("MODEL", "CLIP", "STRING", "STRING")
    RETURN_NAMES = ("model", "clip", "trigger_words", "chosen_loras")
    FUNCTION = "load_lora"
    CATEGORY = "SimpleRandomLora/lora"

    def load_lora(self, model, clip, seed, min_random, max_random, **kwargs):      
        if seed is not None:
            random.seed(seed)  # For reproducibility

        # Initialize list to hold lora configurations
        lora_configs = []

        # Dynamically extract lora configurations from kwargs
        for i in range(1, 51):  # Changed from 21 to 51 for 50 LoRAs
            lora_name = kwargs.get(f"lora_{i}")
            min_str = kwargs.get(f"min_str_{i}")
            max_str = kwargs.get(f"max_str_{i}")
            trigger_words = kwargs.get(f"trigger_words_{i}")

            if lora_name != "None" and not any(config['name'] == lora_name for config in lora_configs):
                lora_configs.append({"name": lora_name, "min_str": min_str, "max_str": max_str, 
                                     "trigger_words": ', '.join([s.strip() for s in trigger_words.strip().split(',') if s.strip()])})

        # Initialize the string to hold chosen loras and values
        chosen_str = ""

        # Initialize the string to hold the trigger words
        chosen_trigger_words = ""

        # Check if no loras are selected
        if len(lora_configs) == 0:
            return (model, clip, chosen_trigger_words, chosen_str)
        
        # Cap min_random and max_random to length of lora configs
        min_random = min(min_random, len(lora_configs))
        max_random = min(max_random, len(lora_configs))

        # Make sure max_random >= min_random
        max_random = max(min_random, max_random)        

        # Randomly choose some of these loras
        chosen_loras = random.sample(lora_configs, random.randint(min_random, max_random))

        for lora in chosen_loras:
            # Randomly determine a value between min_str and max_str
            strength = random.uniform(lora['min_str'], lora['max_str'])

            # Apply changes to model and clip
            model, clip = LoraLoader().load_lora(model, clip, lora['name'], strength, strength)

            # Append the current lora and its value to the string
            chosen_str += f"<lora:{lora['name'].split('.')[0]}:{strength:.2f}>, "

            # Append the trigger words for each lora
            existing_chosen_trigger_words = set(chosen_trigger_words.split(', '))
            chosen_trigger_words = set(lora['trigger_words'].split(', '))
            combined_words = existing_chosen_trigger_words | chosen_trigger_words
            chosen_trigger_words = ', '.join(sorted(combined_words))

        # Find the last occurrence of the comma to remove it
        last_comma_index = chosen_str.rfind(',')
        # Slice the string to remove the last comma and everything after it
        if last_comma_index != -1:
            chosen_str = chosen_str[:last_comma_index]
            
        return (model, clip, chosen_trigger_words.lstrip(", "), chosen_str)
    
class RandomizeLorasStack:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        loras = ["None"] + folder_paths.get_filename_list("loras")
        inputs = {
            "required": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "min_random": ("INT", {"default": 1, "min": 1, "max": 50}),
                "max_random": ("INT", {"default": 50, "min": 1, "max": 50}),
            }
        }
        for i in range(1, 51):  # Changed from 21 to 51 for 50 LoRAs
            inputs["required"][f"lora_{i}"] = (loras,)
            inputs["required"][f"min_str_{i}"] = ("FLOAT", {"default": 0.5, "min": -10.0, "max": 10.0, "step": 0.01})
            inputs["required"][f"max_str_{i}"] = ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01})
            inputs["required"][f"trigger_words_{i}"] = ("STRING", { "multiline": False, "default": "" })

        inputs["optional"] = {
            "lora_stack": ("LORA_STACK",)
        }

        return inputs
  
    RETURN_TYPES = ("LORA_STACK", "STRING", "STRING")
    RETURN_NAMES = ("LORA_STACK", "trigger_words", "chosen_loras")
    FUNCTION = "load_lora_stack"
    CATEGORY = "unwdef/lora"

    def load_lora_stack(self, seed, min_random, max_random, lora_stack=None, **kwargs):      
        if seed is not None:
            random.seed(seed)  # For reproducibility

        # Initialize list to hold lora configurations
        lora_configs = []

        # Initialize lora stack list
        lora_list = list()
        if lora_stack is not None:
            lora_list.extend([l for l in lora_stack if l[0] != "None"])

        # Dynamically extract lora configurations from kwargs
        for i in range(1, 51):  # Changed from 21 to 51 for 50 LoRAs
            lora_name = kwargs.get(f"lora_{i}")
            min_str = kwargs.get(f"min_str_{i}")
            max_str = kwargs.get(f"max_str_{i}")
            trigger_words = kwargs.get(f"trigger_words_{i}")

            if lora_name != "None" and not any(config['name'] == lora_name for config in lora_configs):
                lora_configs.append({"name": lora_name, "min_str": min_str, "max_str": max_str, 
                                     "trigger_words": ', '.join([s.strip() for s in trigger_words.strip().split(',') if s.strip()])})

        # Initialize the string to hold chosen loras and values
        chosen_str = ""

        # Initialize the string to hold the trigger words
        chosen_trigger_words = ""

        # Check if no loras are selected
        if len(lora_configs) == 0:
            return (lora_list, chosen_trigger_words, chosen_str, )
        
        # Cap min_random and max_random to length of lora configs
        min_random = min(min_random, len(lora_configs))
        max_random = min(max_random, len(lora_configs))

        # Make sure max_random >= min_random
        max_random = max(min_random, max_random)  

        # Randomly choose some of these loras
        chosen_loras = random.sample(lora_configs, random.randint(min_random, max_random))

        for lora in chosen_loras:
            # Randomly determine a value between min_str and max_str
            strength = random.uniform(lora['min_str'], lora['max_str'])

            # Add to the stack
            lora_list.extend([(lora['name'], strength, strength)]),

            # Append the current lora and its value to the string
            chosen_str += f"<lora:{lora['name'].split('.')[0]}:{strength:.2f}>, "

            # Append the trigger words for each lora
            existing_chosen_trigger_words = set(chosen_trigger_words.split(', '))
            chosen_trigger_words = set(lora['trigger_words'].split(', '))
            combined_words = existing_chosen_trigger_words | chosen_trigger_words
            chosen_trigger_words = ', '.join(sorted(combined_words))

        # Find the last occurrence of the comma to remove it
        last_comma_index = chosen_str.rfind(',')
        # Slice the string to remove the last comma and everything after it
        if last_comma_index != -1:
            chosen_str = chosen_str[:last_comma_index]
            
        return (lora_list, chosen_trigger_words.lstrip(", "), chosen_str,)

# Keep your existing advanced class if you want to retain it
class RandomLoraChooserAdvanced:
    @classmethod
    def INPUT_TYPES(cls):
        max_lora_num = 50  # Changed from 20 to 50
        
        inputs = {
            "required": {
                "num_loras": ("INT", {"default": 3, "min": 1, "max": max_lora_num}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "randomize_seed": ("BOOLEAN", {"default": True}),
                "return_full_stack": ("BOOLEAN", {"default": False, "tooltip": "If True, returns input stack + chosen LoRA. If False, returns only chosen LoRA."}),
            },
            "optional": {
                "input_lora_stack": ("LORA_STACK",),
            }
        }
        
        # Add dynamic LoRA inputs
        for i in range(1, max_lora_num + 1):  # Now goes to 51 (50 LoRAs)
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
    
    def choose_random_lora_advanced(self, num_loras, seed, randomize_seed, return_full_stack, input_lora_stack=None, **kwargs):
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
                # Handle both ComfyRoll and standard LoRA stack formats
                if len(lora_data) >= 3:
                    lora_name = lora_data[0]
                    model_weight = lora_data[1]
                    clip_weight = lora_data[2] if len(lora_data) > 2 else model_weight
                    
                    # Skip "None" entries from ComfyRoll stacks
                    if lora_name and lora_name != "None":
                        available_loras.append({
                            "name": lora_name,
                            "trigger": "",  # LoRA stacks don't typically include trigger words
                            "model_weight": model_weight,
                            "clip_weight": clip_weight,
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
        debug_info += f"Return full stack: {return_full_stack}\n"
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
        if return_full_stack and input_lora_stack:
            # Return the original input stack plus the chosen LoRA
            output_stack = []
            # Add original stack (filtering out "None" entries)
            for lora_data in input_lora_stack:
                if len(lora_data) >= 3 and lora_data[0] != "None":
                    output_stack.append(lora_data)
            # Add chosen LoRA
            output_stack.append((chosen_lora["name"], chosen_lora["model_weight"], chosen_lora["clip_weight"]))
        else:
            # Return only the chosen LoRA
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