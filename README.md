# Guideline to setup and run the script

This repository provides an offline voice-based chatbot. 
It uses a locally hosted LLM via Ollama, Vosk for speech recognition, and Coqui TTS for speech synthesis. 
The environment and dependencies are managed by **uv**.

## Installation

### 1. Install uv
```bash
python3 -m pip install uv
```
Alternatively, using pipx:
```bash
pipx install uv
```

### 2. Install Ollama and Pull an LLM
1. Install the Ollama CLI following the official guide.  
2. Start the Ollama daemon:
   ```bash
   ollama serve
   ```
3. Pull your chosen model (e.g., Llama3):
   ```bash
   ollama pull llama3.2:1b
   ```

### 3. Download and Unpack the Vosk Model
1. Download (for example) `vosk-model-small-en-us-0.15`:
   ```bash
   wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
   ```
2. Unpack locally:
   ```bash
   unzip vosk-model-small-en-us-0.15.zip -d vosk-model-small-en-us-0.15
   ```
3. Ensure the script points to the `vosk-model-small-en-us-0.15` folder.

## Usage

Run the chatbot with uv:
```bash
uv run main.py
```
Speak naturally. The assistant will reply in speech and text.

## Notes

- On first launch, Coqui TTS will download its model (e.g., `tts_models/en/ljspeech/tacotron2-DDC`).
- After that, all speech synthesis occurs offline.

