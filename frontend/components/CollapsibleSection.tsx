"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Props {
  title: string;
  markdown?: boolean;
  content: string | object;
}

export default function CollapsibleSection({ title, markdown, content }: Props) {
  const [open, setOpen] = useState(true);

  return (
    <section className="mt-8">
      <button
        onClick={() => setOpen(!open)}
        className="flex justify-between items-center w-full bg-gray-800 text-gray-200 px-4 py-3 rounded-lg font-semibold hover:bg-gray-700 transition"
      >
        <span>{title}</span>
        {open ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
      </button>

      {open && (
        <div
          className="
            bg-gray-900 mt-3 p-6 rounded-lg
            text-sm text-gray-100 border border-gray-700
            max-h-128 overflow-y-auto
            leading-relaxed space-y-3
            scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-800
            prose prose-invert prose-pre:bg-gray-800 prose-headings:text-gray-100 prose-a:text-blue-400
          "
        >
          {markdown ? (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {typeof content === "string" ? content : ""}
            </ReactMarkdown>
          ) : (
            <pre className="text-xs text-gray-300">
              {JSON.stringify(content, null, 2)}
            </pre>
          )}
        </div>
      )}
    </section>
  );
}
