import os
import base64
import json
import urllib.request
import urllib.error

# Default to llava for Vision Language capabilities
# For CPU environments, moondream (1.8b) or llava (7b) are ideal.
VLM_MODEL = "llava"
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# T018: Inference Optimization
# Leave at least 1 core for the UI to remain responsive during heavy generation
NUM_THREADS = max(1, os.cpu_count() - 1) if os.cpu_count() else 4

def encode_image(image_path: str) -> str:
    """Encodes an image to a base64 string."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_clinical_data_from_image(image_path: str) -> str:
    """
    Sends an image (prescription or lab report) to the local Ollama VLM
    to extract clinical metrics.
    """
    base64_image = encode_image(image_path)

    prompt = (
        "You are a clinical data extraction assistant. "
        "Analyze the provided medical image (lab report or prescription). "
        "Extract all quantitative metrics (like Blood Pressure, Glucose, HDL, LDL) "
        "and any prescribed medications with their dosages. "
        "Return the extracted data clearly. Do not invent information."
    )

    payload = {
        "model": VLM_MODEL,
        "prompt": prompt,
        "images": [base64_image],
        "stream": False,
        "options": {
            "temperature": 0.0,
            "num_predict": 500,
            "num_thread": NUM_THREADS,
            "num_ctx": 2048  # Cap context to prevent memory ballooning
        }
    }

    req = urllib.request.Request(
        OLLAMA_API_URL, 
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )

    try:
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode('utf-8'))
        return result.get("response", "").strip()
    except urllib.error.URLError as e:
        raise RuntimeError(f"Failed to communicate with local Ollama VLM: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
        print(f"Extracting data from {img_path} using local VLM...")
        try:
            extracted_text = extract_clinical_data_from_image(img_path)
            print("\n--- EXTRACTED CLINICAL DATA ---")
            print(extracted_text)
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Usage: python extractor.py <path_to_image>")
