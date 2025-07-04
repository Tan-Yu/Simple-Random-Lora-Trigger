import json
import os
import random
import folder_paths
from typing import Dict, List, Tuple, Any


class MultiCharacterRandomizer:
    """
    Multi-character randomizer - randomly selects N characters and outputs prompts separately
    Returns base prompt, individual character prompts, combined prompt, and LoRA stack
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
                "num_characters": ("INT", {"default": 2, "min": 1, "max": 10, "step": 1, 
                                  "tooltip": "Number of characters to randomly select and combine"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff,
                               "tooltip": "Seed for random character selection"}),
                "randomize_seed": ("BOOLEAN", {"default": True,
                                             "tooltip": "If True, uses random seed each time"}),
                "allow_duplicates": ("BOOLEAN", {"default": False,
                                                "tooltip": "If True, allows selecting the same character multiple times"}),
                "character_separator": ("STRING", {"default": ", ", "multiline": False,
                                                  "tooltip": "Separator between character prompts in combined output"}),
            },
            "optional": {
                "lora_stack": ("LORA_STACK",),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "LORA_STACK", "STRING", "STRING")
    RETURN_NAMES = ("base_prompt", "char1_prompt", "char2_prompt", "char3_prompt", "combined_prompt", "lora_stack", "selected_characters", "debug_info")
    
    FUNCTION = "randomize_characters"
    CATEGORY = "Character Loader"
    
    def randomize_characters(self, json_file, num_characters, seed, randomize_seed, 
                           allow_duplicates, character_separator, lora_stack=None):
        
        if json_file == "No JSON files found":
            return ("Error: No JSON files found", "", "", "", "Error", [], "Error", "No JSON files in input directory")
        
        try:
            # Set random seed
            if randomize_seed:
                random.seed()
            else:
                random.seed(seed)
            
            # Load JSON data
            json_path = os.path.join(folder_paths.get_input_directory(), json_file)
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            characters = data.get('characters', [])
            if not characters:
                return ("Error: No characters found", "", "", "", "Error", [], "Error", "No characters in JSON")
            
            base_style = data.get('base_style', {})
            
            # Limit num_characters to available characters if duplicates not allowed
            if not allow_duplicates:
                num_characters = min(num_characters, len(characters))
            
            # Select random characters
            if allow_duplicates:
                selected_characters = random.choices(characters, k=num_characters)
            else:
                selected_characters = random.sample(characters, num_characters)
            
            # Get base prompt
            base_prompt = base_style.get('prompt', '').strip()
            
            # Get individual character prompts (up to 3 for the outputs)
            char_prompts = ["", "", ""]  # Initialize with empty strings
            character_prompt_parts = []
            
            for i, character in enumerate(selected_characters):
                char_prompt = character.get('prompt', '').strip()
                character_prompt_parts.append(char_prompt)
                
                # Store in individual outputs (up to 3)
                if i < 3:
                    char_prompts[i] = char_prompt
            
            # Build combined prompt
            prompt_parts = []
            
            # Add base style prompt first
            if base_prompt:
                prompt_parts.append(base_prompt)
            
            # Add character prompts
            if character_prompt_parts:
                combined_character_prompt = character_separator.join(filter(None, character_prompt_parts))
                if combined_character_prompt:
                    prompt_parts.append(combined_character_prompt)
            
            combined_prompt = ', '.join(filter(None, prompt_parts))
            
            # Build LoRA stack - Initialize the list (same as CR_LoRAStack)
            lora_list = list()
            
            # Add incoming LoRA stack if provided
            if lora_stack is not None:
                lora_list.extend([l for l in lora_stack if l[0] != "None"])
            
            # Add style LoRA
            style_lora = base_style.get('style_lora')
            if style_lora and style_lora != "None":
                style_strength = base_style.get('style_strength', 1.0)
                lora_list.extend([(style_lora, style_strength, style_strength)])
            
            # Add character LoRAs for all selected characters
            for character in selected_characters:
                char_lora = character.get('lora')
                if char_lora and char_lora != "None":
                    char_strength = character.get('lora_strength', 1.0)
                    # Check for duplicates in lora_list to avoid adding the same LoRA multiple times
                    if not any(lora[0] == char_lora for lora in lora_list):
                        lora_list.extend([(char_lora, char_strength, char_strength)])
                
                # Add additional character LoRAs
                additional_loras = character.get('additional_loras', [])
                for lora_data in additional_loras:
                    if isinstance(lora_data, dict):
                        lora_name = lora_data.get('name')
                        if lora_name and lora_name != "None":
                            model_strength = lora_data.get('model_strength', 1.0)
                            clip_strength = lora_data.get('clip_strength', 1.0)
                            # Check for duplicates
                            if not any(lora[0] == lora_name for lora in lora_list):
                                lora_list.extend([(lora_name, model_strength, clip_strength)])
            
            # Generate output strings
            selected_character_names = [char.get('name', 'Unnamed') for char in selected_characters]
            selected_characters_str = ', '.join(selected_character_names)
            
            # Debug information
            debug_info = f"Selected {len(selected_characters)} characters:\n"
            debug_info += f"Characters: {selected_characters_str}\n"
            debug_info += f"Base prompt: {base_prompt}\n"
            for i, char_prompt in enumerate(char_prompts):
                if i < len(selected_characters):
                    debug_info += f"Char{i+1} prompt: {char_prompt}\n"
            debug_info += f"Allow duplicates: {allow_duplicates}\n"
            debug_info += f"Seed: {seed} (randomized: {randomize_seed})\n"
            debug_info += f"Total LoRAs in stack: {len(lora_list)}"
            
            return (base_prompt, char_prompts[0], char_prompts[1], char_prompts[2], 
                   combined_prompt, lora_list, selected_characters_str, debug_info)
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            return (error_msg, "", "", "", "Error", [], "Error", error_msg)
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # Force re-execution when randomize_seed is True or when other parameters change
        if kwargs.get("randomize_seed", False):
            return float("NaN")
        return (kwargs.get("seed", 0), kwargs.get("num_characters", 2), kwargs.get("allow_duplicates", False))


class MultiCharacterMixer:
    """
    Alternative version that can handle more than 3 characters by outputting them as a list
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
                "num_characters": ("INT", {"default": 2, "min": 1, "max": 10, "step": 1, 
                                  "tooltip": "Number of characters to randomly select and combine"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff,
                               "tooltip": "Seed for random character selection"}),
                "randomize_seed": ("BOOLEAN", {"default": True,
                                             "tooltip": "If True, uses random seed each time"}),
                "allow_duplicates": ("BOOLEAN", {"default": False,
                                                "tooltip": "If True, allows selecting the same character multiple times"}),
            },
            "optional": {
                "lora_stack": ("LORA_STACK",),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "LORA_STACK", "STRING", "STRING")
    RETURN_NAMES = ("base_prompt", "all_character_prompts", "lora_stack", "selected_characters", "debug_info")
    
    FUNCTION = "mix_characters"
    CATEGORY = "Character Loader"
    
    def mix_characters(self, json_file, num_characters, seed, randomize_seed, 
                      allow_duplicates, lora_stack=None):
        
        if json_file == "No JSON files found":
            return ("Error: No JSON files found", "Error", [], "Error", "No JSON files in input directory")
        
        try:
            # Set random seed
            if randomize_seed:
                random.seed()
            else:
                random.seed(seed)
            
            # Load JSON data
            json_path = os.path.join(folder_paths.get_input_directory(), json_file)
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            characters = data.get('characters', [])
            if not characters:
                return ("Error: No characters found", "Error", [], "Error", "No characters in JSON")
            
            base_style = data.get('base_style', {})
            
            # Limit num_characters to available characters if duplicates not allowed
            if not allow_duplicates:
                num_characters = min(num_characters, len(characters))
            
            # Select random characters
            if allow_duplicates:
                selected_characters = random.choices(characters, k=num_characters)
            else:
                selected_characters = random.sample(characters, num_characters)
            
            # Get base prompt
            base_prompt = base_style.get('prompt', '').strip()
            
            # Get all character prompts as individual lines
            character_prompts_lines = []
            for i, character in enumerate(selected_characters):
                char_name = character.get('name', f'Character_{i+1}')
                char_prompt = character.get('prompt', '').strip()
                if char_prompt:
                    character_prompts_lines.append(f"{char_name}: {char_prompt}")
                else:
                    character_prompts_lines.append(f"{char_name}: [No prompt]")
            
            all_character_prompts = '\n'.join(character_prompts_lines)
            
            # Build LoRA stack
            lora_list = list()
            
            # Add incoming LoRA stack if provided
            if lora_stack is not None:
                lora_list.extend([l for l in lora_stack if l[0] != "None"])
            
            # Add style LoRA
            style_lora = base_style.get('style_lora')
            if style_lora and style_lora != "None":
                style_strength = base_style.get('style_strength', 1.0)
                lora_list.extend([(style_lora, style_strength, style_strength)])
            
            # Add character LoRAs for all selected characters
            for character in selected_characters:
                char_lora = character.get('lora')
                if char_lora and char_lora != "None":
                    char_strength = character.get('lora_strength', 1.0)
                    # Check for duplicates in lora_list to avoid adding the same LoRA multiple times
                    if not any(lora[0] == char_lora for lora in lora_list):
                        lora_list.extend([(char_lora, char_strength, char_strength)])
                
                # Add additional character LoRAs
                additional_loras = character.get('additional_loras', [])
                for lora_data in additional_loras:
                    if isinstance(lora_data, dict):
                        lora_name = lora_data.get('name')
                        if lora_name and lora_name != "None":
                            model_strength = lora_data.get('model_strength', 1.0)
                            clip_strength = lora_data.get('clip_strength', 1.0)
                            # Check for duplicates
                            if not any(lora[0] == lora_name for lora in lora_list):
                                lora_list.extend([(lora_name, model_strength, clip_strength)])
            
            # Generate output strings
            selected_character_names = [char.get('name', 'Unnamed') for char in selected_characters]
            selected_characters_str = ', '.join(selected_character_names)
            
            # Debug information
            debug_info = f"Selected {len(selected_characters)} characters:\n"
            debug_info += f"Characters: {selected_characters_str}\n"
            debug_info += f"Base prompt: {base_prompt}\n"
            debug_info += f"Allow duplicates: {allow_duplicates}\n"
            debug_info += f"Seed: {seed} (randomized: {randomize_seed})\n"
            debug_info += f"Total LoRAs in stack: {len(lora_list)}"
            
            return (base_prompt, all_character_prompts, lora_list, selected_characters_str, debug_info)
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            return (error_msg, "Error", [], "Error", error_msg)
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # Force re-execution when randomize_seed is True or when other parameters change
        if kwargs.get("randomize_seed", False):
            return float("NaN")
        return (kwargs.get("seed", 0), kwargs.get("num_characters", 2), kwargs.get("allow_duplicates", False))