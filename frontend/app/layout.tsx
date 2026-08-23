import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AgentPay — A2A + x402 + Algorand AI Agent Marketplace',
  description: 'Decentralized Agent-to-Agent marketplace settling real-time AI tasks with x402 micropayments on Algorand TestNet.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#080c14] text-slate-100 antialiased selection:bg-cyan-500/30 selection:text-cyan-200">
        {children}
      </body>
    </html>
  );
}
