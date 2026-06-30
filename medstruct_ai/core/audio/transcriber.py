import subprocess
import os
import shutil

# Resolve absolute paths based on the location of this script
BASE_DIR = os.path.dirname(__file__)
WHISPER_DIR = os.path.join(BASE_DIR, "whisper.cpp")
WHISPER_CLI = os.path.join(WHISPER_DIR, "build", "bin", "whisper-cli")
MODEL_PATH = os.path.join(WHISPER_DIR, "models", "ggml-base.en.bin")

def transcribe_audio(file_path: str) -> str:
    """
    Transcribe a given audio file using local whisper.cpp engine.
    NOTE: whisper.cpp requires 16kHz WAV files.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")
        
    if not os.path.exists(WHISPER_CLI):
        raise RuntimeError(f"whisper-cli not found at {WHISPER_CLI}. Did T002 compile successfully?")

    if not os.path.exists(MODEL_PATH):
        raise RuntimeError(f"Whisper model not found at {MODEL_PATH}.")

    # -otxt forces whisper to write the pure transcription to a .txt file
    # -nt removes timestamps so we just get raw paragraphs
    cmd = [
        WHISPER_CLI,
        "-m", MODEL_PATH,
        "-f", file_path,
        "-nt",
        "-otxt"
    ]
    
    # Run the command
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"Whisper transcription failed with exit code {result.returncode}:\n{result.stderr}")
        
    # Whisper creates a file named {original_file}.txt
    output_txt_file = f"{file_path}.txt"
    
    if not os.path.exists(output_txt_file):
        # Fallback to stdout if the file wasn't generated for some reason
        return result.stdout.strip()
        
    # Read the transcribed text
    with open(output_txt_file, 'r', encoding='utf-8') as f:
        transcription = f.read().strip()
        
    # Clean up the temporary txt file
    os.remove(output_txt_file)
    
    return transcription

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        text = transcribe_audio(sys.argv[1])
        print("\n--- TRANSCRIPTION ---")
        print(text)
    else:
        print("Usage: python transcriber.py <path_to_wav_file>")
