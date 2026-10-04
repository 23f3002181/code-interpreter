# Code Interpreter with AI Error Analysis

A FastAPI-based code interpreter that executes Python code, returns the exact execution output, and uses an AI model to identify the line number when an error occurs.

## Features

* Execute Python code through a FastAPI API.
* Capture standard output and Python tracebacks.
* Return exact execution results.
* Use AI only when the submitted code has an error.
* Identify error line numbers using structured AI output.
* CORS enabled for API testing.
* Can be deployed as a public API using Render.

## API Endpoint

```text
POST /code-interpreter
```

## Request Format

```json
{
  "code": "x = 10\ny = 0\nresult = x / y"
}
```

## Successful Response

```json
{
  "error": [],
  "result": "15\n"
}
```

## Error Response

```json
{
  "error": [3],
  "result": "Traceback (most recent call last):\n..."
}
```

## Project Structure

```text
code-interpreter/
│
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Technologies Used

* Python
* FastAPI
* Uvicorn
* Pydantic
* OpenAI-compatible API
* AIPipe
* OpenRouter

## Installation

Clone the repository:

```bash
git clone <your-github-repository-url>
cd code-interpreter
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=YOUR_AIPIPE_TOKEN
OPENAI_BASE_URL=https://aipipe.org/openrouter/v1
```

Never commit your `.env` file or API token to GitHub.

## Run the Application

```bash
uvicorn main:app --reload
```

The API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## Deployment

The application can be deployed on Render.

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

After deployment, the API endpoint will look like:

```text
https://your-app-name.onrender.com/code-interpreter
```

## Example

Send:

```json
{
  "code": "x = 5\ny = 10\nprint(x + y)"
}
```

The API returns:

```json
{
  "error": [],
  "result": "15\n"
}
```

For code containing an error, the API returns the exact Python traceback in `result` and the AI-generated error line numbers in `error`.
