"""
Google ADK agent backed by Azure OpenAI via LiteLLM.

Two tools are exposed to the agent:
  1. extract_pptx  — parse a PPTX and dump all paragraph text to JSON
  2. rebuild_pptx  — translate the JSON and write a new PPTX

📝 TASK (Step 2 — Easy)
-----------------------
Complete the `root_agent` definition below by:
  a) Choosing the right LiteLLM model string for Azure OpenAI.
     Hint: LiteLLM uses the prefix "azure/" followed by the deployment name.
     The deployment name is stored in the environment variable AZURE_OPENAI_DEPLOYMENT.

  b) Passing the two tool functions to the `tools` parameter.
     Both are already imported for you.

Useful docs:
  - LlmAgent  : https://google.github.io/adk-docs/agents/llm-agents/
  - LiteLLM   : https://docs.litellm.ai/docs/providers/azure
"""

from __future__ import annotations

import os

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from .prompts import SYSTEM_PROMPT
from .tools.extractor import extract_pptx
from .tools.rebuilder import rebuild_pptx

_deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

# TODO (Step 2a): Build the correct model string and pass it to LiteLlm.
# TODO (Step 2b): Add the two tool functions to the `tools` list.
root_agent = LlmAgent(
    name="ppt_translator",
    model=LiteLlm(model="???"),          # ← fix this
    description="Translates PowerPoint presentations while preserving all text formatting.",
    instruction=SYSTEM_PROMPT,
    tools=[],                             # ← add the tools here
)
