import requests

class DeepSeekClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise RuntimeError("DeepSeek API key is missing")

        self.api_key = api_key
        self.url = "https://api.deepseek.com/chat/completions"

    def ask(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a helpful study assistant."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 800,
        }

        resp = requests.post(self.url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()

        data = resp.json()
        return data["choices"][0]["message"]["content"]
