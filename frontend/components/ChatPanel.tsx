"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";


export default function ChatPanel({ packet, onClose }: { packet: any; onClose: () => void }) {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { role: "user", content: input }];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: input, packet }),
      });
      const data = await res.json();
      
      setMessages([
        ...newMessages,
        { role: "assistant", content: data.response || "No response" },
      ]);
    } catch (err) {
      console.error(err);
      setMessages([...newMessages, { role: "assistant", content: "⚠️ Error contacting agent." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed right-0 top-0 h-screen w-1/2 bg-gray-900 border-l border-gray-700 flex flex-col z-50">
      <div className="flex justify-between items-center p-4 border-b border-gray-700">
        <h2 className="text-lg font-semibold text-white"> Chat with Agent</h2>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-200">✕</button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg, i) => (

          <div
            key={i}
            className={`p-3 rounded-xl max-w-[80%] ${
              msg.role === "user"
                ? "ml-auto bg-blue-600 text-white"
                : "mr-auto bg-gray-800 text-gray-100"
            }`}
          >
            
            {msg.role === "assistant" ? (
        <ReactMarkdown >
          {msg.content}
        </ReactMarkdown>
      ) : (
        msg.content
      )}
          </div>
        ))}
        {loading && <div className="text-gray-400 text-sm">Thinking...</div>}
      </div>

      <div className="p-4 border-t border-gray-700 flex gap-2">
        <input
          type="text"
          className="flex-1 bg-gray-800 text-gray-100 p-2 rounded-md focus:outline-none"
          placeholder="Ask something..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-md"
        >
          Send
        </button>
      </div>
    </div>
  );
}
