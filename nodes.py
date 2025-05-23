import random
import folder_paths
from comfy.sd import load_lora_for_models
import comfy.utils

class RandomLORALoader:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL",),
                "clip": ("CLIP",),
                "num_loras": ("INT", {"default": 1, "min": 1, "max": 10, "step": 1}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {"lora_stack": ("LORA_STACK",)}
        }

    RETURN_TYPES = ("MODEL", "CLIP", "STRING", "LORA_STACK")
    RETURN_NAMES = ("model", "clip", "trigger_word", "lora_stack")
    FUNCTION = "load_random_lora"
    CATEGORY = "EasyUse/Loaders"

    def load_random_lora(self, model, clip, num_loras, seed, lora_stack=None, **kwargs):
        current_loras = []
        
        # Get from existing stack
        if lora_stack:
            current_loras.extend(lora_stack)
            
        # Get from dynamic inputs
        for i in range(1, num_loras + 1):
            lora_name = kwargs.get(f"lora_name_{i}", "")
            if not lora_name or lora_name == "None":
                continue
                
            strength = kwargs.get(f"lora_strength_{i}", 1.0)
            trigger = kwargs.get(f"trigger_word_{i}", "")
            current_loras.append((lora_name, strength, strength, trigger))

        if not current_loras:
            return (model, clip, "", [])

        # Random selection
        random.seed(seed)
        selected = random.choice(current_loras)
        lora_name, model_str, clip_str, trigger = selected

        # Load LORA
        lora_path = folder_paths.get_full_path("loras", lora_name)
        lora = comfy.utils.load_torch_file(lora_path, safe_load=True)
        model_lora, clip_lora = load_lora_for_models(model, clip, lora, model_str, clip_str)

        # Create output stack
        output_stack = [(lora_name, model_str, clip_str, trigger)]

        return (model_lora, clip_lora, trigger, output_stack)

NODE_CLASS_MAPPINGS = {"RandomLORALoader": RandomLORALoader}
NODE_DISPLAY_NAME_MAPPINGS = {"RandomLORALoader": "Random LORA Loader"}