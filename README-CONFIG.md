### Ollama config
1. Close Ollama

2. On terminal execute 
```shell
docker-compose up -d
```
```shell
launchctl setenv OLLAMA_HOST "0.0.0.0"
```

3. Open Ollama and execute on terminal
```shell
'netstat -an | grep 11434'
```
- The result must be like this
```shell
tcp46      0      0  *.11434    *.*     LISTEN
```
4. On terminal execute
```shell
curl http://localhost:4000/v1/models
```
- The response must be like this
```json
{
    "data": [
        {
            "id": "ai-angelo-zero",
            "object": "model",
            "created": 1677610602,
            "owned_by": "openai"
        }
    ],
    "object": "list"
}
```

---

### .ENV config file
```properties
# LLM 
MODEL_NAME="ai-angelo-zero"
API_KEY="api-key-angelo-1234"
BASE_URL="http://localhost:4000/v1"

# LANGCHAIN SMITH
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com
LANGSMITH_API_KEY=YOUR_LANGSMITH_API_KEY
LANGSMITH_PROJECT="python-rag-project"
OPENAI_API_KEY="api-key-angelo-1234"
```