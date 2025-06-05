import json
import os
import folder_paths
from typing import Dict, List, Tuple, Any


class SimpleCharacterLoop:
    """
    Simple character looper - just increments through all characters
    Now returns LORA_STACK in the same format as CR_LoRAStack
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()
        json_files = []
        if os.path.exists(input_dir):
            json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]
        
        if not json_files:
            json_files = ["No JSON files found"]
            
        return {
            "required": {
                "json_file": (json_files,),
                "loop_count": ("INT", {"default": 0, "min": 0, "max": 10000, "step": 1, 
                              "tooltip": "Increment this to go to next character"}),
            },
            "optional": {
                "lora_stack": ("LORA_STACK",),
            }
        }
    
    RETURN_TYPES = ("STRING", "LORA_STACK", "STRING", "STRING")
    RETURN_NAMES = ("character_prompt", "lora_stack", "character_name", "loop_info")
    
    FUNCTION = "loop_character"
    CATEGORY = "Character Loader"
    
    def loop_character(self, json_file, loop_count, lora_stack=None):
        
        if json_file == "No JSON files found":
            return ("Error: No JSON files found", [], "Error", "No JSON files in input directory")
        
        try:
            # Load JSON data
            json_path = os.path.join(folder_paths.get_input_directory(), json_file)
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            characters = data.get('characters', [])
            if not characters:
                return ("Error: No characters found", [], "Error", "No characters in JSON")
            
            total_characters = len(characters)
            current_index = loop_count % total_characters
            
            character = characters[current_index]
            base_style = data.get('base_style', {})
            
            # Build prompt
            prompt_parts = []
            if base_style.get('prompt'):
                prompt_parts.append(base_style['prompt'].strip())
            if character.get('prompt'):
                prompt_parts.append(character['prompt'].strip())
            
            combined_prompt = ', '.join(filter(None, prompt_parts))
            
            # Build LoRA stack - Initialize the list (same as CR_LoRAStack)
            lora_list = list()
            
            # Add incoming LoRA stack if provided (same logic as CR_LoRAStack)
            if lora_stack is not None:
                lora_list.extend([l for l in lora_stack if l[0] != "None"])
            
            # Add style LoRA
            style_lora = base_style.get('style_lora')
            if style_lora and style_lora != "None":
                style_strength = base_style.get('style_strength', 1.0)
                # Format: (lora_name, model_weight, clip_weight) - same as CR_LoRAStack
                lora_list.extend([(style_lora, style_strength, style_strength)])
            
            # Add character LoRA
            char_lora = character.get('lora')
            if char_lora and char_lora != "None":
                char_strength = character.get('lora_strength', 1.0)
                # Format: (lora_name, model_weight, clip_weight) - same as CR_LoRAStack
                lora_list.extend([(char_lora, char_strength, char_strength)])
            
            # Add additional character LoRAs
            additional_loras = character.get('additional_loras', [])
            for lora_data in additional_loras:
                if isinstance(lora_data, dict):
                    lora_name = lora_data.get('name')
                    if lora_name and lora_name != "None":
                        model_strength = lora_data.get('model_strength', 1.0)
                        clip_strength = lora_data.get('clip_strength', 1.0)
                        # Format: (lora_name, model_weight, clip_weight) - same as CR_LoRAStack
                        lora_list.extend([(lora_name, model_strength, clip_strength)])
            
            character_name = character.get('name', f'Character_{current_index}')
            
            loop_info = f"Character {current_index + 1} of {total_characters}: {character_name}"
            
            # Return lora_list (not lora_stack) to match CR_LoRAStack format
            return (combined_prompt, lora_list, character_name, loop_info)
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            # Return empty list for lora_stack on error
            return (error_msg, [], "Error", error_msg)
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # Force re-execution when loop_count changes
        return kwargs.get("loop_count", 0)