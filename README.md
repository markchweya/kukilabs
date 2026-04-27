# Kuki

Kuki is a local, CPU-first study assistant built in Streamlit. It turns raw notes into structured study material for learners who want cleaner revision sheets from messy inputs.

## What Kuki does

- Extracts text from pasted notes, PDFs, DOCX files, PPTX files, and note images.
- Rewrites notes in `Simple` or `Complex` learning modes.
- Supports strict extraction-only mode or a fill-gaps mode.
- Produces structured output with definitions, main points, explanations, examples, mistakes, questions, and summary.
- Runs locally with a GGUF model through `llama.cpp` when available.
- Falls back to a structured extraction view if the local model is not set up yet.

## Quick start

From the project folder:

```powershell
cd C:\Users\HP\OneDrive\Documents\GitHub\kukiai
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Streamlit will print a local URL, usually:

```text
http://localhost:8501
```

Open that URL in your browser.

## Local model setup

Kuki needs a local GGUF model before it can generate full AI rewrites. Without a model, the app still opens and shows a structured extraction fallback.

1. Put a GGUF model file in `models/llm/`.
2. Create or update `.env.local` with your model path:

```env
LLM_MODEL_PATH=.\models\llm\model.gguf
LLM_N_THREADS=4
LLM_N_CTX=4096
LLM_MAX_TOKENS=900
```

3. Restart Streamlit after changing `.env.local`.

For a first CPU test, use a small quantized instruct model such as a 1B-3B GGUF file. Larger models may work, but they will be slower on CPU.

## Image notes and OCR

Image uploads use local OCR through `rapidocr-onnxruntime`. If OCR is not installed or cannot load, Kuki will still run, but image extraction will show as unavailable in the sidebar.

## Notes on CPU-local inference

- Kuki uses `n_gpu_layers=0`, so inference stays on CPU.
- Image OCR is local too when `rapidocr-onnxruntime` is installed.
- On Python 3.13, install a compatible `llama-cpp-python` build manually or use Python 3.11 for the smoothest setup.

## Daily run command

After setup, you usually only need:

```powershell
cd C:\Users\HP\OneDrive\Documents\GitHub\kukiai
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

## Troubleshooting

- If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then activate `.venv` again.
- If `llama-cpp-python` fails to install on Python 3.13, create the virtual environment with Python 3.11.
- If Kuki says no model is found, check that `LLM_MODEL_PATH` points to the exact `.gguf` file.
- If image OCR is unavailable, rerun `pip install -r requirements.txt` inside the active virtual environment.

## Author

Built by Mark Chweya.

## License

MIT License.
