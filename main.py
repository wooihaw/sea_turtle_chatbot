import json

# Offline ASR
from vosk import Model, KaldiRecognizer, SetLogLevel
import pyaudio

# Offline TTS
from TTS.api import TTS
import sounddevice as sd

# Ollama Python client
from ollama import Client

client = Client(host="http://127.0.0.1:11434")

# --- Initialize Vosk speech recognizer ---
SetLogLevel(0)
# vosk_model = Model("vosk-model-en-us-0.22-lgraph")
vosk_model = Model("vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(vosk_model, 16000)

pa = pyaudio.PyAudio()
stream = pa.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    frames_per_buffer=8192
)
stream.start_stream()

# --- Initialize pyttsx3 TTS engine ---
# Download a pretrained model (e.g., "tts_models/en/ljspeech/tacotron2-DDC")
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")

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

def speak(text: str):
    """Speak the given text aloud."""
    # tts_engine.say(text)
    # tts_engine.runAndWait()
    wav = tts.tts(text)
    sd.play(wav, samplerate=tts.synthesizer.output_sample_rate)
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
            model="llama3.2",  # Specify the model to use
            messages=[
                {"role": "system",   "content": "You are a helpful assistant."},
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
