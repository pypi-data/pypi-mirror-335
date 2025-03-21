# Wetrocloud SDK

A powerful Python SDK for interacting with Wetrocloud's suite of AI and data processing services.

## Table of Contents
- [Installation](#installation)
- [Authentication](#authentication)
- [Core Concepts](#core-concepts)
- [Modules](#modules)
  - [Wetrocloud Client](#wetrocloud-client)
  - [RAG Module](#rag-module)
  - [Tools Module](#tools-module)
- [Examples](#examples)
  - [RAG Examples](#rag-examples)
  - [Tools Examples](#tools-examples)
- [Error Handling](#error-handling)
- [Advanced Usage](#advanced-usage)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)

## Installation

```bash
pip install wetro
```

## Authentication

Authentication with the Wetrocloud API requires an API key. You can provide this key when initializing any client.

```python
from wetro import Wetrocloud

# Initialize the main client and access modules
client = Wetrocloud(api_key="your_api_key")
rag_client = client.rag
tools_client = client.tools
```

## Core Concepts

The Wetrocloud SDK is organized into specialized modules that focus on different functionalities:

1. **RAG (Retrieval-Augmented Generation)**: Manage collections of documents and query them using natural language.
2. **Tools**: Access utility functions including text generation, image processing, web extraction, and content categorization.

Each module can be used independently or together through the unified `Wetrocloud` client.

## Modules

### Wetrocloud Client

The main entry point that provides access to all functionality in the SDK.

```python
from wetro import Wetrocloud

client = Wetrocloud(api_key="your_api_key")

# Access modules
rag_client = client.rag
tools_client = client.tools
```

### RAG Module

The RAG (Retrieval-Augmented Generation) module allows you to create, manage, and query collections of documents.

#### Key Features
- Create and manage document collections
- Insert documents from various sources (web, text, files)
- Query collections using natural language
- Chat with context from your collections
- Structured output formatting with JSON schemas

#### Basic Usage

```python
from wetro import WetroRAG

# Initialize RAG client
rag_client = WetroRAG(api_key="your_api_key")

# Set or create a collection
rag_client.collection.get_or_create_collection_id("my_unique_collection_id")

# Insert a web resource
insert_response = rag_client.collection.insert("https://example.com/article", "web")
print("Insert response: %s", insert_response)

# Query the collection
query_response = rag_client.collection.query("What are the key points of the article?")
print("Query response: %s", query_response)
```

### Tools Module

The Tools module provides access to various AI-powered utilities.

#### Key Features
- Text generation with different models
- Content categorization
- Image-to-text conversion (OCR)
- Web extraction with structured output

#### Basic Usage

```python
from wetro import WetroTools

# Initialize Tools client
tools_client = WetroTools(api_key="your_api_key")

# Generate text
generate_response = tools_client.generate_text(
    messages=[{"role": "user", "content": "What is a large language model?"}],
    model="gpt-4"
)
print("Generate text response: %s", generate_response)
```

## Examples

### RAG Examples

#### Working with Collections

```python
# Create or access a collection
rag_client.collection.get_or_create_collection_id("research_papers")

# Insert documents from different sources
rag_client.collection.insert("https://medium.com/@wetrocloud/why-legal-tech-needs-wetrocloud-ai-rag-and-the-future-of-legal-practice-66fb38c4df09", "web")
rag_client.collection.insert("This is a sample text document about AI.", "text")
```

#### Basic Querying

```python
# Simple query
response = rag_client.collection.query("What are the main findings in the research?")
print(response)
```

#### Specify Model

```python
# Define Model to get response from the specific model
response = rag_client.collection.query(
    "Give me a detailed summary of the article",
    model="gpt-3.5-turbo"
)

print(response)
```

#### Structured Output with JSON Schema

```python
# Define a JSON schema for structured output
json_schema = [{"point_number": "<int>", "point": "<str>"}]

# Add processing rules
rules = ["Only 5 points", "Strictly return JSON only"]

# Query with structured output requirements
response = rag_client.collection.query(
    "What are the key points of the article?",
    json_schema,
    rules
)
print(response)
```

#### Streaming Responses

```python
# Stream responses for long-form content
streaming_response = rag_client.collection.query(
    "Give me a detailed summary of the article",
    stream=True
)

# Process streaming response
for chunk in streaming_response:
    print(chunk.response, end="")
```
Note: Streaming is not supported with Structured Output with JSON Schema, it's one or the other 

#### Conversational Context

```python
# Create a chat history
chat_history = [
    {"role": "user", "content": "What is this collection about?"}, 
    {"role": "system", "content": "It stores research papers on AI technology."}
]

# Continue the conversation with context
chat_response = rag_client.collection.chat(
    "Can you explain the latest paper's methodology?",
    chat_history
)
print(chat_response)
```

### Tools Examples

#### Text Generation

```python
# Generate text with a specific model
response = tools_client.generate_text(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."}, 
        {"role": "user", "content": "Write a short poem about technology."}
    ],
    model="gpt-4"
)
print(response)
```

#### Content Categorization

```python
# Categorize content
categorize_response = tools_client.categorize(
    resource="match review: John Cena vs. The Rock.",
    type="text",
    json_schema='{"label": "string"}',
    categories=["wrestling", "entertainment", "sports", "news"]
)
print(categorize_response)
```

#### Image to Text (OCR)

```python
# Extract text from an image and answer questions about it
ocr_response = tools_client.image_to_text(
    image_url = "https://images.squarespace-cdn.com/content/v1/54822a56e4b0b30bd821480c/45ed8ecf-0bb2-4e34-8fcf-624db47c43c8/Golden+Retrievers+dans+pet+care.jpeg",
    request_query="What animal is in this image?"
)
print(ocr_response)
```

#### Web Extraction

```python
# Extract structured data from a website
extract_response = tools_client.extract(
    website="https://www.forbes.com/real-time-billionaires/",
    json_schema='[{"name": "<name>", "networth": "<networth>"}]'
)
print(extract_response)
```

## Error Handling

The SDK uses standardized error handling. All API calls may raise exceptions derived from `WetrocloudError`.

```python
from wetro import Wetrocloud, WetrocloudError

client = Wetrocloud(api_key="your_api_key")

try:
    response = client.rag.collection.query("What is this article about?")
except WetrocloudError as e:
    print(f"Error: {e.status_code} - {e.message}")
    # Handle specific error cases
    if e.status_code == 401:
        print("Authentication failed. Check your API key.")
    elif e.status_code == 404:
        print("Collection not found. Create a collection first.")
```

## Advanced Usage

### Custom Domain

```python
client = Wetrocloud(
    api_key="your_api_key",
    base_url="custom_url"
)
```

### Configuring Request Timeouts

```python
client = Wetrocloud(
    api_key="your_api_key",
    timeout=30  # 30 seconds timeout
)
```

### Using with Async Frameworks (Coming Soon)

```python
import asyncio
from wetro import AsyncWetrocloud

async def main():
    client = AsyncWetrocloud(api_key="your_api_key")
    response = await client.rag.collection.query("What are the key insights?")
    return response

result = asyncio.run(main())
```

## API Reference

### WetroRAG Methods

#### `collection.get_or_create_collection_id(collection_id)`
Sets the current collection ID or creates a new collection.

#### `collection.insert(resource, type)`
Inserts a document into the collection.
- `resource`: URL, text content, or file path
- `type`: "web", "text", "json", or "file"

#### `collection.query(request_query, model=None, json_schema=None, json_schema_rules=None, stream=False)`
Queries the collection.
- `request_query`: Natural language query
- `model`: Optional model name (e.g., "gpt-3.5-turbo", "gpt-4")
- `json_schema`: Optional JSON schema for structured output
- `json_schema_rules`: Optional list of processing rules
- `stream`: Boolean to enable response streaming

#### `collection.chat(message, chat_history=None, model=None, stream=False)`
Chat with context from the collection.
- `message`: Current user message
- `chat_history`: List of previous message dictionaries
- `model`: Optional model name
- `stream`: Boolean to enable response streaming

#### `collection.delete_resource(resource_id)`
Delete a resource from the collection.
- `resource_id`: Current user message

#### `collection.delete()`
Delete the collection.

### WetroTools Methods

#### `generate_text(messages, model=None)`
Generates text using a specified model.
- `messages`: List of message dictionaries
- `model`: Model name (e.g., "gpt-3.5-turbo", "gpt-4")

#### `categorize(resource, type, json_schema, categories, prompt)`
Categorizes content according to provided categories.
- `resource`: Content to categorize
- `type`: "text", "url", etc.
- `json_schema`: Schema for structured output
- `categories`: List of category options
- `prompt`: Prompt to instruction or inform the LLM on what and how to perfom the categorization

#### `image_to_text(image_url, request_query=None)`
Extracts text from images and optionally answers questions about the content.
- `image_url`: URL of the image
- `request_query`: Optional question about the image content

#### `extract(website, json_schema)`
Extracts structured data from websites.
- `website`: URL to extract from
- `json_schema`: Schema defining the data structure to extract

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```
   Error: 401 - Invalid API key
   ```
   Solution: Verify your API key is correct and has the necessary permissions.

2. **Collection Not Found**
   ```
   Error: 404 - Collection not found
   ```
   Solution: Use `get_or_create_collection_id()` before querying.

3. **Rate Limiting**
   ```
   Error: 429 - Too many requests
   ```
   Solution: Implement backoff and retry logic for high-volume operations.


## Support

For additional support, please contact support@wetrocloud.com or visit our documentation at https://docs.wetrocloud.com.
