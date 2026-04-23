# PPT Translator Agent

A **Google ADK** agent connected to **Azure OpenAI** (via LiteLLM) that translates PowerPoint presentations into any language while **preserving every formatting detail** — bold runs, colored text, font sizes, tables, grouped shapes, and speaker notes.

---

## How it works

### The formatting problem

A single sentence in a slide can be split across several "runs" inside a paragraph:

```
"Important: " (bold, blue)  +  "do not forget"  +  "!"  (red)
```

Naively translating each run independently breaks sentence context and produces poor output. Translating the whole paragraph as plain text loses the run boundaries, so you can't restore the formatting.

### The solution — tagged runs

Each run is wrapped in `[[N]]...[[/N]]` markers before being sent to the model:

```
[[0]]Important: [[/0]][[1]]do not forget[[/1]][[2]]![[/2]]
```

The model translates the text **inside** the markers while keeping them intact:

```
[[0]]Important : [[/0]][[1]]ne pas oublier[[/1]][[2]] ![[/2]]
```

The translated fragments are then written back into the original runs — their formatting (bold, color, font, size) is never touched.

### Batching

All paragraphs in a shape are sent in a **single API call** (configurable batch size, default 30 paragraphs). This keeps terminology consistent within a shape and reduces API round-trips.

---

## Project structure

```
ppt_translator_agent/
├── src/
│   └── ppt_translator/
│       ├── __init__.py
│       ├── agent.py          # Azure OpenAI agent with tool-calling loop
│       ├── prompts.py        # system prompt
│       └── tools/
│           ├── __init__.py
│           └── translator.py # core translation logic
├── main.py                   # CLI entry point
├── .env.example
├── requirements.txt
└── README.md
```

---

## Architecture

```
Google ADK Runner
   └── LlmAgent
         ├── model: LiteLlm("azure/gpt-4o")   ← routes to Azure OpenAI
         └── tools: [translate_pptx]           ← pure Python function
```

Google ADK supports non-Gemini models via its built-in **LiteLLM** integration.
`LiteLlm(model="azure/<deployment>")` is the official way to point the agent at Azure OpenAI — no custom loop needed.

---

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure credentials
cp .env.example .env
# Edit .env with your Azure OpenAI values

# 3. Run
python main.py

# Optional: open the ADK web UI (auto-discovers root_agent)
adk web
```

### Required environment variables

| Variable | Description |
|---|---|
| `AZURE_API_KEY` | Your Azure OpenAI API key (LiteLLM naming) |
| `AZURE_API_BASE` | e.g. `https://my-resource.openai.azure.com/` |
| `AZURE_API_VERSION` | API version, e.g. `2024-08-01-preview` |
| `AZURE_OPENAI_DEPLOYMENT` | Deployment name, e.g. `gpt-4o` |

---

## Usage

### Interactive CLI

```
You: translate deck.pptx to Spanish
  [tool] translate_pptx({"input_path": "deck.pptx", "output_path": "deck_Spanish.pptx", "target_language": "Spanish"})

Agent: Done! Translated 12 slides (147 paragraphs) in 8 API calls → deck_Spanish.pptx
```

### Direct Python call

```python
from dotenv import load_dotenv
load_dotenv()

from src.ppt_translator import translate_pptx

result = translate_pptx(
    input_path="deck.pptx",
    output_path="deck_fr.pptx",
    target_language="French",
    translate_notes=True,   # include speaker notes
    batch_size=30,          # paragraphs per API call
)
print(result)
# {'status': 'success', 'slides': 12, 'paragraphs_translated': 147, 'api_calls': 8, ...}
```

---

## What is preserved

| Element | Preserved |
|---|---|
| Bold / italic / underline | Yes — run-level |
| Font color (hex / theme) | Yes |
| Font size | Yes |
| Font family | Yes |
| Hyperlinks | Yes (text only — href untouched) |
| Bullet points & numbering | Yes |
| Text alignment | Yes |
| Tables | Yes (each cell translated) |
| Grouped shapes | Yes (recursive) |
| Speaker notes | Yes (optional) |
| Images, charts, animations | Untouched |

---

## Limitations

- Does not translate text embedded inside images or charts.
- Very long runs (> ~4 000 tokens per batch) may need a lower `batch_size`.
- The model occasionally drops a `[[N]]` marker on complex mixed-language slides; the fallback puts all translated text in the first run of that paragraph.
