"use client";

import { useRef, useEffect, useState, KeyboardEvent } from "react";
import { useRouter } from "next/navigation";
import { Zap, Send, Loader2 } from "lucide-react";
import { useCartStore } from "@/store/useCartStore";

interface PromptBarProps {
  userId?: string;
  /** When true, navigate to /results after submitting (used on home page) */
  navigateOnSubmit?: boolean;
  /** Compact styling for the results page header */
  compact?: boolean;
}

export function PromptBar({
  userId = "USER#123",
  navigateOnSubmit = false,
  compact = false,
}: PromptBarProps) {
  const router = useRouter();
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [localPrompt, setLocalPrompt] = useState("");
  const [urgent, setUrgent] = useState(false);

  const { streamCart, isLoading, setPrompt } = useCartStore();

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
  }, [localPrompt]);

  const handleSubmit = async () => {
    const trimmed = localPrompt.trim();
    if (!trimmed || isLoading) return;
    setPrompt(trimmed);
    if (navigateOnSubmit) {
      router.push("/results");
    }
    // Fire the search (store persists across the client-side navigation)
    streamCart({ prompt: trimmed, user_id: userId, urgent });
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto">
      <div
        className={`
          relative flex items-end gap-2 rounded-2xl border-2 bg-white
          transition-all duration-200
          ${compact ? "p-2 shadow-md" : "p-3 shadow-xl"}
          ${urgent
            ? "border-amber-400 shadow-amber-100"
            : "border-gray-200 focus-within:border-brand-primary"
          }
        `}
      >
        <textarea
          ref={textareaRef}
          value={localPrompt}
          onChange={(e) => setLocalPrompt(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="What do you need today? (e.g. 'Reorder my mouse and find something for my camping trip')"
          rows={1}
          disabled={isLoading}
          aria-label="Shopping prompt input"
          className="
            flex-1 resize-none overflow-hidden bg-transparent
            text-gray-900 placeholder-gray-400 text-base leading-relaxed
            focus:outline-none disabled:opacity-50 min-h-[40px] px-2
          "
        />

        <div className="flex items-center gap-2 shrink-0">
          <button
            type="button"
            onClick={() => setUrgent((u) => !u)}
            aria-pressed={urgent}
            aria-label="Toggle urgent delivery"
            title="Urgent: prioritize fastest delivery"
            className={`
              flex items-center gap-1 px-3 py-1.5 rounded-full text-sm font-medium
              transition-all duration-150 select-none
              ${urgent
                ? "bg-amber-400 text-amber-900 shadow-inner"
                : "bg-gray-100 text-gray-500 hover:bg-gray-200"
              }
            `}
          >
            <Zap className="w-3.5 h-3.5" aria-hidden="true" />
            <span>Urgent</span>
          </button>

          <button
            type="button"
            onClick={handleSubmit}
            disabled={!localPrompt.trim() || isLoading}
            aria-label="Submit shopping prompt"
            className="
              flex items-center justify-center w-10 h-10 rounded-xl
              bg-brand-primary text-white font-medium
              hover:bg-orange-500 active:scale-95 transition-all
              disabled:opacity-40 disabled:cursor-not-allowed disabled:active:scale-100
            "
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
            ) : (
              <Send className="w-4 h-4" aria-hidden="true" />
            )}
          </button>
        </div>
      </div>

      {!compact && (
        <p className="mt-3 text-center text-xs text-gray-400">
          Press <kbd className="px-1.5 py-0.5 bg-gray-100 rounded text-gray-500">Enter</kbd> to search &nbsp;·&nbsp;
          <kbd className="px-1.5 py-0.5 bg-gray-100 rounded text-gray-500">Shift+Enter</kbd> for new line
        </p>
      )}
    </div>
  );
}
