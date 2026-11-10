"use client";

import { useState } from "react";
import Sidebar, { View } from "@/components/Sidebar";
import PaperLibrary from "@/components/PaperLibrary";
import ChatInterface from "@/components/ChatInterface";
import ComparisonScreen from "@/components/ComparisonScreen";

export default function Dashboard() {
  const [view, setView] = useState<View>("library");

  return (
    <div className="flex min-h-screen">
      <Sidebar view={view} onChangeView={setView} />
      <main className="flex-1">
        {view === "library" && <PaperLibrary />}
        {view === "chat" && <ChatInterface />}
        {view === "compare" && <ComparisonScreen />}
      </main>
    </div>
  );
}
