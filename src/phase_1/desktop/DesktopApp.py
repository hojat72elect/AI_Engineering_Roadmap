import os
import queue
import threading
from typing import Any

import ttkbootstrap as tb
from ttkbootstrap.constants import BOTH, END, LEFT, RIGHT

from src.phase_1.desktop.ApiClient import ApiClient, ApiError

DEFAULT_BASE_URL = "http://127.0.0.1:8000"
DEFAULT_THEME = "bootstrap-dark"


class ChatWindow:
    """
    Windows desktop client for the phase 1 API: ask a question, read the answer and its metadata.
    """
    def __init__(self, *, client: ApiClient | None = None, theme: str = DEFAULT_THEME):
        self.root = tb.Window(title="AI Research Assistant", theme=theme, size=(820, 700))
        self.root.minsize(620, 520)
        self.client = client or ApiClient(baseUrl=os.environ.get("API_BASE_URL", DEFAULT_BASE_URL))
        # Worker threads only enqueue results; the Tk thread drains the queue, because Tk is not thread-safe.
        self.results: queue.Queue[tuple[str, Any]] = queue.Queue()
        self.buildLayout()

    def run(self) -> None:
        self.root.mainloop()

    def buildLayout(self) -> None:
        container = tb.Frame(self.root, padding=16)
        container.pack(fill=BOTH, expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(5, weight=1)

        header = tb.Frame(container)
        header.grid(row=0, column=0, sticky="ew")
        tb.Label(header, text="AI Research Assistant", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tb.Label(header, text="Ask a question and the API answers it.", bootstyle="secondary").pack(anchor="w")

        tb.Label(container, text="Your question", bootstyle="secondary").grid(row=1, column=0, sticky="w", pady=(16, 6))

        self.questionBox = tb.ScrolledText(container, height=5, wrap="word", auto_hide=True)
        self.questionBox.grid(row=2, column=0, sticky="ew")
        self.questionBox.bind("<Control-Return>", self.askQuestion)

        actions = tb.Frame(container)
        actions.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        tb.Label(actions, text="Ctrl + Enter sends", bootstyle="secondary").pack(side=LEFT)
        self.askButton = tb.Button(actions, text="Ask", bootstyle="primary", width=10, command=self.askQuestion)
        self.askButton.pack(side=RIGHT)
        self.clearButton = tb.Button(
            actions, text="Clear", bootstyle="secondary-outline", width=8, command=self.clearConversation
        )
        self.clearButton.pack(side=RIGHT, padx=(0, 8))

        tb.Label(container, text="Answer", bootstyle="secondary").grid(row=4, column=0, sticky="w", pady=(16, 6))

        self.answerBox = tb.ScrolledText(container, height=14, wrap="word", auto_hide=True)
        self.answerBox.grid(row=5, column=0, sticky="nsew")
        self.answerBox.configure(state="disabled")

        status = tb.Frame(container)
        status.grid(row=6, column=0, sticky="ew", pady=(10, 0))
        self.progressBar = tb.Progressbar(status, mode="indeterminate", bootstyle="primary", length=110)
        self.statusLabel = tb.Label(status, text="Ready", bootstyle="secondary")
        self.statusLabel.pack(side=LEFT)

        self.questionBox.focus_set()

    def askQuestion(self, event: Any = None) -> None:
        """
        Sends the question from a worker thread so the window keeps repainting while we wait.
        """
        if self.askButton.instate(["disabled"]):
            return

        question = self.questionBox.get("1.0", END).strip()

        if not question:
            self.setStatus("Type a question first.", isError=True)
            self.questionBox.focus_set()
            return

        self.setBusy(True)
        threading.Thread(target=self.runQuestion, args=(question,), daemon=True).start()
        self.root.after(100, self.pollResults)

    def runQuestion(self, question: str) -> None:
        try:
            self.results.put(("answer", self.client.ask(question)))
        except ApiError as error:
            self.results.put(("error", str(error)))
        except Exception as error:
            # A worker that dies silently would leave the window stuck in "Thinking...".
            self.results.put(("error", f"Unexpected error: {error}"))

    def pollResults(self) -> None:
        try:
            kind, payload = self.results.get_nowait()
        except queue.Empty:
            self.root.after(100, self.pollResults)
            return

        self.setBusy(False)

        if kind == "answer":
            self.showAnswer(payload)
            return

        self.setStatus(str(payload), isError=True)

    def showAnswer(self, payload: dict) -> None:
        self.answerBox.configure(state="normal")
        self.answerBox.delete("1.0", END)
        self.answerBox.insert("1.0", str(payload.get("answer", "")))
        self.answerBox.configure(state="disabled")

        self.setStatus(self.describeMetadata(payload.get("metadata") or {}))

    @staticmethod
    def describeMetadata(metadata: dict) -> str:
        """
        The same facts the API exposes, so a slow or expensive answer is never a mystery.
        """
        details = []

        if metadata.get("model"):
            details.append(str(metadata["model"]))
        if metadata.get("latencyMs") is not None:
            details.append(f"{metadata['latencyMs']} ms")
        if metadata.get("inputTokens") is not None:
            details.append(f"{metadata['inputTokens']} input / {metadata.get('outputTokens', 0)} output tokens")

        return " · ".join(details) if details else "Done"

    def clearConversation(self) -> None:
        self.questionBox.delete("1.0", END)
        self.answerBox.configure(state="normal")
        self.answerBox.delete("1.0", END)
        self.answerBox.configure(state="disabled")
        self.setStatus("Ready")
        self.questionBox.focus_set()

    def setBusy(self, isBusy: bool) -> None:
        state = "disabled" if isBusy else "normal"
        self.askButton.configure(state=state)
        self.questionBox.configure(state=state)

        if isBusy:
            self.progressBar.pack(side=LEFT, before=self.statusLabel)
            self.progressBar.start(12)
            self.setStatus("Thinking...")
            return

        self.progressBar.stop()
        self.progressBar.pack_forget()
        self.questionBox.focus_set()

    def setStatus(self, message: str, *, isError: bool = False) -> None:
        colors = self.root.style.colors
        self.statusLabel.configure(text=message, foreground=colors.danger if isError else colors.secondary)


def main() -> None:
    ChatWindow().run()


if __name__ == "__main__":
    main()
