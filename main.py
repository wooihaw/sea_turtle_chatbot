import ollama
import pyttsx3
import json
import pyaudio
import sys
from vosk import Model, KaldiRecognizer

# --- Configuration ---
VOSK_MODEL_PATH = "vosk-model-small-en-us-0.15"  # Path to the Vosk model directory
MIC_INDEX = None  # Default microphone index. Set to a specific number if needed.
MODEL_NAME = 'llama3' # The Ollama model to use for the conversation
OLLAMA_HOST = 'http://localhost:11434' # Default host for Ollama

def list_microphones():
    """Lists available audio input devices."""
    p = pyaudio.PyAudio()
    print("Available Microphone Devices:")
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if dev['maxInputChannels'] > 0:
            print(f"  {i}: {dev['name']}")
    p.terminate()

def main():
    """Main function to run the voice assistant."""

    # --- Initialization ---
    try:
        # Initialize Text-to-Speech Engine, explicitly using the SAPI5 driver for Windows
        print("Initializing Text-to-Speech engine...")
        engine = pyttsx3.init('sapi5')
        print("TTS engine initialized.")

        # Initialize Vosk Speech-to-Text Model
        print("Initializing Speech-to-Text model...")
        model = Model(VOSK_MODEL_PATH)
        recognizer = KaldiRecognizer(model, 16000)
        print("STT model initialized.")

        # Initialize PyAudio for microphone input
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=16000,
                        input=True,
                        frames_per_buffer=8192,
                        input_device_index=MIC_INDEX)
    except Exception as e:
        print(f"Error during initialization: {e}")
        print("Please ensure that you have downloaded the Vosk model and that all dependencies are installed.")
        sys.exit(1)

    # --- Connect to Ollama ---
    try:
        print(f"Connecting to Ollama at {OLLAMA_HOST}...")
        client = ollama.Client(host=OLLAMA_HOST)
        # A quick check to see if we can list models
        client.list()
        print("Successfully connected to Ollama.")
    except Exception as e:
        print(f"\nError connecting to Ollama: {e}")
        print("Please ensure the Ollama application is running and accessible at the specified host.")
        print("You may also need to check your firewall settings.")
        sys.exit(1)


    print("\n--- Ollama Voice Assistant ---")
    print(f"Using Ollama model: {MODEL_NAME}")
    print("Say 'exit' or 'quit' to end the conversation.")
    engine.say("Ollama voice assistant is ready.")
    engine.runAndWait()


    # --- Main Conversation Loop ---
    try:
        while True:
            print("\nListening...")
            stream.start_stream()
            full_transcript = ""
            
            # This inner loop will now correctly capture a single utterance
            while True:
                data = stream.read(4096, exception_on_overflow=False)
                # AcceptWaveform returns True when a final result is ready
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    transcript = result.get('text', '')
                    
                    # If we got a non-empty transcript, we'll use it and break the inner loop
                    if transcript:
                        full_transcript = transcript
                        break

            stream.stop_stream()


            if full_transcript.strip():
                print(f"You said: {full_transcript.strip()}")

                # Check for exit command
                if any(word in full_transcript.lower() for word in ["exit", "quit"]):
                    print("Exiting...")
                    engine.say("Goodbye!")
                    engine.runAndWait()
                    break

                # --- Get Response from Ollama ---
                try:
                    print("Getting response from Ollama...")
                    response = client.chat(
                        model=MODEL_NAME,
                        messages=[{'role': 'user', 'content': full_transcript.strip()}],
                    )
                    llm_response = response['message']['content']
                    print(f"Ollama: {llm_response}")

                    # --- Speak the Response ---
                    try:
                        print("Attempting to speak the response...")
                        engine.say(llm_response)
                        engine.runAndWait()
                        print("Finished speaking.")
                    except Exception as e_tts:
                        print(f"Error during text-to-speech: {e_tts}")

                except Exception as e:
                    error_message = f"Error communicating with Ollama: {e}"
                    print(error_message)
                    engine.say("Sorry, I'm having trouble connecting to the language model.")
                    engine.runAndWait()

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        # --- Cleanup ---
        stream.close()
        p.terminate()


if __name__ == '__main__':
    # If you are unsure which microphone to use, you can uncomment the following line
    # to list all available microphones.
    # list_microphones()
    main()
