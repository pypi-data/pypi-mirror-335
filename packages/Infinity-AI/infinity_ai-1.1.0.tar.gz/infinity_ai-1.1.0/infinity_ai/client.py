import os
import sys
import io
import g4f
# 🔹 Patch sys.stdout to block g4f print messages
class BlockPrint(io.StringIO):
    def write(self, text):
        if "New g4f version" in text:
            return  # Do nothing, block the message
        sys.__stdout__.write(text)  # Print everything else normally

sys.stdout = BlockPrint()

class AI:
    def __init__(self):
        self.model = "Orion"
        self.default_system_prompt = (
            "You are Orion, a helpful AI assistant created by abdullah ali who is 13 years old. You provide accurate, informative, "
            "and friendly responses while keeping them concise and relevant."
        )

    class chat:
        class completions:
            @staticmethod
            def create(model, messages, web_search=False):
                if model != "Orion":
                    raise ValueError("Only 'Orion' model is supported.")

                # Extract user-defined system prompt if provided
                user_system_prompt = ""
                if messages and messages[0]["role"] == "system":
                    user_system_prompt = messages.pop(0)["content"] + " "

                # Combine default and user system prompts
                full_prompt = [{"role": "system", "content": AI().default_system_prompt + " " + user_system_prompt}] + messages

                response = g4f.ChatCompletion.create(
                    model=g4f.models.gpt_4o_mini,
                    messages=full_prompt,
                    web_search=web_search
                )

                class Response:
                    class Choice:
                        class Message:
                            content = response
                        message = Message()
                    choices = [Choice()]

                return Response()
