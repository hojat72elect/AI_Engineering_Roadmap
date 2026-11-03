import json
from urllib import error, request

class ApiError(Exception):
    """
    Raised when the API cannot produce an answer. The message is already safe to show to the user.
    """

class ApiClient:
    """
    The desktop window is a client of the HTTP API, exactly like the terminal is,
    so anything added to the API later (authentication, rate limiting, caching) applies here too.
    """
    def __init__(self, baseUrl: str, timeoutSeconds: float = 120.0):
        self.baseUrl = baseUrl.rstrip("/")
        self.timeoutSeconds = timeoutSeconds

    def ask(self, question: str) -> dict:
        payload = json.dumps({"question": question}).encode("utf-8")
        askRequest = request.Request(
            f"{self.baseUrl}/api/v1/chat/ask",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with request.urlopen(askRequest, timeout=self.timeoutSeconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except error.HTTPError as httpError:
            # HTTPError is a URLError subclass, so it has to be caught first.
            raise ApiError(self.readErrorMessage(httpError)) from httpError
        except error.URLError as urlError:
            raise ApiError(f"Could not reach the API at {self.baseUrl}. Is the server running?") from urlError
        except TimeoutError as timeoutError:
            raise ApiError("The API took too long to answer.") from timeoutError

    @staticmethod
    def readErrorMessage(httpError: error.HTTPError) -> str:
        """
        FastAPI answers with {"detail": ...}, where detail is a message for our own errors
        and a list of field problems for validation failures.
        """
        try:
            body = json.loads(httpError.read().decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            return f"The server answered with HTTP {httpError.code}."

        detail = body.get("detail")

        if isinstance(detail, str):
            return f"{detail} (HTTP {httpError.code})"

        if isinstance(detail, list):
            return " ".join(str(item.get("msg", "")) for item in detail).strip()

        return f"The server answered with HTTP {httpError.code}."
