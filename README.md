# LLM and MCP Server

A comprehensive implementation of a Language Learning Model (LLM) and Model Context Protocol (MCP) Server for natural language processing and machine learning applications.

## Features

### LLM (Language Learning Model)
- **Transformer-based architecture** using Hugging Face Transformers
- **Fine-tuning capabilities** for custom datasets
- **Text generation** with configurable parameters
- **Sentiment analysis** and text classification
- **Named Entity Recognition (NER)**
- **Text summarization**
- **Question answering**

### MCP Server (Model Context Protocol)
- **RESTful API** with FastAPI
- **WebSocket support** for real-time communication
- **Model management** and versioning
- **Request/response handling** with proper validation
- **Authentication and authorization**
- **Rate limiting** and request throttling
- **Logging and monitoring**
- **Database integration** for model metadata

## Project Structure

```
├── llm/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── transformer_model.py
│   │   ├── text_classifier.py
│   │   └── text_generator.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── dataset.py
│   │   └── preprocessor.py
│   ├── training/
│   │   ├── __init__.py
│   │   ├── trainer.py
│   │   └── metrics.py
│   └── utils/
│       ├── __init__.py
│       ├── config.py
│       └── helpers.py
├── mcp_server/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── inference.py
│   │   │   └── health.py
│   │   └── middleware/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       └── rate_limit.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   └── logging.py
│   └── services/
│       ├── __init__.py
│       ├── model_service.py
│       └── inference_service.py
├── tests/
│   ├── test_llm/
│   └── test_mcp_server/
├── notebooks/
│   ├── llm_training.ipynb
│   └── mcp_server_demo.ipynb
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements.txt
├── main.py
└── README.md
```

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd llm-mcp-server
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Usage

### Starting the MCP Server

```bash
# Start the server
python main.py

# Or using uvicorn directly
uvicorn mcp_server.main:app --host 0.0.0.0 --port 8000 --reload
```

### Using the LLM

```python
from llm.models.transformer_model import TransformerModel

# Initialize model
model = TransformerModel("gpt2")

# Generate text
text = model.generate("Hello, how are you?", max_length=50)
print(text)
```

### API Endpoints

#### Model Management
- `GET /api/v1/models` - List all available models
- `POST /api/v1/models` - Register a new model
- `GET /api/v1/models/{model_id}` - Get model details
- `DELETE /api/v1/models/{model_id}` - Delete a model

#### Inference
- `POST /api/v1/inference/generate` - Text generation
- `POST /api/v1/inference/classify` - Text classification
- `POST /api/v1/inference/summarize` - Text summarization
- `POST /api/v1/inference/qa` - Question answering

#### Health and Monitoring
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

## Configuration

The application uses environment variables for configuration:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/dbname

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Model Configuration
MODEL_CACHE_DIR=./models
DEFAULT_MODEL=gpt2

# Security
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test files
pytest tests/test_llm/
pytest tests/test_mcp_server/

# Run with coverage
pytest --cov=llm --cov=mcp_server
```

### Code Formatting

```bash
# Format code
black .

# Check code style
flake8 .

# Type checking
mypy .
```

### Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run individual services
docker-compose up mcp-server
docker-compose up redis
docker-compose up postgres
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue on GitHub or contact the development team.