# 🎯 Lab — PPT Translator Agent with Google ADK

> **Exercise**
>
> Branches:
> | Branch | Purpose |
> |--------|---------|
> | `exercise` | Starter code to fill |
> | `solution` | Reference implementation |

---

## What you will build

A conversational agent that translates a PowerPoint presentation into any
language while **preserving every formatting detail** — bold text, colours,
font sizes, tables, grouped shapes, and speaker notes.

The user simply types:

```
Translate report.pptx to French
```

…and the agent calls two tools in sequence, then reports the results.

### Tool 1 — `extract_pptx`

Reads the PPTX, encodes every paragraph as a tagged string, and saves the
result to a JSON file.

### Tool 2 — `rebuild_pptx`

Reads that JSON, sends the encoded paragraphs to Azure OpenAI in batches for
translation, then re-opens the original PPTX and writes the translations back
run-by-run.

---

## The "tagged runs" trick 🔑

A single visible sentence in a slide is often stored as **multiple runs**,
each with its own formatting:

```
"Important: " (bold, blue)  +  "do not forget"  +  "!"  (red)
```

Sending each run to the LLM independently breaks sentence context.  Sending
the whole paragraph as plain text loses the run boundaries, so you can't put
the formatting back.

**Solution:** wrap every run in `[[N]]…[[/N]]` markers before translation:

```
[[0]]Important: [[/0]][[1]]do not forget[[/1]][[2]]![[/2]]
```

The model translates the text *inside* the markers and returns:

```
[[0]]Important : [[/0]][[1]]ne pas oublier[[/1]][[2]] ![[/2]]
```

Each fragment is then written back into the correct run.

---

## Project structure

```
DDEJ_GOOGLE_ADK/
├── .env.example                   ← copy to .env and fill in your keys
├── pyproject.toml                 ← Poetry project & dependencies
├── main.py                        ← CLI entry point (mostly given)
└── ppt_translator/
    ├── __init__.py
    ├── agent.py                   ← Step 2: wire model + tools
    ├── prompts.py                 ← Step 1: write the system prompt
    └── tools/
        ├── __init__.py
        ├── _common.py             ← Step 3: encode / decode paragraphs
        ├── extractor.py           ← Step 4: extract text to JSON
        └── rebuilder.py           ← Step 5: translate + rebuild PPTX
```

---

## Setup

### 1 — Prerequisites

- Python ≥ 3.11
- An **Azure OpenAI** resource with a deployed model (e.g. `gpt-4o`)

### 2 — Install dependencies

Make sure [Poetry](https://python-poetry.org/docs/#installation) is installed, then:

```bash
cd DDEJ_GOOGLE_ADK
poetry install
poetry shell
```

This creates a virtual environment and installs all dependencies declared in
`pyproject.toml` automatically.

### 3 — Configure environment variables

```bash
cp .env.example .env
# then edit .env with your Azure OpenAI credentials
```

| Variable | Description |
|---|---|
| `AZURE_API_KEY` | Your Azure OpenAI API key |
| `AZURE_API_BASE` | Endpoint, e.g. `https://my-resource.openai.azure.com/` |
| `AZURE_API_VERSION` | API version, e.g. `2024-08-01-preview` |
| `AZURE_OPENAI_DEPLOYMENT` | Deployment name, e.g. `gpt-4o` |

---

## Exercises

Work through the steps **in order**, each one builds on the previous.

---

### Step 1 — Write the system prompt (`prompts.py`)

**File:** `ppt_translator/prompts.py`

Write a string called `SYSTEM_PROMPT` that tells the agent:

1. What it is.
2. What its two tools do and what arguments they take.
3. That it **must always call `extract_pptx` first, then `rebuild_pptx`**.
4. The default naming conventions for the output files.
5. What to report back to the user after both steps.

> **Tip:** A clear, precise prompt is critical for reliable tool-calling.
> Be explicit about the order of steps and the exact argument names.

---

### Step 2 — Wire the agent (`agent.py`)

**File:** `ppt_translator/agent.py`

Two small TODOs:

**a)** Build the correct LiteLLM model string.
LiteLLM addresses Azure OpenAI models as `"azure/<deployment_name>"`.
The deployment name is in the `AZURE_OPENAI_DEPLOYMENT` environment variable.

