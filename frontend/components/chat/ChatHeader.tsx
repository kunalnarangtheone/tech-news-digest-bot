"use client";

import { MessageSquarePlus } from "lucide-react";

interface ChatHeaderProps {
  onNewConversation: () => void;
}

export function ChatHeader({ onNewConversation }: ChatHeaderProps) {
  return (
    <div className="border-b bg-white dark:bg-gray-900 px-4 py-3">
      <div className="flex items-center justify-between max-w-4xl mx-auto">
        <button
          onClick={onNewConversation}
          className="text-xl font-semibold text-gray-900 dark:text-gray-100
                     hover:text-blue-600 dark:hover:text-blue-400 transition-colors duration-200
                     cursor-pointer"
        >
          AI Adversarial Chatbot
        </button>
        <button
          onClick={onNewConversation}
          className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium
                     text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800
                     transition-colors duration-200"
        >
          <MessageSquarePlus className="h-4 w-4" />
          <span>New Chat</span>
        </button>
      </div>
    </div>
  );
}
