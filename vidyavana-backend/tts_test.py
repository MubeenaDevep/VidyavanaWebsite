import torch
import soundfile as sf

from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer


MODEL_ID = "ai4bharat/indic-parler-tts"

print("Loading model...")

device = "cpu"

model = ParlerTTSForConditionalGeneration.from_pretrained(
    MODEL_ID
).to(device)


# --------------------------------------------------
# TWO DIFFERENT TOKENIZERS
# --------------------------------------------------

# Tokenizer for the actual Indian-language text
text_tokenizer = AutoTokenizer.from_pretrained(
    MODEL_ID
)

# Tokenizer for the voice description
description_tokenizer = AutoTokenizer.from_pretrained(
    "google/flan-t5-large"
)


# --------------------------------------------------
# KANNADA TEXT
# --------------------------------------------------

prompt = "ನಮಸ್ಕಾರ, ವಿದ್ಯಾವನ ಕಂಪ್ಯೂಟರ್ ಶಿಕ್ಷಣ ಸಂಸ್ಥೆಗೆ ಸ್ವಾಗತ."


# --------------------------------------------------
# VOICE DESCRIPTION
# --------------------------------------------------

description = (
    "A clear and natural female voice speaking Kannada. "
    "The speaker speaks at a moderate speed with a friendly tone."
)


# --------------------------------------------------
# TOKENIZE
# --------------------------------------------------

print("Preparing inputs...")

prompt_inputs = text_tokenizer(
    prompt,
    return_tensors="pt",
    padding=True,
)

description_inputs = description_tokenizer(
    description,
    return_tensors="pt",
    padding=True,
)


input_ids = prompt_inputs.input_ids.to(device)
attention_mask = prompt_inputs.attention_mask.to(device)

description_input_ids = description_inputs.input_ids.to(device)
description_attention_mask = description_inputs.attention_mask.to(device)





# --------------------------------------------------
# GENERATE
# --------------------------------------------------

with torch.no_grad():

    generation = model.generate(
         input_ids=description_input_ids,
        attention_mask=description_attention_mask,
        prompt_input_ids=input_ids,
        prompt_attention_mask=attention_mask,
    )


# --------------------------------------------------
# SAVE AUDIO
# --------------------------------------------------

audio = generation.cpu().numpy().squeeze()

output_file = "kannada_test.wav"

sf.write(
    output_file,
    audio,
    model.config.sampling_rate,
)


print()
print("======================================")
print("SUCCESS!")
print("Created:", output_file)
print("======================================")