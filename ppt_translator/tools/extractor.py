"""
Extractor tool — reads a PPTX and saves all paragraph text to a JSON file.

Each paragraph entry in the output JSON looks like:
  {
    "id":         "s<slide_index>:p<paragraph_index>",
    "encoded":    "[[0]]Hello [[/0]][[1]]World[[/1]]",
    "plain_text": "Hello World"
  }

The JSON traversal order MUST match the order used by the rebuilder so that
translated strings can be applied back positionally without any ID look-up.

📝 TASK (Step 4 — Medium)
--------------------------
Implement the body of `extract_pptx` below.

Steps:
  1. Validate that `input_path` exists; return an error dict if not.
  2. Open the presentation with python-pptx.
  3. Iterate over slides.  For each slide call `visit_slide`, passing a
     callback that appends a paragraph entry (id, encoded, plain_text) to a list.
  4. Build the output dict and write it as pretty-printed JSON (ensure_ascii=False)
     to `output_json_path`, creating parent directories as needed.
  5. Return a summary dict (see docstring of extract_pptx).

Useful helpers (already imported):
  - visit_slide(slide, callback, include_notes=True)
  - encode_paragraph is called INSIDE visit_slide for you.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pptx import Presentation

from ._common import visit_slide


def extract_pptx(
    input_path: str,
    output_json_path: str,
    include_notes: bool = True,
) -> dict[str, Any]:
    """
    Extract all text from *input_path* and save it to *output_json_path*.

    Parameters
    ----------
    input_path       : source .pptx file path
    output_json_path : where to write the extraction JSON
    include_notes    : whether to include speaker notes (default True)

    Returns
    -------
    On success:
        {
            "status": "success",
            "output_json_path": <str>,
            "slides": <int>,
            "paragraphs_extracted": <int>,
        }
    On error:
        {"error": <message>}
    """
    # TODO (Step 4): Implement the extraction logic described above.
    raise NotImplementedError("extract_pptx is not implemented yet.")
