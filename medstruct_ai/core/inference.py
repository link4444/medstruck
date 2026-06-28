import json
import urllib.request
import urllib.error
import logging
from pydantic import ValidationError

from medstruct_ai.core.schemas import ClinicalInsight

logger = logging.getLogger(__name__)

OLLAMA_API_URL = "http://localhost:11434/api/generate"
# We use the medstruct-qwen model we configured in T001
MODEL = "medstruct-qwen"

def generate_structured_clinical_insight(text_input: str, max_retries: int = 3) -> ClinicalInsight:
    """
    Passes raw unstructured clinical text to the local LLM and forces it to
    output a JSON structure that strictly matches the ClinicalInsight Pydantic schema.
    Implements retry logic if the output is invalid.
    """
    
    schema_definition = json.dumps(ClinicalInsight.model_json_schema(), indent=2)
    
    base_prompt = (
        "You are a clinical data extraction assistant. "
        "Extract the information from the following clinical note and format it EXACTLY as a JSON object "
        "that validates against this JSON schema:\n\n"
        f"{schema_definition}\n\n"
        "Here is the raw clinical note:\n"
        f"{text_input}\n\n"
        "Output ONLY valid JSON. No markdown, no explanations, no text outside the JSON object."
    )
    
    current_prompt = base_prompt
    
    for attempt in range(1, max_retries + 1):
        payload = {
            "model": MODEL,
            "prompt": current_prompt,
            "stream": False,
            "format": "json", # Ollama native JSON mode
            "options": {
                "temperature": 0.0,
                "num_predict": 1000
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
            llm_output = result.get("response", "").strip()
            
            # Attempt to parse into our Pydantic model
            insight = ClinicalInsight.model_validate_json(llm_output)
            return insight
            
        except urllib.error.URLError as e:
            raise RuntimeError(f"Failed to communicate with local Ollama: {e}")
            
        except ValidationError as e:
            logger.warning(f"Attempt {attempt} failed validation: {e}")
            if attempt == max_retries:
                raise RuntimeError(f"LLM failed to produce valid schema after {max_retries} attempts.")
            
            # Retry logic: feedback the exact Pydantic error to the LLM
            current_prompt = (
                f"{base_prompt}\n\n"
                f"Your previous output was invalid JSON or did not match the schema.\n"
                f"Validation errors encountered:\n{str(e)}\n"
                f"Please fix the errors and provide ONLY the corrected JSON object."
            )
        
        except json.JSONDecodeError as e:
            logger.warning(f"Attempt {attempt} produced invalid JSON: {e}")
            if attempt == max_retries:
                raise RuntimeError(f"LLM failed to produce valid JSON after {max_retries} attempts.")
            
            current_prompt = (
                f"{base_prompt}\n\n"
                f"Your previous output was not valid JSON. Error: {str(e)}\n"
                f"Please provide ONLY a valid JSON object."
            )

    raise RuntimeError("Unexpected failure in structured generation.")

if __name__ == "__main__":
    # Quick Test
    sample_note = "Patient visited on 2023-10-25. Diagnosed with hypertension. Prescribed Lisinopril 10mg. Blood pressure was 130/85."
    print("Testing LLM Structural Constraint Logic...\n")
    try:
        parsed_insight = generate_structured_clinical_insight(sample_note)
        print("Success! Extracted Pydantic Object:")
        print(parsed_insight.model_dump_json(indent=2))
    except Exception as e:
        print(f"Test Failed: {e}")
