# layer1/llm_engine/llm_connector.py
from __future__ import annotations
import requests
from typing import Optional, Dict, Any
import urllib.parse


class LMStudioConnector:
    """
    Connector for LM Studio / local model serving.
    Expects LMSTUDIO_BASE_URL like "http://192.168.1.6:1234" (no extra :port)
    Provides llm(prompt, **kwargs) -> str
    """

    def __init__(self, base_url: Optional[str] = None, timeout: int = 120):
        if base_url is None:
            raise ValueError("LMStudio base_url required (e.g. http://192.168.1.6:1234)")
        # normalize and strip trailing slashes
        self.base_url = base_url.rstrip("/")
        # validate url
        parsed = urllib.parse.urlparse(self.base_url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError(f"Invalid LMStudio base_url: {self.base_url}")
        self.timeout = timeout

    def llm(self, prompt: str, max_tokens: int = 512, temperature: float = 0.2) -> str:
        """
        Uses /v1/chat/completions endpoint of LM Studio or compatible server.
        If your LM server uses a different path, change the endpoint here.
        """
        endpoint = f"{self.base_url}/v1/chat/completions"
        payload = {
            "model": "deepseek-r1-0528-qwen3-8b",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        try:
            resp = requests.post(endpoint, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            # support both Chat-style and text completion style
            if "choices" in data and data["choices"]:
                # Chat-style: choices[0].message.content
                ch0 = data["choices"][0]
                if "message" in ch0 and "content" in ch0["message"]:
                    return ch0["message"]["content"]
                if "text" in ch0:
                    return ch0["text"]
            # fallback: if 'output' root key
            if "output" in data:
                return str(data["output"])
            return str(data)
        except Exception as e:
            raise RuntimeError(f"LMStudioConnector failed: {e}")
