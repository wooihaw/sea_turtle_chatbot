import json
import subprocess
import threading

# Offline ASR
from vosk import Model, KaldiRecognizer, SetLogLevel
import pyaudio

# Offline TTS
from kittentts import KittenTTS

# sounddevice for audio playback
import sounddevice as sd

# Ollama Python client
from ollama import Client

client = Client(host="http://127.0.0.1:11434")

# --- Initialize Vosk speech recognizer ---
SetLogLevel(0)
vosk_model = Model("vosk-model-en-us-0.22-lgraph")
recognizer = KaldiRecognizer(vosk_model, 16000)

# --- Initialize KittenTTS model ---
ktts = KittenTTS("KittenML/kitten-tts-nano-0.1")

pa = pyaudio.PyAudio()
stream = pa.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    frames_per_buffer=8192
)
stream.start_stream()

# --- Functions for speech recognition---
def listen_and_recognize():
    """Capture audio from microphone and return transcribed text."""
    print("Listening…")
    while True:
        data = stream.read(4096, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").strip()
            if text:
                return text

# --- Functions for TTS ---
def speak(text: str):
    """Speak the given text aloud."""
    wav = ktts.generate(text + "...", voice='expr-voice-2-f')
    sd.play(wav, samplerate=24000)
    sd.wait()

def converse():
    """Main loop: listen, query LLM, and speak the response."""
    print("You may start speaking. Say 'exit' to quit.")
    history = []  # Optional: maintain conversation history
    while True:
        user_text = listen_and_recognize()
        print(f"You said: {user_text}")
        if user_text.lower() in {"exit", "quit"}:
            speak("Goodbye.")
            break

        # Call Ollama locally
        response = client.chat(
            model="sea_turtle_llama3_1_8b_q4_k_m",  # Specify the model to use
            messages=[
                {"role": "system",   "content": "You are a highly factual and accurate AI assistant for anything related to sea turtles. Do not invent information or speculate. If information is not available, indicate that. Always respond with single-sentence answer with not more than 30 words."},
                *history,
                {"role": "user",     "content": user_text},
            ],
            options={"temperature": 0.2},
        )
        reply = response.message.content
        print(f"Assistant: {reply}")

        # Speak the reply
        speak(reply)

        # Update history (optional)
        history.append({"role": "user",   "content": user_text})
        history.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    try:
        converse()
    except KeyboardInterrupt:
        print("\nSession terminated.")
        stream.stop_stream()
        stream.close()
        pa.terminate()
