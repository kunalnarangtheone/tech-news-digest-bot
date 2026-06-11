"use client";

import { Send } from "lucide-react";
import { useState, type FormEvent, type KeyboardEvent } from "react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [input, setInput] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput("");
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as unknown as FormEvent);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t bg-white dark:bg-gray-900 p-4">
      <div className="flex gap-2 items-end max-w-4xl mx-auto">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about any tech topic..."
          disabled={disabled}
          rows={1}
          className="flex-1 resize-none rounded-xl border border-gray-300 dark:border-gray-700 px-4 py-3
                     focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                     disabled:opacity-50 disabled:cursor-not-allowed
                     bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                     placeholder:text-gray-500 dark:placeholder:text-gray-400
                     min-h-[48px] max-h-[200px]"
          style={{
            height: "auto",
            minHeight: "48px",
          }}
          onInput={(e) => {
            const target = e.target as HTMLTextAreaElement;
            target.style.height = "auto";
            target.style.height = `${Math.min(target.scrollHeight, 200)}px`;
          }}
        />
        <button
          type="submit"
          disabled={disabled || !input.trim()}
          className="rounded-xl bg-blue-600 px-4 py-3 text-white hover:bg-blue-700
                     disabled:opacity-50 disabled:cursor-not-allowed
                     transition-colors duration-200 h-[48px] flex items-center justify-center"
        >
          <Send className="h-5 w-5" />
        </button>
      </div>
    </form>
  );
}
