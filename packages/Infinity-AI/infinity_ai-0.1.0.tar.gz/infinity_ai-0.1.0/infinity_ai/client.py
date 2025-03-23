import g4f

class AI:
    def __init__(self):
        self.model = "Orion"
        self.default_system_prompt = (
            "You are Orion, a helpful AI assistant. You provide accurate, informative, "
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
                    model=g4f.models.gpt_4o,
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
