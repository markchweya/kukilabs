# Kuki

Kuki is a production-style AI workspace built in Streamlit. It supports chat, uploaded study material, document extraction, and local OCR.

## What Kuki does

- Provides a ChatGPT-style chat interface with conversation history.
- Extracts text from PDFs, DOCX files, PPTX files, note images, TXT, and Markdown.
- Uses uploaded material as chat context.
- Uses Ollama as the AI runtime when it is running.
- Keeps OCR local through `rapidocr-onnxruntime`.

## Quick start

From the project folder:

```powershell
cd C:\Users\HP\OneDrive\Documents\GitHub\kukiai
npm run dev
```

That command launches Streamlit through the Kuki helper script. The helper keeps its Python virtual environment in your local app data folder so OneDrive does not freeze Python imports or cache files.

If you prefer to manage the Python environment manually:

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

The app entry point is `app.py`. Do not run `kuki/chat_page.py` from inside the `kuki` folder unless you are debugging that page directly.

If your project is inside OneDrive, use the helper script instead:

```powershell
cd C:\Users\HP\OneDrive\Documents\GitHub\kukiai
.\run_kuki.ps1
```

The script runs Streamlit from your user folder while pointing it back to this app. That avoids broken OneDrive placeholder reads from `.streamlit/config.toml`.

The helper script skips dependency installation during normal launches so the app opens faster. If you change `requirements.txt`, run:

```powershell
npm run dev:install
```

## AI setup

Kuki uses Ollama for AI responses. This machine already has Ollama installed and models available, so the app can answer immediately when Ollama is running.

To choose a specific Ollama model, set `KUKI_AI_MODEL` in `.env.local`:

```env
KUKI_AI_MODEL=llama3.2:3b
```

Restart Streamlit after changing `.env.local`.

## Image notes and OCR

Image uploads use local OCR through `rapidocr-onnxruntime`. If OCR is not installed or cannot load, Kuki will still run, but image extraction will show as unavailable in the sidebar.

## Notes on AI and OCR

- Ollama manages the model runtime for Kuki.
- Image OCR is local too when `rapidocr-onnxruntime` is installed.

## Daily run command

After setup, you usually only need:

```powershell
cd C:\Users\HP\OneDrive\Documents\GitHub\kukiai
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

If Streamlit shows `OSError: [Errno 22] Invalid argument` while reading config, run:

```powershell
cd C:\Users\HP\OneDrive\Documents\GitHub\kukiai
.\run_kuki.ps1
```

If you see `ModuleNotFoundError: No module named 'kuki'`, you are probably running a file from inside the `kuki` package. Go back to the project root and run `streamlit run app.py`, or use `.\run_kuki.ps1`.

## Troubleshooting

- If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then activate `.venv` again.
- If Kuki says AI is offline, start Ollama and refresh the app.
- If you want a different model, set `KUKI_AI_MODEL` to an installed Ollama model name.
- If image OCR is unavailable, rerun `pip install -r requirements.txt` inside the active virtual environment.
- If Streamlit fails while reading `.streamlit/config.toml`, use `.\run_kuki.ps1` or move the project outside OneDrive.

## Author

Built by Mark Chweya.

## License

MIT License.
