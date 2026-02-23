# Business Website Finder API

Production-ready FastAPI service for finding likely official business websites.

## Local run

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Production run

```bash
gunicorn -k uvicorn.workers.UvicornWorker -w 2 -b 0.0.0.0:8000 main:app
```

## Docker

```bash
docker build -t business-website-finder .
docker run -p 8000:8000 business-website-finder
```

## Environment variables

- `REQUEST_TIMEOUT` (default: `10`)
- `MAX_RESULTS` (default: `10`)

## Endpoints

- `GET /health`
- `GET /find-website?business_name=...`
"# scrappingapi" 
"# URLExtractionAPI" 
