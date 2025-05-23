from .nodes.random_lora_chooser import RandomLoraChooser

NODE_CLASS_MAPPINGS = {
    "RandomLoraChooser": RandomLoraChooser,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RandomLoraChooser": "Random LoRA Chooser",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']