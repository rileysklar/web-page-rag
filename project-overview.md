# Prompt for LLM AI Agent

Write a Python script that performs the following tasks using **LangChain** and **Pinecone**:

## Web Scraping with Recursive Web Loader
- Scrape a website and retrieve all pages, handling links recursively to capture the entire structure of the website.
- Use LangChain's `RecursiveWebPageLoader` for web scraping, ensuring it:
  - Handles redirects and retries.
  - Filters out unnecessary file types (e.g., images, videos, or binary files).

## Indexing with Pinecone
- Use the scraped content to create an index in Pinecone.
- Set up a Pinecone vector database with proper configurations, such as:
  - Index dimensions.
  - Metadata support.
- Implement a clear workflow for storing text embeddings, including splitting large text blocks into chunks for efficient storage and retrieval.

## Text Chunking and Preprocessing
- Use LangChain's `TextSplitter` to chunk the text into smaller pieces suitable for embedding.
- Include overlapping chunks to maintain context in embeddings.
- Ensure that all text preprocessing steps are applied, such as:
  - Removing HTML tags.
  - Normalizing whitespace.
  - Handling non-UTF-8 characters.

## Best Practices for RAG (Retrieval-Augmented Generation)
- Set up a pipeline to retrieve chunks from the Pinecone index based on similarity search, integrating this with LangChain's retrieval tools.
- Use LangChain's `RetrievalQA` to demonstrate how to query the index and get context-aware answers.
- Incorporate error handling and logging for scraping, indexing, and query execution.

## Comments and Documentation
- Provide detailed comments and docstrings for each function, explaining its purpose and usage.
- Include a clear README-style explanation within the script outlining:
  - **Dependencies**
  - **Setup Instructions** (e.g., Pinecone API key, installing necessary libraries)
  - **Example Usage** and **Expected Outcomes**

