"use client";

import { useRouter } from "next/navigation";
import { useCartStore } from "@/store/useCartStore";

const EXAMPLES = [
  "Reorder my mouse",
  "Something for a camping trip under $100",
  "Healthy snacks for late-night coding",
  "Birthday gift ideas, deliver by tomorrow",
  "A warm jacket but not red",
];

export function ExamplePrompts() {
  const router = useRouter();
  const { setPrompt, streamCart } = useCartStore();

  const run = (prompt: string) => {
    setPrompt(prompt);
    router.push("/results");
    streamCart({ prompt, user_id: "USER#123", urgent: false });
  };

  return (
    <div className="mt-8 flex flex-wrap items-center justify-center gap-2">
      <span className="text-xs text-gray-500 mr-1">Try:</span>
      {EXAMPLES.map((ex) => (
        <button
          key={ex}
          type="button"
          onClick={() => run(ex)}
          className="
            px-3 py-1.5 rounded-full text-xs font-medium
            bg-white/5 text-gray-300 border border-white/10
            hover:bg-white/10 hover:text-white hover:border-white/20
            transition-all duration-150
          "
        >
          {ex}
        </button>
      ))}
    </div>
  );
}
