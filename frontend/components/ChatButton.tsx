"use client";

import { MessageCircle } from "lucide-react";

export default function ChatButton({ onClick }: { onClick?: () => void }) {
  return (
    
    <button
      onClick={onClick}
      className="
        fixed bottom-6 left-1/2 transform -translate-x-1/2
        bg-gray-900/80 backdrop-blur-md
        border border-blue-500/30
        text-blue-400 font-medium
        px-6 py-3 rounded-full
        shadow-lg shadow-blue-900/30
        flex items-center gap-2
        hover:bg-blue-950/70 hover:text-blue-300 hover:border-blue-400
        transition-all duration-300 ease-in-out
        z-50
      "
    >
      <MessageCircle size={20} className="text-blue-400" />
      Chat with Agent
    </button>
    
  );
}
