"use client";

import { useChat } from "@/hooks/useChat";
import { ChatHeader } from "./ChatHeader";
import { ChatInput } from "./ChatInput";
import { ChatMessage } from "./ChatMessage";
import { useEffect, useRef } from "react";
import { Sparkles } from "lucide-react";

export function ChatInterface() {
  const { messages, isLoading, sendMessage, newConversation } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-950">
      <ChatHeader onNewConversation={newConversation} />

      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-4xl mx-auto">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="mb-6 p-4 rounded-full bg-blue-100 dark:bg-blue-900/20">
                <Sparkles className="h-12 w-12 text-blue-600 dark:text-blue-400" />
              </div>
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
                Welcome to Tech Digest AI
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-8 max-w-md">
                Ask me about any tech topic, programming language, framework, or
                recent tech news. I'll research and provide you with a comprehensive
                digest.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-2xl">
                <button
                  onClick={() => sendMessage("What is Rust programming language?")}
                  className="text-left p-4 rounded-xl border border-gray-200 dark:border-gray-800
                           hover:border-blue-500 dark:hover:border-blue-500 hover:bg-white dark:hover:bg-gray-900
                           transition-all duration-200 group"
                >
                  <div className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">
                    What is Rust?
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-500">
                    Learn about the Rust programming language
                  </div>
                </button>
                <button
                  onClick={() =>
                    sendMessage("Explain Next.js App Router vs Pages Router")
                  }
                  className="text-left p-4 rounded-xl border border-gray-200 dark:border-gray-800
                           hover:border-blue-500 dark:hover:border-blue-500 hover:bg-white dark:hover:bg-gray-900
                           transition-all duration-200 group"
                >
                  <div className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">
                    Next.js App vs Pages Router
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-500">
                    Compare Next.js routing approaches
                  </div>
                </button>
                <button
                  onClick={() =>
                    sendMessage("What are the latest AI developments in 2026?")
                  }
                  className="text-left p-4 rounded-xl border border-gray-200 dark:border-gray-800
                           hover:border-blue-500 dark:hover:border-blue-500 hover:bg-white dark:hover:bg-gray-900
                           transition-all duration-200 group"
                >
                  <div className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">
                    Latest AI News
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-500">
                    Discover recent AI breakthroughs
                  </div>
                </button>
                <button
                  onClick={() => sendMessage("Compare React vs Vue.js in 2026")}
                  className="text-left p-4 rounded-xl border border-gray-200 dark:border-gray-800
                           hover:border-blue-500 dark:hover:border-blue-500 hover:bg-white dark:hover:bg-gray-900
                           transition-all duration-200 group"
                >
                  <div className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">
                    React vs Vue.js
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-500">
                    Framework comparison
                  </div>
                </button>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message, index) => (
                <ChatMessage key={index} message={message} />
              ))}
              {isLoading && messages[messages.length - 1]?.role === "user" && (
                <div className="flex justify-start mb-4">
                  <div className="bg-gray-100 dark:bg-gray-800 rounded-2xl px-4 py-3">
                    <div className="flex gap-1">
                      <div
                        className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                        style={{ animationDelay: "0ms" }}
                      ></div>
                      <div
                        className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                        style={{ animationDelay: "150ms" }}
                      ></div>
                      <div
                        className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                        style={{ animationDelay: "300ms" }}
                      ></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>
      </div>

      <ChatInput onSend={sendMessage} disabled={isLoading} />
    </div>
  );
}
