from ollama import chat
from ollama import ChatResponse

class OllamaClient:
    def generate(prompt, m):
        response: ChatResponse = chat(model=m, messages=[
            {
                'role': 'user',
                'content': prompt,
            },
            ])
        return response['message']['content']