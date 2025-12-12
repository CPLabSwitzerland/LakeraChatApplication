import requests
import json
from utils.logger_setup import getlogger

# Set up a dedicated logger for this module
logger = getlogger("llm")

# Configuration constants
LLAMA_API_URL = "http://ai-llm-01:8081/v1/completions"  # TinyLlama API endpoint
MAX_TOKENS = 250
N_CTX = 2048
TEMPERATURE = 0.1
MODEL_NAME = "tinylama-rust-q4_k_m.gguf"
STOP_SEQUENCE = "\n"

class LLM:
    """
    Single LLM class for LakeraApplication.
    Streams responses from TinyLlama API.
    """

    def build_prompt(self, question: str) -> str:
        return (
            "\nYou are a helpful assistant.\n"
            "Answer the following question in **one sentence only**.\n"
            "Do not add extra text, do not repeat the question, and do not generate any new questions.\n\n"
            f"Question: {question}\n"
            "Answer:"
        )

    def stream(self, prompt: str):
        full_prompt = self.build_prompt(prompt)
        logger.info(f"[LLM] Sending prompt ({len(full_prompt)} chars): {full_prompt!r}")

        payload = {
            "model": MODEL_NAME,
            "prompt": full_prompt,
            "max_tokens": MAX_TOKENS,
            "n_ctx": N_CTX,
            "temperature": TEMPERATURE,
            "stop": STOP_SEQUENCE,
            "stream": True
        }

        assistant_response = ""

        try:
            with requests.post(LLAMA_API_URL, json=payload, stream=True) as response:
                response.raise_for_status()

                for line in response.iter_lines(decode_unicode=True):
                    if not line or line.strip() == "[DONE]":
                        continue

                    if line.startswith("data: "):
                        data_str = line[len("data: "):]
                        try:
                            data_json = json.loads(data_str)
                            for choice in data_json.get("choices", []):
                                text = choice.get("text", "")
                                if text:
                                    if STOP_SEQUENCE in text:
                                        text = text.split(STOP_SEQUENCE)[0]
                                        assistant_response += text
                                        logger.info(f"[LLM] chunk (stopped): {text!r}")
                                        yield text
                                        logger.info(f"[LLM] Streaming finished.")
                                        return
                                    assistant_response += text
                                    logger.info(f"[LLM] chunk: {text!r}")
                                    yield text
                        except json.JSONDecodeError:
                            logger.warning(f"[LLM] Could not parse JSON: {data_str!r}")

        except requests.RequestException as e:
            logger.error(f"[LLM] Request failed: {e}")

        if assistant_response:
            logger.info(f"[LLM] Full assistant response: {assistant_response!r}")
