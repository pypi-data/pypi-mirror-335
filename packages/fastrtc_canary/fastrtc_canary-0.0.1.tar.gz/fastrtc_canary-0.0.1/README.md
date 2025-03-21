<div style='text-align: center; margin-bottom: 1rem; display: flex; justify-content: center; align-items: center;'>
    <h1 style='color: white; margin: 0;'>FastRTC Canary</h1>
    <img src='https://huggingface.co/datasets/freddyaboulton/bucket/resolve/main/fastrtc_logo_small.png'
         alt="FastRTC Logo" 
         style="margin-right: 10px;">
</div>

<div style="display: flex; flex-direction: row; justify-content: center">
<img style="display: block; padding-right: 5px; height: 20px;" alt="Static Badge" src="https://img.shields.io/pypi/v/fastrtc_canary"> 
<a href="https://github.com/mahimairaja/fastrtc_canary" target="_blank"><img alt="Static Badge" src="https://img.shields.io/badge/github-white?logo=github&logoColor=black"></a>
</div>

<h3 style='text-align: center'>
The Real-Time Communication Library for Python with Canary STT
</h3>

Turn any python function into a real-time audio and video stream over WebRTC or WebSockets.

## Installation

### Assume you have fastrtc installed - [fastrtc](https://github.com/freddyaboulton/fastrtc)

```bash
pip install fastrtc_canary
```


## Features

- 🎯 Direct integration with Nvidia's Canary STT model
- 🔄 Seamless compatibility with all FastRTC features
- 🚀 Real-time audio transcription
- 🔌 Drop-in replacement for FastRTC's STT components

## Quick Start

```python
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
```

## Requirements

- Python >= 3.10
- FastRTC >= 0.0.14
- Groq >= 0.20.0

## Documentation

For more detailed information about the base FastRTC package, visit [https://fastrtc.org](https://fastrtc.org)

## License

MIT

