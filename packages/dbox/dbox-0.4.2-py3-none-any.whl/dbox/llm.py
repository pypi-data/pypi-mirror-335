import logging
from contextvars import ContextVar

from IPython.core.interactiveshell import InteractiveShell
from ollama import Client

from dbox.utils.ipython import MarkdownPrinter

log = logging.getLogger(__name__)
ollama_client = Client(host="http://localhost:11434")

HISTORY_CTX = ContextVar("history", default=[])
MODEL_CTX = ContextVar("model", default="llama3.2")


def llm(line, cell: str = None):
    # Define the model and initial user message

    line = line.strip()
    if line == "clear":
        HISTORY_CTX.set([])
        return
    elif line.startswith("set-model"):
        model = line.split()[1]
        MODEL_CTX.set(model)
        return

    model = MODEL_CTX.get()
    prompt = cell.strip() if cell else line

    messages = HISTORY_CTX.get()
    messages.append({"role": "user", "content": prompt})
    try:
        stream = ollama_client.chat(
            model=model,
            messages=messages,
            stream=True,
        )
        # Initialize the history string
        response = ""
        with MarkdownPrinter() as printer:
            for chunk in stream:
                content = chunk["message"]["content"]
                response += content
                printer.print(content)
    except KeyboardInterrupt:
        return
    finally:
        messages.append({"role": "assistant", "content": response})
        HISTORY_CTX.set(messages)


# This function is needed to load the extension into IPython
def load_ipython_extension(ipython: InteractiveShell):
    ipython.register_magic_function(llm, magic_kind="line_cell", magic_name="llm")
