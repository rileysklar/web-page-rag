# Web Scraping RAG System

A Python-based system that implements Retrieval-Augmented Generation (RAG) using web scraping, LangChain, and Pinecone. This system allows you to scrape websites, process the content, store it in a vector database, and perform question-answering using the stored knowledge.

## Features

- Recursive web scraping with proper handling of links and content
- Text processing with chunking and preprocessing
- Vector storage using Pinecone
- RAG-based question answering
- Comprehensive logging and error handling
- Command-line interface for easy usage

## Prerequisites

- Python 3.8+
- Pinecone API key
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your API keys:
```
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment_here
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

The main script provides a command-line interface with the following options:

```bash
python src/main.py --url URL --index-name INDEX_NAME [--namespace NAMESPACE] [--query QUERY]
```

### Arguments

- `--url`: The URL of the website to scrape (required)
- `--index-name`: Name for the Pinecone index (required)
- `--namespace`: Optional namespace for vectors in Pinecone
- `--query`: Optional query to run after indexing

### Examples

1. Scrape a website and create an index:
```bash
python src/main.py --url https://example.com --index-name my-index
```

2. Scrape, index, and run a query:
```bash
python src/main.py --url https://example.com --index-name my-index --query "What is the main topic of the website?"
```

3. Use a specific namespace:
```bash
python src/main.py --url https://example.com --index-name my-index --namespace website1
```

## Project Structure

```
.
├── src/
│   ├── main.py              # Main script
│   ├── web_scraper.py       # Web scraping module
│   ├── text_processor.py    # Text processing module
│   ├── vector_store.py      # Pinecone operations
│   └── rag_query.py         # RAG query engine
├── requirements.txt         # Project dependencies
├── .env                    # Environment variables
└── README.md              # This file
```

## Error Handling

The system includes comprehensive error handling and logging:

- All major operations are logged with appropriate log levels
- Exceptions are caught and logged with meaningful messages
- The system fails gracefully with proper error messages

## Best Practices

1. **API Keys**: Never commit your `.env` file. Use the provided `.env.example` as a template.
2. **Rate Limiting**: The web scraper respects website rate limits and robots.txt.
3. **Memory Usage**: Text is processed in chunks to manage memory efficiently.
4. **Error Handling**: All operations include proper error handling and logging.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 