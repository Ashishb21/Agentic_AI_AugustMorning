import gradio as gr
import requests
import json
import os

from pypdf import PdfReader
import docx

# Ollama API
URL = "http://localhost:11434/api/generate"

# Global variable to store uploaded file text
FILE_CONTEXT = ""


# ---------------------------
# File Parsing
# ---------------------------
def extract_text(file_path):
    if file_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    elif file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)

    else:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()


def upload_file(file):
    global FILE_CONTEXT

    if not file:
        return "❌ No file uploaded"

    FILE_CONTEXT = extract_text(file.name)

    if len(FILE_CONTEXT.strip()) == 0:
        return "❌ Unable to extract text"

    return "✅ File uploaded and processed successfully!"


# ---------------------------
# Prompt + Context Injection
# ---------------------------
def build_prompt(user_question):
    return f"""
You are an intelligent assistant.
Answer the question strictly using the context below.
If the answer is not present, say "Information not found in the document."

### Context:
{FILE_CONTEXT}

### Question:
{user_question}

### Answer:
"""


# ---------------------------
# Streaming LLM Call
# ---------------------------
def generate_text(user_question, model):
    if not FILE_CONTEXT:
        yield "❌ Please upload a document first."
        return

    prompt = build_prompt(user_question)

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True
    }

    try:
        with requests.post(URL, json=payload, stream=True, timeout=None) as response:
            response.raise_for_status()
            output = ""

            for line in response.iter_lines():
                if line:
                    data = json.loads(line.decode("utf-8"))
                    token = data.get("response", "")
                    output += token
                    yield output

    except Exception as e:
        yield f"❌ Error: {str(e)}"


# ---------------------------
# Gradio UI
# ---------------------------
with gr.Blocks(title="Resume / Document Q&A (Ollama)") as demo:
    gr.Markdown("## 📄 Document Q&A using Ollama")
    gr.Markdown("Upload a resume or document and ask questions based on its content.")

    with gr.Row():
        model_dropdown = gr.Dropdown(
            choices=[
                "gpt-oss-safeguard:20b",
                "llama3:8b",
                "llama3.2"
            ],
            value="llama3:8b",
            label="Select Model"
        )

    with gr.Row():
        file_upload = gr.File(
            label="Upload Document (PDF / DOCX / TXT)",
            file_types=[".pdf", ".docx", ".txt"]
        )
        upload_status = gr.Textbox(label="Upload Status")

    file_upload.change(
        fn=upload_file,
        inputs=file_upload,
        outputs=upload_status
    )

    question_box = gr.Textbox(
        label="Ask a question",
        placeholder="What skills does the candidate have?",
        lines=3
    )

    output_box = gr.Textbox(
        label="LLM Response",
        lines=12
    )

    ask_btn = gr.Button("Ask Question")

    ask_btn.click(
        fn=generate_text,
        inputs=[question_box, model_dropdown],
        outputs=output_box
    )

demo.launch()
