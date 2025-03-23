# UsageFlow FastAPI

FastAPI middleware for UsageFlow - Usage-based pricing made simple.

## Installation

```bash
pip install usageflow-fastapi
```

## Usage

```python
from fastapi import FastAPI
from usageflow.fastapi import UsageFlowMiddleware

app = FastAPI()

# Initialize UsageFlow middleware
app.add_middleware(UsageFlowMiddleware, api_key="your-api-key")

@app.get("/")
async def home():
    return {"message": "Hello World!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Features

- Automatic usage tracking
- Request/response logging
- Rate limiting
- User identification
- Custom metadata support
- Async support

## Documentation

For full documentation, visit [https://docs.usageflow.io](https://docs.usageflow.io)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
