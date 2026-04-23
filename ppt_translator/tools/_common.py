"""
Shared utilities: tagged-run encoding/decoding and shape traversal.

Both the extractor and rebuilder must traverse shapes in EXACTLY the same
order so that the flat paragraph list produced by the extractor maps
positionally to the runs in the rebuilt PPTX.

Background — why "tagged runs"?
--------------------------------
A single slide paragraph can be split across many python-pptx *runs*, each
carrying its own formatting (bold, colour, font size…).  Sending each run to
the LLM independently produces terrible translations because the model loses
sentence context.  Sending the whole paragraph as plain text means we can't
put the formatting back.

The solution: before translating, we wrap every run in [[N]]…[[/N]] markers:

    [[0]]Important: [[/0]][[1]]do not forget[[/1]][[2]]![[/2]]

The model translates the text *inside* the markers, leaving the markers intact:

    [[0]]Important : [[/0]][[1]]ne pas oublier[[/1]][[2]] ![[/2]]

We then parse the markers back out and write each fragment into the
corresponding run — formatting is never touched.

📝 TASKS (Step 3 — Core logic)
-------------------------------
Implement the two functions marked with TODO below.
The shape-traversal helpers (visit_text_frame, visit_shape, visit_slide) are
already provided for you — read them to understand how the traversal works.
"""

from __future__ import annotations

import re
from typing import Any, Callable

# Regex that matches one tagged run: [[N]]...[[/N]]
_TAG_RE = re.compile(r"\[\[(\d+)\]\](.*?)\[\[/\1\]\]", re.DOTALL)


# ── run encoding ──────────────────────────────────────────────────────────────

def encode_paragraph(para) -> tuple[str, list[tuple[int, Any]]]:
    """
    Encode a python-pptx paragraph into a tagged string for the LLM.

    Only runs that actually contain text are considered "active".

    Returns
    -------
    encoded  : str
        - If there are NO active runs  → return ("", [])
        - If there is exactly ONE run  → return (run.text, [(original_idx, run)])
          (no markers needed; keeps the LLM prompt cleaner)
        - If there are MULTIPLE runs   → return the tagged string, e.g.
          "[[0]]Hello [[/0]][[1]]World[[/1]]"
          together with the list of (original_index, run) pairs.

    active   : list[tuple[int, run]]
        The (original_run_index, run_object) pairs for every run that has text.

    📝 TODO (Step 3a): Implement this function.
    Hint: iterate over `para.runs` with enumerate(); keep only runs where
    r.text is truthy.
    """
    # TODO: implement encode_paragraph
    raise NotImplementedError("encode_paragraph is not implemented yet.")


# ── run decoding ──────────────────────────────────────────────────────────────

def decode_paragraph(translated: str, active: list[tuple[int, Any]]) -> None:
    """
    Write translated text back into the original run objects.

    Formatting (bold, colour, font, size) on each run is NEVER touched —
    only `run.text` is updated.

    Parameters
    ----------
    translated : the string returned by the LLM for this paragraph
    active     : the list returned by encode_paragraph (same paragraph)

    Algorithm
    ---------
    1. If `active` is empty → nothing to do, return.
    2. If there is exactly ONE active run → set run.text = translated, return.
    3. Otherwise, parse `_TAG_RE` matches from `translated` to build a dict
       {run_index: translated_text}.
       - If matches were found  → update each run whose index appears in the dict.
       - If NO matches (the LLM dropped the markers) → put everything in the
         first run and set all other runs' text to "".

    📝 TODO (Step 3b): Implement this function.
    """
    # TODO: implement decode_paragraph
    raise NotImplementedError("decode_paragraph is not implemented yet.")


# ── shape traversal (provided — do not modify) ────────────────────────────────

def visit_text_frame(tf, callback: Callable[[Any, str, list], None]) -> None:
    """Call callback(para, encoded, active_runs) for every non-empty paragraph."""
    for para in tf.paragraphs:
        encoded, active = encode_paragraph(para)
        if encoded.strip():
            callback(para, encoded, active)


def visit_shape(shape, callback: Callable[[Any, str, list], None]) -> None:
    """Recursively visit all text-bearing elements in a shape."""
    if shape.shape_type == 6:   # GROUP
        for child in shape.shapes:
            visit_shape(child, callback)
        return
    if shape.has_text_frame:
        visit_text_frame(shape.text_frame, callback)
    if shape.has_table:
        for row in shape.table.rows:
            for cell in row.cells:
                visit_text_frame(cell.text_frame, callback)


def visit_slide(slide, callback: Callable[[Any, str, list], None],
                include_notes: bool = True) -> None:
    """Visit every shape on a slide, then optionally the notes text frame."""
    for shape in slide.shapes:
        visit_shape(shape, callback)
    if include_notes and slide.has_notes_slide:
        notes_tf = slide.notes_slide.notes_text_frame
        visit_text_frame(notes_tf, callback)
