import random

class RandomLoraChooser:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "num_loras": ("INT", {"default": 1, "min": 1, "max": 5}),
                "lora_1_name": (["None", "loraA", "loraB"],),
                "lora_1_trigger": ("STRING", {"default": "triggerA"}),
                "lora_2_name": (["None", "loraA", "loraB"],),
                "lora_2_trigger": ("STRING", {"default": "triggerB"}),
                "lora_3_name": (["None", "loraA", "loraB"],),
                "lora_3_trigger": ("STRING", {"default": "triggerC"}),
                "lora_4_name": (["None", "loraA", "loraB"],),
                "lora_4_trigger": ("STRING", {"default": "triggerD"}),
                "lora_5_name": (["None", "loraA", "loraB"],),
                "lora_5_trigger": ("STRING", {"default": "triggerE"}),
            }
        }

    RETURN_TYPES = ("LORA_STACK", "STRING", "STRING")
    RETURN_NAMES = ("selected_lora_stack", "selected_lora_name", "selected_lora_trigger")
    FUNCTION = "choose"
    CATEGORY = "LoRA"

    def choose(self, num_loras, **kwargs):
        candidates = []
        for i in range(1, num_loras + 1):
            name = kwargs.get(f"lora_{i}_name", "None")
            trigger = kwargs.get(f"lora_{i}_trigger", "")
            if name and name != "None":
                candidates.append((name, 1.0, trigger))
        if not candidates:
            return ([], "", "")
        selected = random.choice(candidates)
        stack = [(selected[0], 1.0, 1.0)]
        return (stack, selected[0], selected[2])

NODE_CLASS_MAPPINGS = {
    "RandomLoraChooser": RandomLoraChooser,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "RandomLoraChooser": "Random LoRA Chooser",
}
