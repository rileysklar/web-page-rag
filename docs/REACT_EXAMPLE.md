# React Integration Example

## Environment Setup

Create a `.env` file in your React project:
```env
# Astro/Vite environment variables must start with VITE_
VITE_API_URL="https://web-page-rag-api.fly.dev"
VITE_API_KEY="test123"
```

## Chat Component

Here's a React component that interacts with the deployed RAG API:

```tsx
import { useState } from 'react';

interface Source {
  url: string;
  title: string;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
}

interface ChatProps {
  apiKey?: string; // Optional prop to override default API key
  apiUrl?: string; // Optional prop to override default API URL
}

export const RagChat: React.FC<ChatProps> = ({ apiKey, apiUrl }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Use environment variables with fallbacks
  // Make sure the URL doesn't have a trailing slash
  const BASE_URL = (apiUrl || import.meta.env.VITE_API_URL || 'https://web-page-rag-api.fly.dev').replace(/\/$/, '');
  const API_KEY = apiKey || import.meta.env.VITE_API_KEY || 'test123';

  const sendMessage = async (message: string) => {
    try {
      setLoading(true);
      setError(null);
      
      // Add user message
      setMessages(prev => [...prev, { role: 'user', content: message }]);
      
      // Log the full URL for debugging
      console.log('Sending request to:', `${BASE_URL}/api/rag/query`);
      
      // Send request to deployed API
      const response = await fetch(`${BASE_URL}/api/rag/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': API_KEY,
        },
        body: JSON.stringify({ message }),
      });
      
      if (!response.ok) {
        throw new Error(
          `API request failed: ${response.status} ${response.statusText}`
        );
      }
      
      const data = await response.json();
      
      // Add assistant response
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
      }]);
      
    } catch (error) {
      console.error('Error:', error);
      setError(error instanceof Error ? error.message : 'An error occurred');
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request.',
      }]);
    } finally {
      setLoading(false);
      setInput('');
    }
  };

  return (
    <div className="flex flex-col h-[600px] w-full max-w-2xl mx-auto bg-white rounded-lg shadow-lg">
      {/* Chat messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex flex-col ${
              message.role === 'user' ? 'items-end' : 'items-start'
            }`}
          >
            <div
              className={`p-3 rounded-lg max-w-[80%] ${
                message.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              {message.content}
            </div>
            
            {/* Sources */}
            {message.sources && (
              <div className="mt-2 text-sm text-gray-500">
                <details className="cursor-pointer">
                  <summary className="font-medium">View Sources</summary>
                  <ul className="mt-1 list-disc list-inside pl-2">
                    {message.sources.map((source, idx) => (
                      <li key={idx}>
                        <a
                          href={source.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-500 hover:underline"
                        >
                          {source.title || source.url}
                        </a>
                      </li>
                    ))}
                  </ul>
                </details>
              </div>
            )}
          </div>
        ))}
        
        {/* Loading indicator */}
        {loading && (
          <div className="flex justify-center">
            <div className="animate-pulse text-gray-500">Thinking...</div>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="text-red-500 text-center p-2 bg-red-50 rounded">
            {error}
          </div>
        )}
      </div>
      
      {/* Input form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (input.trim() && !loading) {
            sendMessage(input.trim());
          }
        }}
        className="p-4 border-t border-gray-200"
      >
        <div className="flex space-x-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about the website..."
            className="flex-1 p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg disabled:opacity-50 hover:bg-blue-600 transition-colors"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
};
```

## Usage in Astro

1. Create the component file:
```tsx
// src/components/RagChat.tsx
// (Copy the component code from above)
```

2. Use in Astro page:
```astro
---
// src/pages/index.astro
import { RagChat } from '../components/RagChat';
---

<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width" />
    <title>RAG Chat</title>
  </head>
  <body>
    <main class="container mx-auto p-4">
      <h1 class="text-2xl font-bold mb-4">Chat with our Website</h1>
      
      <RagChat
        client:load
        apiUrl={import.meta.env.VITE_API_URL}
        apiKey={import.meta.env.VITE_API_KEY}
      />
    </main>
  </body>
</html>
```

3. Configure environment variables in `.env`:
```env
VITE_API_URL="https://web-page-rag-api.fly.dev"
VITE_API_KEY="test123"
```

## Troubleshooting

Common issues and solutions:

1. **404 Not Found Error**
   - Make sure `VITE_API_URL` is set correctly in `.env`
   - Verify no trailing slash in the API URL
   - Check the API endpoint path is correct (`/api/rag/query`)

2. **Authentication Error**
   - Verify `VITE_API_KEY` is set correctly
   - Check the `X-API-Key` header is being sent

3. **CORS Error**
   - Ensure your domain is allowed in the API's CORS configuration
   - Check for any proxy settings in your Astro config

4. **Environment Variables**
   - In Astro/Vite, environment variables must start with `VITE_`
   - Restart the dev server after changing `.env`
   - Use `import.meta.env.VITE_*` to access variables

## Best Practices
1. Store API key securely
2. Implement proper error handling
3. Add loading states for better UX
4. Cache responses when appropriate
5. Add retry logic for failed requests
6. Implement proper TypeScript types
7. Use environment variables for configuration
8. Log API URLs during development
9. Handle trailing slashes in URLs
10. Provide fallback values for environment variables 