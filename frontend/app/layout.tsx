import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ResearchMate — Autonomous Academic Literature Review Assistant",
  description: "Self-RAG powered literature reviews with zero hallucinations, dynamic citation networks, and instant PowerPoint/PDF exports.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased overflow-hidden select-none bg-slate-950 text-slate-100 h-screen max-h-screen">
        {/* Neon decorative background blurs */}
        <div className="absolute top-[-10%] left-[-10%] w-[45%] h-[45%] rounded-full bg-emerald-500 neon-glow" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[45%] h-[45%] rounded-full bg-indigo-500 neon-glow" />
        
        {children}
      </body>
    </html>
  );
}
