# React Integration Example

## Chat Component

Here's a simple React component that interacts with the RAG API:

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
  apiUrl: string;
  apiKey: string;
}

export const RagChat: React.FC<ChatProps> = ({ apiUrl, apiKey }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async (message: string) => {
    try {
      setLoading(true);
      
      // Add user message
      setMessages(prev => [...prev, { role: 'user', content: message }]);
      
      // Send request to API
      const response = await fetch(`${apiUrl}/api/rag/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': apiKey,
        },
        body: JSON.stringify({
          message,
          conversation_id: 'optional-conversation-id',
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to get response');
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
    <div className="flex flex-col h-[600px] w-full max-w-2xl mx-auto">
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
                <details>
                  <summary>Sources</summary>
                  <ul className="mt-1 list-disc list-inside">
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
      </div>
      
      {/* Input form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (input.trim() && !loading) {
            sendMessage(input.trim());
          }
        }}
        className="p-4 border-t"
      >
        <div className="flex space-x-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            className="flex-1 p-2 border rounded-lg"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
};
```

## Usage

1. Install the component in your React/Next.js/Astro project:

```bash
# If using TypeScript
npm install @types/react @types/react-dom

# If using Tailwind (for styling)
npm install -D tailwindcss
```

2. Use the component:

```tsx
// pages/index.tsx or App.tsx
import { RagChat } from './components/RagChat';

export default function Home() {
  return (
    <main className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Chat with our Documentation</h1>
      
      <RagChat
        apiUrl="http://localhost:8000"
        apiKey="your-api-key"
      />
    </main>
  );
}
```

3. Environment Variables:

Create a `.env.local` file:

```env
NEXT_PUBLIC_RAG_API_URL=http://localhost:8000
NEXT_PUBLIC_RAG_API_KEY=your-api-key
```

## Features

- Real-time chat interface
- Source attribution with collapsible details
- Loading states
- Error handling
- Rate limiting handling
- Mobile-responsive design
- Accessible UI elements

## Styling

The component uses Tailwind CSS for styling. Make sure to include Tailwind in your project or replace the classes with your preferred styling solution. 