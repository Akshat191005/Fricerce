import Link from "next/link";
import { Zap, ArrowLeft } from "lucide-react";
import { SolutionCart } from "@/components/SolutionCart";

export default function ResultsPage() {
  return (
    <main className="min-h-screen bg-gray-50">
      {/* Dark brand header — matches the home page theme */}
      <header className="sticky top-0 z-20 bg-brand-dark border-b border-white/10">
        <div className="max-w-3xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link
            href="/"
            className="flex items-center gap-2 text-white font-bold"
            aria-label="Back to home"
          >
            <span className="flex items-center justify-center w-8 h-8 rounded-lg bg-brand-primary/20 text-brand-primary">
              <Zap className="w-4 h-4" />
            </span>
            <span className="text-sm">Frictionless Commerce</span>
          </Link>

          <Link
            href="/"
            className="
              flex items-center gap-1.5 px-3 py-1.5 rounded-lg
              bg-white/10 text-gray-200 text-sm font-medium
              hover:bg-white/20 hover:text-white transition-colors
            "
          >
            <ArrowLeft className="w-4 h-4" />
            New Search
          </Link>
        </div>
      </header>

      {/* Results */}
      <div className="px-4 pb-20">
        <SolutionCart />
      </div>
    </main>
  );
}
