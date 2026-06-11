"use client";

import { useCallback, useState } from "react";
import { api } from "@/lib/api";
import {
  clearSessionId,
  getSessionId,
  setSessionId,
} from "@/lib/session";
import type { Message } from "@/types/chat";

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionIdState] = useState<string | null>(() =>
    getSessionId()
  );

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim()) return;

      setIsLoading(true);

      // Add user message to UI immediately
      const userMessage: Message = { role: "user", content };
      setMessages((prev) => [...prev, userMessage]);

      // Get or create session
      let currentSessionId = sessionId;
      if (!currentSessionId) {
        try {
          const session = await api.createSession();
          currentSessionId = session.session_id;
          setSessionId(currentSessionId);
          setSessionIdState(currentSessionId);
        } catch (error) {
          console.error("Failed to create session:", error);
          setIsLoading(false);
          return;
        }
      }

      // Stream response
      let assistantContent = "";
      const assistantMessage: Message = { role: "assistant", content: "" };
      setMessages((prev) => [...prev, assistantMessage]);

      try {
        for await (const event of api.chatStream({
          message: content,
          session_id: currentSessionId,
        })) {
          if (event.type === "session") {
            // Update session ID if server returned a new one
            if (event.content !== currentSessionId) {
              currentSessionId = event.content;
              setSessionId(currentSessionId);
              setSessionIdState(currentSessionId);
            }
          } else if (event.type === "token") {
            assistantContent += event.content;
            setMessages((prev) => {
              const updated = [...prev];
              updated[updated.length - 1] = {
                role: "assistant",
                content: assistantContent,
              };
              return updated;
            });
          } else if (event.type === "error") {
            console.error("Error from server:", event.content);
            setMessages((prev) => {
              const updated = [...prev];
              updated[updated.length - 1] = {
                role: "assistant",
                content: `Error: ${event.content}`,
              };
              return updated;
            });
          }
        }
      } catch (error) {
        console.error("Error streaming response:", error);
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            role: "assistant",
            content: "Sorry, an error occurred while processing your request.",
          };
          return updated;
        });
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId]
  );

  const newConversation = useCallback(async () => {
    if (sessionId) {
      try {
        await api.deleteSession(sessionId);
      } catch (error) {
        console.error("Failed to delete session:", error);
      }
    }
    clearSessionId();
    setSessionIdState(null);
    setMessages([]);
  }, [sessionId]);

  return {
    messages,
    isLoading,
    sendMessage,
    newConversation,
  };
}
