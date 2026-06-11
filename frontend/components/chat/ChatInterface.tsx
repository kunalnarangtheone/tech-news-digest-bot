"use client";

import { useChat } from "@/hooks/useChat";
import { ChatHeader } from "./ChatHeader";
import { ChatInput } from "./ChatInput";
import { ChatMessage } from "./ChatMessage";
import { useEffect, useRef } from "react";
import { Sparkles } from "lucide-react";

export function ChatInterface() {
  const { messages, isLoading, status, sendMessage, newConversation } = useChat();
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
                Welcome to AI Adversarial Chatbot
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-8 max-w-md">
                I analyze tech topics from multiple perspectives using an adversarial
                research approach. Get balanced insights with pros, cons, and different
                viewpoints on any technology decision.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-2xl">
                <button
                  onClick={() => sendMessage("Should I choose Rust or Go for my backend?")}
                  className="text-left p-4 rounded-xl border border-gray-200 dark:border-gray-800
                           hover:border-blue-500 dark:hover:border-blue-500 hover:bg-white dark:hover:bg-gray-900
                           transition-all duration-200 group"
                >
                  <div className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">
                    Rust or Go for Backend?
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-500">
                    Compare pros and cons from different perspectives
                  </div>
                </button>
                <button
                  onClick={() =>
                    sendMessage("React vs Vue.js: Which should I choose?")
                  }
                  className="text-left p-4 rounded-xl border border-gray-200 dark:border-gray-800
                           hover:border-blue-500 dark:hover:border-blue-500 hover:bg-white dark:hover:bg-gray-900
                           transition-all duration-200 group"
                >
                  <div className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">
                    React vs Vue.js?
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-500">
                    Analyze tradeoffs from multiple viewpoints
                  </div>
                </button>
                <button
                  onClick={() =>
                    sendMessage("Is serverless architecture right for my project?")
                  }
                  className="text-left p-4 rounded-xl border border-gray-200 dark:border-gray-800
                           hover:border-blue-500 dark:hover:border-blue-500 hover:bg-white dark:hover:bg-gray-900
                           transition-all duration-200 group"
                >
                  <div className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">
                    Serverless Architecture?
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-500">
                    Evaluate benefits and drawbacks from different angles
                  </div>
                </button>
                <button
                  onClick={() => sendMessage("Microservices vs Monolithic architecture?")}
                  className="text-left p-4 rounded-xl border border-gray-200 dark:border-gray-800
                           hover:border-blue-500 dark:hover:border-blue-500 hover:bg-white dark:hover:bg-gray-900
                           transition-all duration-200 group"
                >
                  <div className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">
                    Microservices vs Monolith?
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-500">
                    Weigh competing perspectives and real-world tradeoffs
                  </div>
                </button>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message, index) => (
                message.content ? <ChatMessage key={index} message={message} /> : null
              ))}
              {isLoading && status && (
                <div className="flex justify-start mb-4">
                  <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-2xl px-4 py-3">
                    <div className="flex items-center gap-2 text-sm text-blue-700 dark:text-blue-300">
                      <div className="flex gap-1">
                        <div
                          className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce"
                          style={{ animationDelay: "0ms" }}
                        ></div>
                        <div
                          className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce"
                          style={{ animationDelay: "150ms" }}
                        ></div>
                        <div
                          className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce"
                          style={{ animationDelay: "300ms" }}
                        ></div>
                      </div>
                      <span>{status}</span>
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
