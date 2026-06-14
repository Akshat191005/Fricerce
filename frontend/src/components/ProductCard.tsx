"use client";

import { Clock, Package, Database, Brain } from "lucide-react";
import type { UnifiedItem } from "@/types";

interface ProductCardProps {
  item: UnifiedItem;
}

export function ProductCard({ item }: ProductCardProps) {
  const isDynamo = item.source_database === "dynamodb_history";

  return (
    <article
      className="
        flex gap-4 p-4 bg-white rounded-2xl border border-gray-100
        shadow-sm hover:shadow-lg hover:border-gray-200 transition-all duration-200
        animate-slide-in
      "
      aria-label={`Product: ${item.name}`}
    >
      {/* Product image */}
      <div className="relative w-24 h-24 shrink-0 rounded-xl overflow-hidden bg-gray-100 flex items-center justify-center">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={item.image_url}
          alt={item.name}
          width={96}
          height={96}
          className="w-full h-full object-cover"
          onError={(e) => {
            const name = encodeURIComponent(item.name.slice(0, 20));
            (e.currentTarget as HTMLImageElement).src =
              `https://placehold.co/96x96/e2e8f0/64748b?text=${name}`;
          }}
        />
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        {/* Source badge + context badge */}
        <div className="flex flex-wrap items-center gap-2 mb-1.5">
          {/* Source database indicator */}
          <span
            className={`
              inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold
              ${isDynamo
                ? "bg-blue-50 text-badge-history border border-blue-200"
                : "bg-green-50 text-badge-semantic border border-green-200"
              }
            `}
            aria-label={`Source: ${isDynamo ? "Purchase History" : "AI Discovery"}`}
          >
            {isDynamo ? (
              <Database className="w-3 h-3" aria-hidden="true" />
            ) : (
              <Brain className="w-3 h-3" aria-hidden="true" />
            )}
            <span>{isDynamo ? "History" : "AI Found"}</span>
          </span>

          {/* Context badge — the key UX element */}
          <span
            className="
              inline-flex items-center px-2 py-0.5 rounded-full
              bg-brand-light/30 text-amber-800 text-xs font-medium
              border border-amber-200 truncate max-w-xs
            "
            title={item.context_badge}
          >
            {item.context_badge}
          </span>
        </div>

        {/* Product name */}
        <h3 className="font-semibold text-gray-900 text-sm leading-snug truncate">
          {item.name}
        </h3>

        {/* Brand */}
        <p className="text-xs text-gray-500 mt-0.5">{item.brand}</p>

        {/* Description */}
        <p className="text-xs text-gray-600 mt-1 line-clamp-2">
          {item.description}
        </p>

        {/* Price + delivery */}
        <div className="flex items-center gap-4 mt-2">
          <span className="text-lg font-bold text-gray-900">
            ${item.price.toFixed(2)}
          </span>
          <span className="flex items-center gap-1 text-xs text-gray-500">
            <Clock className="w-3 h-3" aria-hidden="true" />
            {item.delivery_time_hours < 24
              ? `${item.delivery_time_hours}h delivery`
              : `${Math.round(item.delivery_time_hours / 24)}d delivery`}
          </span>
          <span className="flex items-center gap-1 text-xs text-gray-500">
            <Package className="w-3 h-3" aria-hidden="true" />
            {item.stock_quantity} in stock
          </span>
        </div>
      </div>

      {/* Add to cart */}
      <div className="shrink-0 self-center">
        <button
          type="button"
          aria-label={`Add ${item.name} to cart`}
          className="
            px-4 py-2 rounded-lg bg-brand-primary text-white
            text-sm font-semibold hover:bg-orange-500 active:scale-95
            transition-all duration-150 whitespace-nowrap
          "
        >
          Add to Cart
        </button>
      </div>
    </article>
  );
}