**b)** Pass `extract_pptx` and `rebuild_pptx` to the `tools` parameter of
`LlmAgent`.

> **Tip:** `LlmAgent` accepts plain Python functions as tools, it
> automatically reads their docstrings and type hints to build the tool schema.

---

### Step 3 — Encode and decode paragraphs (`_common.py`)

**File:** `ppt_translator/tools/_common.py`

This is the heart of the formatting-preservation mechanism.

**3a) `encode_paragraph(para)`**

Given a python-pptx `Paragraph` object, return `(encoded_string, active_runs)`:

- `active_runs` = `[(original_index, run), ...]` for every run where `run.text` is non-empty.
- If no active runs → return `("", [])`.
- If exactly one active run → return `(run.text, [(idx, run)])`.
- If multiple runs → build `"[[0]]text[[/0]][[1]]text[[/1]]…"`.

**3b) `decode_paragraph(translated, active)`**

Write the translated fragments back into the run objects:

- If `active` is empty → return immediately.
- If one run → `run.text = translated`.
- Otherwise, use `_TAG_RE.finditer(translated)` to parse `{index: text}` pairs and update each run.
- **Fallback:** if the LLM dropped the markers, put everything in `active[0][1].text` and set all others to `""`.

> **Note:** the shape-traversal functions (`visit_slide`, etc.) are already
> implemented. Read them to understand how your encode/decode functions will
> be called.

---

### Step 4 — Implement the extractor (`extractor.py`)

**File:** `ppt_translator/tools/extractor.py`

Implement `extract_pptx(input_path, output_json_path, include_notes=True)`.

Suggested algorithm:

1. Return `{"error": "…"}` if `input_path` does not exist.
2. Open the presentation: `prs = Presentation(str(src))`.
3. Create an empty `paragraphs` list.
4. Iterate over `prs.slides`.  For each slide call `visit_slide(slide, callback, include_notes)` where `callback` appends a dict to `paragraphs`:
   ```python
   {
       "id":         f"s{slide_idx}:p{len(paragraphs)}",
       "encoded":    encoded,
       "plain_text": "".join(r.text for _, r in active),
   }
   ```
5. Write the result as JSON to `output_json_path` (create parent dirs).
6. Return the success summary dict.

---

### Step 5 — Implement the rebuilder (`rebuilder.py`)

**File:** `ppt_translator/tools/rebuilder.py`

**5a) `_translate_batch(client, deployment, encoded_paragraphs, target_language)`**

Build a numbered prompt, call `client.chat.completions.create`, parse the
numbered response back into a list.

Example prompt sent to the model:

```
PARA_0: [[0]]Hello[[/0]]
PARA_1: Some plain text
PARA_2: [[0]]Bonjour[[/0]] le monde
```

The model must return the same format with translated content.
Parse each `PARA_N: …` line; fall back to the original if a line is missing.

**5b) `rebuild_pptx(input_path, extraction_json_path, output_path, target_language, batch_size=30)`**

1. Validate files exist.
2. Load the extraction JSON.
3. Create `AzureOpenAI` client from env vars.
4. Translate in batches using `_translate_batch`.
5. Re-open the original PPTX and apply translations with `visit_slide` +
   `decode_paragraph` (use `iter` + `next` over `translated_list`).
6. Save the new PPTX and return the summary dict.

---

## Running the agent

Once all steps are implemented:

```bash
adk web
```
or 
```bash
python main.py
```
---

## References

- [Google ADK documentation](https://google.github.io/adk-docs/)
- [LiteLLM — Azure provider](https://docs.litellm.ai/docs/providers/azure)
- [python-pptx documentation](https://python-pptx.readthedocs.io/)
- [Azure OpenAI Python SDK](https://learn.microsoft.com/azure/ai-services/openai/quickstart?pivots=programming-language-python)

