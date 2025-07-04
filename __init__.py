from .nodes.random_lora_chooser import RandomizeLoras, RandomizeLorasStack, RandomLoraChooserAdvanced
from .nodes.character_batch_loader import SimpleCharacterLoop
from .nodes.video_index_loader import SimpleVideoIndexLoader, SimpleVideoLoop
from .nodes.multi_character_randomizer import MultiCharacterRandomizer, MultiCharacterMixer

NODE_CLASS_MAPPINGS = {
    "RandomizeLoras": RandomizeLoras,
    "RandomizeLorasStack": RandomizeLorasStack,
    "RandomLoraChooserAdvanced": RandomLoraChooserAdvanced,
    "SimpleCharacterLoop": SimpleCharacterLoop,
    "SimpleVideoIndexLoader": SimpleVideoIndexLoader,
    "SimpleVideoLoop": SimpleVideoLoop,
    "MultiCharacterRandomizer": MultiCharacterRandomizer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RandomizeLoras": "Randomize LoRAs",
    "RandomizeLorasStack": "Randomize LoRAs Stack",
    "RandomLoraChooserAdvanced": "Random LoRA Chooser (Advanced)",
    "SimpleCharacterLoop": "Simple Character Loop",
    "SimpleVideoIndexLoader": "Simple Video Index Loader",
    "SimpleVideoLoop": "Simple Video Loop",
    "MultiCharacterRandomizer": "Multi Character Randomizer",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']