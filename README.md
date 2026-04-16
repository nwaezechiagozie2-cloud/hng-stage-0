# Name Classification API (HNG Stage 0)

A simple FastAPI service that classifies a first name using the `Genderize` API and returns prediction details.

## Features

- Classifies a name with `gender`, `probability`, and `sample_size`
- Adds `is_confident` and `processed_at` fields
- Returns consistent error responses in this format:

```json
{ "status": "error", "message": "<error message>" }
```

## Project Structure

```text
.
├── main.py
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.10+
- Internet connection (required to call `https://api.genderize.io`)

## Setup

```bash
cd "/home/chiagozie/Desktop/hng stage 0"
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the API

```bash
uvicorn main:app --reload
```

Server starts at:

- `http://127.0.0.1:8000`
- Swagger docs: `http://127.0.0.1:8000/docs`

## Endpoint

### `GET /api/classify`

#### Query Parameter

- `name` (string, required)

### Success Response (`200`)

```json
{
	"name": "michael",
	"gender": "male",
	"probability": 0.99,
	"sample_size": 12345,
	"is_confident": true,
	"processed_at": "2026-04-16T12:34:56.123456"
}
```

## Error Responses

All errors use the same structure:

```json
{ "status": "error", "message": "<error message>" }
```

### Example Errors

Missing `name`:

```json
{ "status": "error", "message": "Name parameter is required" }
```

Invalid `name` (non-alphabetic):

```json
{ "status": "error", "message": "Name must contain only alphabetic characters" }
```

No prediction available:

```json
{ "status": "error", "message": "No prediction available for the provided name" }
```

Unexpected internal error:

```json
{ "status": "error", "message": "An unexpected error occurred." }
```

## Quick Test with `curl`

```bash
curl -X GET "http://127.0.0.1:8000/api/classify?name=Chiagozie" -H "accept: application/json"
```

```bash
curl -X GET "http://127.0.0.1:8000/api/classify" -H "accept: application/json"
```

## Notes

- The API currently accepts only alphabetic names (`isalpha()`).
- Confidence is computed as:
	- `probability >= 0.7`
	- `sample_size >= 100`

