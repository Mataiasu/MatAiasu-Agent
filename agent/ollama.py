import json
from urllib import error, request


class OllamaError(RuntimeError):
    pass


class OllamaClient:
    """Minimal dependency-free client for a local Ollama server."""

    def __init__(self, base_url: str, model: str, timeout: int = 120) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def available(self) -> bool:
        try:
            with request.urlopen(f"{self.base_url}/api/tags", timeout=5) as response:
                return response.status == 200
        except (OSError, error.URLError):
            return False

    def chat(self, prompt: str, system: str | None = None) -> str:
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        if system:
            payload["system"] = system
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            f"{self.base_url}/api/generate",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (OSError, error.URLError, TimeoutError) as exc:
            raise OllamaError(f"Ollama unavailable: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise OllamaError("Ollama returned invalid JSON") from exc
        return str(data.get("response", "")).strip()
