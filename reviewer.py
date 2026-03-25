"""
reviewer.py
-----------
All Gemini AI logic. Reads API key from .env file automatically.
"""

import os
import re
from google import genai
from dotenv import load_dotenv

# Load .env file
load_dotenv()

API_KEY = os.environ.get("GEMINI_API_KEY", "")
client  = genai.Client(api_key=API_KEY)
MODEL = "gemini-2.0-flash"


REVIEW_PROMPT = """You are an expert code reviewer with deep knowledge of software engineering,
security, and best practices. When given code, you provide a thorough, structured review.

You MUST respond in exactly this format, using these exact section headers:

OVERALL SCORE: [X/10]

SUMMARY
[2-3 sentence overview of the code quality]

🐛 BUGS
[List each bug found, one per line, starting with a dash. Include the line number if possible.
If no bugs found, write: - No bugs detected]

🔒 SECURITY ISSUES
[List each security issue, one per line, starting with a dash.
If none found, write: - No security issues detected]

⚡ PERFORMANCE
[List each performance issue, one per line, starting with a dash.
If none found, write: - No performance issues detected]

📖 READABILITY & STYLE
[List each style/readability improvement, one per line, starting with a dash.
If none found, write: - Code style is good]

✅ WHAT'S GOOD
[List what the code does well, one per line, starting with a dash]

🔧 TOP RECOMMENDATIONS
[List the 3 most important things to fix or improve, numbered 1-3]

Be specific, practical, and educational. Mention line numbers where possible.
Do not add any extra text outside of these sections."""


FIX_PROMPT = """You are an expert software engineer. Rewrite the given code with ALL issues fixed.

Rules:
- Fix every bug, security issue, and performance problem
- Keep the same overall logic and purpose
- Add brief inline comments on lines you changed explaining what you fixed
- Return ONLY the fixed code, no markdown fences, no explanations outside the code

Code to fix:"""


def _call_gemini(prompt: str) -> str:
    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text


def review_code(code: str, language: str) -> dict:
    try:
        prompt = f"""{REVIEW_PROMPT}

Please review the following {language.upper()} code:

```{language}
{code}
```"""
        text = _call_gemini(prompt)
        match = re.search(r'OVERALL SCORE:\s*(\d+)/10', text, re.IGNORECASE)
        score = int(match.group(1)) if match else None
        return {"review": text, "score": score}
    except Exception as e:
        return _handle_error(e)


def fix_code(code: str, language: str) -> dict:
    try:
        prompt = f"{FIX_PROMPT}\n\n```{language}\n{code}\n```"
        fixed = _call_gemini(prompt).strip()
        if fixed.startswith("```"):
            lines = fixed.split("\n")
            fixed = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
        return {"fixed_code": fixed}
    except Exception as e:
        return _handle_error(e)


def _handle_error(e: Exception) -> dict:
    msg = str(e)
    if "API_KEY" in msg or "invalid" in msg.lower():
        return {"error": "Invalid API key. Check your .env file."}
    elif "quota" in msg.lower():
        return {"error": "API quota exceeded. Please wait a moment and try again."}
    elif "404" in msg:
        return {"error": f"Model not found: {MODEL}. Check your API access."}
    else:
        return {"error": f"AI error: {msg}"}
