# Document Chat Application

This project is a document chat application that leverages Elasticsearch for search capabilities and Ollama for natural language processing. The application is containerized using Docker and can be deployed using Docker Compose or Kubernetes. Currently, the application only supports PDF documents. The user interface is developed with Streamlit.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

Ensure you have the following installed on your system:

- Docker
- Docker Compose
- Kubernetes (kubectl and a cluster)
- Python 3.11
- OpenAI API Key (Get your API key [here](https://openai.com/api/))

## Installation

### Using Docker Compose

1. Clone the repository:
    ```bash
    git clone https://github.com/Jbdu4493/chat_rag
    cd chat_rag
    ```

2. Build and run the Docker containers:
    ```bash
    docker-compose up --build
    ```

### Using Kubernetes

1. Clone the repository:
    ```bash
    git clone https://github.com/Jbdu4493/chat_rag
    cd chat_rag/k8s
    ```

2. Apply the Kubernetes configurations:
    ```bash
    kubectl apply -f configurationk8s.yaml
    ```

## Usage

### Accessing the Application

- Once the containers are up and running, access the application at `http://localhost:8501`.

### Interacting with the Application

- The application provides a chat interface where you can interact with the document processing and search capabilities powered by Elasticsearch and Ollama. Please note that the application only supports PDF documents. The user interface is developed with Streamlit.

## Configuration

### Environment Variables

The application can be configured using the following environment variables:

- `OLLAMA_URL`: URL of the Ollama service (default: `http://ollama:11434`)
- `ELASTICSEARCH_URI`: URL of the Elasticsearch service (default: `http://elasticsearch:9200`)
- `OPENAI_API_KEY`: Your OpenAI API key

### Docker Compose Configuration

The Docker Compose configuration is defined in `docker-compose.yaml`.

### Kubernetes Configuration

The Kubernetes configuration is defined in `k8s/configurationk8s.yaml`.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss any changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
