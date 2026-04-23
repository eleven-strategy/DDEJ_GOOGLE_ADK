"""
System prompt for the PPT Translator agent.

📝 TASK (Step 1 — Easy)
-----------------------
Write a system prompt that tells the agent:
  1. What it is (a PowerPoint translation assistant).
  2. What two tools it has and what each one does:
       - extract_pptx(input_path, output_json_path)
       - rebuild_pptx(input_path, extraction_json_path, output_path, target_language)
  3. The order in which it MUST call the tools (extract first, then rebuild).
  4. The default naming conventions when the user does not specify:
       - extraction JSON : <same directory>/<stem>_extraction.json
       - translated PPTX : <same directory>/<stem>_<Language>.pptx
  5. What to report after both steps are done.

Store the result in a module-level constant called SYSTEM_PROMPT.
"""

# TODO (Step 1): Replace the placeholder below with your system prompt string.
SYSTEM_PROMPT = ""  # ← your prompt here
