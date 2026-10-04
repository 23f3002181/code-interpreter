import os
import sys
import traceback
from io import StringIO
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI


# Load .env file
load_dotenv()


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI()


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# OpenAI-compatible AIPipe client
# --------------------------------------------------

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=os.environ.get(
        "OPENAI_BASE_URL",
        "https://aipipe.org/openrouter/v1"
    ),
)


# --------------------------------------------------
# Request model
# --------------------------------------------------

class CodeRequest(BaseModel):
    code: str


# --------------------------------------------------
# AI response model
# --------------------------------------------------

class ErrorAnalysis(BaseModel):
    error_lines: List[int]


# --------------------------------------------------
# Tool function
# --------------------------------------------------

def execute_python_code(code: str) -> dict:
    """
    Execute Python code and return exact output.

    Returns:
        {
            "success": bool,
            "output": str
        }
    """

    old_stdout = sys.stdout

    # Capture print() output
    sys.stdout = StringIO()

    try:
        # Execute submitted Python code
        exec(code)

        output = sys.stdout.getvalue()

        return {
            "success": True,
            "output": output
        }

    except Exception:
        # Get complete traceback
        output = traceback.format_exc()

        return {
            "success": False,
            "output": output
        }

    finally:
        # Restore normal stdout
        sys.stdout = old_stdout


# --------------------------------------------------
# AI error analysis
# --------------------------------------------------

def analyze_error_with_ai(code: str, error_traceback: str) -> List[int]:
    """
    Ask the LLM to identify the exact line number(s)
    where the submitted Python code failed.
    """

    prompt = f"""
You are analyzing a Python program submitted by a user.

Your job is to identify the exact line number(s) in the
USER'S CODE that caused the error.

Important rules:

1. Return only line numbers from the submitted code.
2. Do not invent line numbers.
3. For runtime errors, use the final relevant traceback frame
   belonging to the submitted code.
4. For SyntaxError or IndentationError, use the line number
   reported by Python.
5. The submitted code starts at line 1.

USER CODE:
----------------
{code}
----------------

PYTHON TRACEBACK:
----------------
{error_traceback}
----------------

Return the error line number(s).
"""

    response = client.chat.completions.create(
        model="openai/gpt-4.1-nano",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "error_analysis",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "error_lines": {
                            "type": "array",
                            "items": {
                                "type": "integer"
                            }
                        }
                    },
                    "required": ["error_lines"],
                    "additionalProperties": False
                }
            }
        }
    )

    content = response.choices[0].message.content

    # Validate AI response using Pydantic
    result = ErrorAnalysis.model_validate_json(content)

    # Keep only valid line numbers
    total_lines = len(code.splitlines())

    valid_lines = [
        line
        for line in result.error_lines
        if 1 <= line <= total_lines
    ]

    return valid_lines


# --------------------------------------------------
# Main API endpoint
# --------------------------------------------------

@app.post("/code-interpreter")
def code_interpreter(request: CodeRequest):

    # Step 1: Execute code
    execution = execute_python_code(request.code)

    # --------------------------------------------------
    # SUCCESS
    # --------------------------------------------------

    if execution["success"]:
        return {
            "error": [],
            "result": execution["output"]
        }

    # --------------------------------------------------
    # ERROR
    # --------------------------------------------------

    error_lines = analyze_error_with_ai(
        request.code,
        execution["output"]
    )

    return {
        "error": error_lines,
        "result": execution["output"]
    }


# --------------------------------------------------
# Root endpoint
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Code Interpreter API is running"
    }