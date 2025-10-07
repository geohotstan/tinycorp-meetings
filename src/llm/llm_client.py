import os
import re
import dotenv
import requests

class LLMClient:
    def __init__(self):
        dotenv.load_dotenv()
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in .env file")
        self.base_url = "https://openrouter.ai/api/v1"

    def call_llm(self, model_name: str, messages: list):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model_name,
            "messages": messages
        }
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"Request failed: {e}")

        try:
            response_json = response.json()
            if "choices" in response_json and response_json["choices"]:
                first_choice = response_json["choices"][0]
                if "message" in first_choice and "content" in first_choice["message"]:
                    return first_choice["message"]["content"]
            raise Exception("Unexpected response format from API")
        except ValueError: # Catches json.JSONDecodeError if response is not valid JSON
            raise Exception("Failed to parse response JSON from API")
        except Exception as e: # Catches other exceptions, including the one raised above
            raise Exception(f"Error processing API response: {e}")

    def _parse_markdown(self, text: str) -> str:
        # The pattern looks for a markdown code block and captures the content inside.
        # It handles optional language specifiers (like 'md' or 'markdown') and is case-insensitive.
        pattern = r"```(?:md|markdown)?\s*\n(.*?)\n```"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return text.strip()

    def get_llm_highlights(self, readme_content: str, highlights_prompt: str) -> str:
        prompt = f"{readme_content}\n\n{highlights_prompt}"
        messages = [{"role": "user", "content": prompt}]
        # TODO update to better free models
        response = self.call_llm("deepseek/deepseek-chat-v3.1:free", messages)
        return self._parse_markdown(response)

if __name__ == "__main__":
    try:
        client = LLMClient()
        model_name = "deepseek/deepseek-r1-0528:free"

        # Example 1: Simple user prompt
        messages_1 = [{"role": "user", "content": "What is the capital of France?"}]
        response_1 = client.call_llm(model_name, messages_1)
        print(f"LLM Response (simple prompt):\n{response_1}")

        # Example 2: User prompt with a system message
        messages_2 = [
            {"role": "system", "content": "You are a helpful assistant that always responds in French."},
            {"role": "user", "content": "What is the capital of France?"}
        ]
        response_2 = client.call_llm(model_name, messages_2)
        print(f"\nLLM Response (with system prompt 'Always respond in French'):\n{response_2}")

    except ValueError as e:
        print(f"Configuration Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Network Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
