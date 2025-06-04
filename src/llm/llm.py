from src.llm.llm_client import LLMClient

class ConversationalLLM:
    def __init__(self, system_prompt: str, model_name: str):
        self.system_prompt = system_prompt
        self.model_name = model_name
        self.llm_client = LLMClient()
        self.chat_history = [{"role": "system", "content": self.system_prompt}]

    def send_message(self, user_message: str) -> str:
        self.chat_history.append({"role": "user", "content": user_message})
        try:
            # Assuming call_llm will be modified to take 'messages' argument
            # For now, this will likely cause an error if not yet modified.
            # We will adapt this once LLMClient is updated.
            # LLMClient.call_llm now expects a 'messages' list.
            assistant_response = self.llm_client.call_llm(
                model_name=self.model_name,
                messages=self.chat_history
            )
            self.chat_history.append({"role": "assistant", "content": assistant_response})
            return assistant_response
        except Exception as e:
            # Basic error handling, append error or remove last user message
            # For simplicity, just re-raising for now or returning error message
            print(f"Error calling LLM: {e}")
            # Optionally remove the last user message if the call failed
            # self.chat_history.pop()
            return f"Error: Could not get response from LLM. {e}"

    def get_history(self) -> list:
        return self.chat_history

    def clear_history(self):
        self.chat_history = [{"role": "system", "content": self.system_prompt}]

if __name__ == "__main__":
    try:
        system_prompt = "You are a pirate chatbot who answers with 'Arr!' at the beginning of every sentence."
        model_name = "deepseek/deepseek-r1-0528:free" # Ensure this model is compatible with your API key

        conversation = ConversationalLLM(system_prompt, model_name)

        print(f"Starting conversation with a pirate chatbot (System Prompt: '{system_prompt}')...")

        user_message1 = "Hello there!"
        print(f"\nUser: {user_message1}")
        response1 = conversation.send_message(user_message1)
        print(f"Pirate Bot: {response1}")

        user_message2 = "How are you today?"
        print(f"\nUser: {user_message2}")
        response2 = conversation.send_message(user_message2)
        print(f"Pirate Bot: {response2}")

        print("\n--- Full Chat History ---")
        full_history = conversation.get_history()
        for message in full_history:
            print(f"{message['role'].capitalize()}: {message['content']}")

        conversation.clear_history()
        print("\n--- Chat history cleared. ---")

        print("\n--- History After Clearing ---")
        history_after_clear = conversation.get_history()
        for message in history_after_clear:
            print(f"{message['role'].capitalize()}: {message['content']}")

        user_message3 = "Hello again!"
        print(f"\nUser: {user_message3}")
        response3 = conversation.send_message(user_message3)
        print(f"Pirate Bot: {response3}")

        print("\n--- History After New Message Post-Clear ---")
        final_history = conversation.get_history()
        for message_item in final_history: # Renamed to avoid conflict
            print(f"{message_item['role'].capitalize()}: {message_item['content']}")

    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred during the example usage: {e}")
