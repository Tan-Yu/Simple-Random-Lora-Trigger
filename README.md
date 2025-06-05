# Example of Characters.json (put in ComfyUI/inputs)


{
  "base_style": {
    "prompt": "masterpiece, best quality, highly detailed",
    "style_lora": "anime_style.safetensors",
    "style_strength": 1.0
  },
  "characters": [
    {
      "name": "Alice",
      "prompt": "alice, blonde hair, blue eyes, school uniform",
      "lora": "alice_character.safetensors",
      "lora_strength": 0.8
    },
    {
      "name": "Bob",
      "prompt": "bob, brown hair, green eyes, casual clothes",
      "lora": "bob_character.safetensors", 
      "lora_strength": 0.7
    },
    {
      "name": "Carol",
      "prompt": "carol, red hair, hazel eyes, business suit",
      "lora": "carol_character.safetensors",
      "lora_strength": 0.9,
      "additional_loras": [
        {
          "name": "business_attire.safetensors",
          "model_strength": 0.5,
          "clip_strength": 0.5
        }
      ]
    }
  ]
}