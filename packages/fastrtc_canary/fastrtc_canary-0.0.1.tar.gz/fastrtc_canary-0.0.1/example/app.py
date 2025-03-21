from fastrtc_canary import get_stt_model as get_stt_model_canary
from fastrtc import (ReplyOnPause, Stream, get_tts_model, list_stt_models)
from groq import Groq

print(f"Available STT models: {list_stt_models()}")  
# Available STT models: ['moonshine/base', 'moonshine/tiny', 'canary/1b']

client = Groq()
stt_model = get_stt_model_canary(
                        "canary/1b",
                        lang="en"  # Optional, defaults to "en"
                    )
tts_model = get_tts_model()

def echo(audio):
    prompt = stt_model.stt(audio)

    response = (
        client.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=200,
            messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
        )
        .choices[0]
        .message.content
    )

    for audio_chunk in tts_model.stream_tts_sync(response):
        yield audio_chunk

stream = Stream(ReplyOnPause(echo), modality="audio", mode="send-receive")

stream.ui.launch()