"use client";

import { ShoppingCart, Loader2, AlertCircle, Sparkles } from "lucide-react";
import { useCartStore } from "@/store/useCartStore";
import { ProductCard } from "./ProductCard";

export function SolutionCart() {
  const { items, isLoading, error, prompt } = useCartStore();

  const hasContent = items.length > 0 || isLoading || error;

  if (!hasContent) {
    return (
      <div className="w-full max-w-3xl mx-auto mt-24 text-center">
        <div className="flex flex-col items-center gap-3 text-gray-400">
          <ShoppingCart className="w-14 h-14 opacity-20" aria-hidden="true" />
          <p className="text-sm">
            Search above and your AI suggestions will appear here.
          </p>
        </div>
      </div>
    );
  }

  // Split by source for nicer grouping
  const reorders = items.filter((i) => i.source_database === "dynamodb_history");
  const discoveries = items.filter((i) => i.source_database === "pinecone_semantic");

  return (
    <section
      className="w-full max-w-3xl mx-auto mt-6"
      aria-label="Smart cart results"
      aria-live="polite"
      aria-busy={isLoading}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-brand-primary" aria-hidden="true" />
          <h2 className="text-xl font-bold text-gray-900">Your Smart Cart</h2>
          {items.length > 0 && (
            <span className="px-2 py-0.5 bg-brand-primary/10 text-brand-primary text-xs font-semibold rounded-full">
              {items.length} item{items.length !== 1 ? "s" : ""}
            </span>
          )}
        </div>
        {isLoading && (
          <span className="flex items-center gap-1.5 text-sm text-gray-400">
            <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
            <span>Searching…</span>
          </span>
        )}
      </div>

      {prompt && (
        <p className="mb-5 text-sm text-gray-500 italic">&ldquo;{prompt}&rdquo;</p>
      )}

      {error && (
        <div
          role="alert"
          className="flex items-start gap-3 p-4 mb-4 rounded-xl bg-red-50 border border-red-200"
        >
          <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" aria-hidden="true" />
          <div>
            <p className="text-sm font-semibold text-red-700">Something went wrong</p>
            <p className="text-xs text-red-600 mt-0.5">{error}</p>
          </div>
        </div>
      )}

      {/* Loading skeletons */}
      {isLoading && items.length === 0 && (
        <div className="flex flex-col gap-3" aria-label="Loading results">
          {[1, 2, 3].map((n) => (
            <div key={n} className="h-32 rounded-xl bg-gray-100 animate-pulse" aria-hidden="true" />
          ))}
        </div>
      )}

      {/* Reorders group */}
      {reorders.length > 0 && (
        <div className="mb-6">
          <h3 className="text-xs font-semibold uppercase tracking-wide text-badge-history mb-2">
            ⚡ Instant Reorders
          </h3>
          <div className="flex flex-col gap-3">
            {reorders.map((item) => (
              <ProductCard key={item.sku} item={item} />
            ))}
          </div>
        </div>
      )}

      {/* Discoveries group */}
      {discoveries.length > 0 && (
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-wide text-badge-semantic mb-2">
            ✨ AI Discoveries
          </h3>
          <div className="flex flex-col gap-3">
            {discoveries.map((item) => (
              <ProductCard key={item.sku} item={item} />
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
