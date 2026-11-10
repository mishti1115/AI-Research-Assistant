"use client";

import { BookOpen, MessagesSquare, Scale, Library, Sun, Moon } from "lucide-react";
import { useEffect, useState } from "react";

export type View = "library" | "chat" | "compare";

const NAV: { id: View; label: string; icon: React.ElementType }[] = [
  { id: "library", label: "Paper Library", icon: Library },
  { id: "chat", label: "Chat", icon: MessagesSquare },
  { id: "compare", label: "Compare", icon: Scale },
];

export default function Sidebar({
  view,
  onChangeView,
}: {
  view: View;
  onChangeView: (v: View) => void;
}) {
  const [isLight, setIsLight] = useState(false);

  useEffect(() => {
    const root = document.documentElement;
    root.classList.toggle("light", isLight);
    root.classList.toggle("dark", !isLight);
  }, [isLight]);

  return (
    <aside className="w-60 shrink-0 border-r hairline flex flex-col h-screen sticky top-0">
      <div className="px-5 py-6 border-b hairline">
        <div className="flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-brass-500" />
          <span className="font-display text-lg tracking-tight">The Reading Room</span>
        </div>
        <p className="text-xs mt-1 opacity-60 font-body">AI Research Paper Assistant</p>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => onChangeView(id)}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-sm transition-colors ${
              view === id
                ? "bg-brass-500/15 text-brass-400 font-medium"
                : "opacity-70 hover:opacity-100 hover:bg-ink-800/60"
            }`}
          >
            <Icon className="w-4 h-4" />
            {label}
          </button>
        ))}
      </nav>

      <div className="px-3 py-4 border-t hairline">
        <button
          onClick={() => setIsLight((v) => !v)}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-sm opacity-70 hover:opacity-100 hover:bg-ink-800/60 transition-colors"
        >
          {isLight ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
          {isLight ? "Dark mode" : "Light mode"}
        </button>
      </div>
    </aside>
  );
}
