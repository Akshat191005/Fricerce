/**
 * Zustand store for the streaming cart state.
 * Receives SSE chunks from POST /api/chat and appends items as they arrive.
 */
import { create } from "zustand";
import { UnifiedItem, ChatRequest } from "@/types";

interface CartState {
  items: UnifiedItem[];
  isLoading: boolean;
  error: string | null;
  prompt: string;
  addItem: (item: UnifiedItem) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setPrompt: (prompt: string) => void;
  reset: () => void;
  streamCart: (request: ChatRequest) => Promise<void>;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
// Lambda/API Gateway can't stream SSE — use batch JSON mode for non-localhost
const USE_BATCH = !API_BASE_URL.includes("localhost");

export const useCartStore = create<CartState>((set, get) => ({
  items: [],
  isLoading: false,
  error: null,
  prompt: "",

  addItem: (item) =>
    set((state) => {
      const exists = state.items.some((i) => i.sku === item.sku);
      if (exists) return state;
      return { items: [...state.items, item] };
    }),

  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  setPrompt: (prompt) => set({ prompt }),

  reset: () => set({ items: [], isLoading: false, error: null }),

  streamCart: async (request: ChatRequest) => {
    const { reset, addItem, setLoading, setError } = get();
    reset();
    setLoading(true);

    // ── Batch mode (Lambda / API Gateway) ──────────────────────────────
    if (USE_BATCH) {
      try {
        const response = await fetch(`${API_BASE_URL}/api/chat/batch`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(request),
        });
        if (!response.ok) {
          throw new Error(`API error: ${response.status} ${response.statusText}`);
        }
        const data = await response.json();
        if (data.error) {
          setError(data.error);
          return;
        }
        for (const item of data.items as UnifiedItem[]) {
          addItem(item);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
      return;
    }

    // ── SSE streaming mode (local uvicorn) ─────────────────────────────
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error("No response body");

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const payload = line.slice(6).trim();
          if (payload === "[DONE]") {
            setLoading(false);
            return;
          }
          try {
            const item: UnifiedItem = JSON.parse(payload);
            if ("error" in item) {
              setError((item as unknown as { error: string }).error);
              return;
            }
            addItem(item);
          } catch {
            // Skip malformed lines
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  },
}));
