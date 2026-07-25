"use client";
import { useState, useRef, useEffect } from "react";
import { streamChat } from "@/lib/api";
import { Send, Bot, User as UserIcon, Sparkles, RefreshCw } from "lucide-react";
import ReactMarkdown from "react-markdown";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function MentorPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hello! I'm your **SkillBridge AI Career Mentor**. Ask me anything about skills to learn, resume tips, project ideas, or interview guidance!",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const isProcessingRef = useRef(false); // Prevent duplicate calls

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading || isProcessingRef.current) return;

    // Prevent duplicate calls
    isProcessingRef.current = true;

    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    // Create a single placeholder for the assistant response
    const assistantMessageIndex = messages.length + 1;
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

    try {
      await streamChat(
        userMsg,
        sessionId,
        (chunk) => {
          // Update the assistant message by replacing it completely
          setMessages((prev) => {
            const updated = [...prev];
            const lastMsg = updated[updated.length - 1];
            if (lastMsg && lastMsg.role === "assistant") {
              // Append chunk to existing content
              return [
                ...updated.slice(0, -1),
                { ...lastMsg, content: lastMsg.content + chunk }
              ];
            }
            return updated;
          });
        },
        (sid) => {
          setSessionId(sid);
          setLoading(false);
          isProcessingRef.current = false;
        }
      );
      
      setLoading(false);
      isProcessingRef.current = false;
    } catch (err) {
      console.error(err);
      setMessages((prev) => {
        const updated = [...prev];
        const lastMsg = updated[updated.length - 1];
        if (lastMsg && lastMsg.role === "assistant" && lastMsg.content === "") {
          return [
            ...updated.slice(0, -1),
            { ...lastMsg, content: "Sorry, I ran into an error connecting to Groq AI." }
          ];
        }
        return updated;
      });
      setLoading(false);
      isProcessingRef.current = false;
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-5xl mx-auto p-4 md:p-8">
      <div className="mb-4">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Bot className="text-[var(--blue)]" /> AI Career Mentor
        </h1>
        <p className="text-xs text-[var(--subtext)]">Powered by Groq LLM (Llama 3.3 70B)</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-2 mb-4">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex gap-3 ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            {m.role === "assistant" && (
              <div className="w-8 h-8 rounded-lg bg-[var(--surface0)] flex items-center justify-center text-[var(--blue)] shrink-0 mt-1">
                <Bot size={18} />
              </div>
            )}
            <div
              className={`max-w-2xl p-4 rounded-2xl text-sm ${
                m.role === "user"
                  ? "bg-[var(--blue)] text-[var(--crust)] font-medium rounded-tr-none"
                  : "glass rounded-tl-none prose-dark"
              }`}
            >
              {m.role === "user" ? (
                m.content
              ) : (
                <ReactMarkdown>{m.content || "..."}</ReactMarkdown>
              )}
            </div>
            {m.role === "user" && (
              <div className="w-8 h-8 rounded-lg bg-[var(--gradient-primary)] flex items-center justify-center text-[var(--crust)] font-bold shrink-0 mt-1">
                U
              </div>
            )}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSend} className="glass p-2 rounded-xl flex items-center gap-2">
        <input
          type="text"
          className="input border-none bg-transparent focus:ring-0"
          placeholder="Ask your mentor (e.g. 'How do I prepare for SDE internships?')..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button
          type="submit"
          disabled={!input.trim() || loading}
          className="btn-primary py-2 px-4 shrink-0"
        >
          {loading ? <RefreshCw size={16} className="animate-spin" /> : <Send size={16} />}
        </button>
      </form>
    </div>
  );
}
