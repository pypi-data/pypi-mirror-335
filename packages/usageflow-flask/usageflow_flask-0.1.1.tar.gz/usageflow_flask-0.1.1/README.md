# UsageFlow Flask

Flask middleware for UsageFlow - Usage-based pricing made simple.

## Installation

```bash
pip install usageflow-flask
```

## Usage

```python
from flask import Flask
from usageflow.flask import UsageFlowMiddleware

app = Flask(__name__)

# Initialize UsageFlow middleware
UsageFlowMiddleware(app, api_key="your-api-key")

@app.route("/")
def home():
    return {"message": "Hello World!"}

if __name__ == "__main__":
    app.run()
```

## Features

- Automatic usage tracking
- Request/response logging
- Rate limiting
- User identification
- Custom metadata support

## Documentation

For full documentation, visit [https://docs.usageflow.io](https://docs.usageflow.io)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
