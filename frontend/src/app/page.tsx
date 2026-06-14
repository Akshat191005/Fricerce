import { PromptBar } from "@/components/PromptBar";
import { ExamplePrompts } from "@/components/ExamplePrompts";
import { Zap } from "lucide-react";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-brand-dark via-brand-dark to-gray-900 flex flex-col">
      {/* Centered hero */}
      <div className="flex-1 flex flex-col items-center justify-center px-4 py-16">
        <div className="w-full max-w-3xl mx-auto text-center">
          {/* Logo / title */}
          <div className="flex items-center justify-center gap-2 mb-3">
            <span className="flex items-center justify-center w-12 h-12 rounded-2xl bg-brand-primary/20 text-brand-primary">
              <Zap className="w-7 h-7" />
            </span>
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight text-white mb-3">
            Frictionless Commerce
          </h1>
          <p className="text-gray-400 text-base sm:text-lg mb-10 max-w-xl mx-auto">
            Your AI shopping copilot. Describe what you need in plain words —
            reorders and discoveries, found instantly.
          </p>

          {/* Search bar */}
          <PromptBar navigateOnSubmit />

          {/* Example prompts */}
          <ExamplePrompts />
        </div>
      </div>

      {/* Footer tagline */}
      <footer className="text-center py-6 text-gray-500 text-xs">
        Dual-path engine · DynamoDB reorders + Pinecone discovery · Powered by Groq
      </footer>
    </main>
  );
}
