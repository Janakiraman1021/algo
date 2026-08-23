'use client';

import React, { useState, useEffect } from 'react';
import { 
  Bot, 
  Zap, 
  Coins, 
  CheckCircle2, 
  ArrowRight, 
  ExternalLink, 
  RefreshCw, 
  Copy, 
  Check, 
  Layers, 
  Activity, 
  ShieldCheck, 
  FileText, 
  Send, 
  Cpu, 
  Database,
  Globe,
  Sparkles
} from 'lucide-react';
import { 
  fetchStats, 
  fetchAgents, 
  submitTask, 
  checkBackendHealth, 
  AgentInfo, 
  StatsResponse, 
  TaskResponse 
} from '../lib/api';

const SAMPLE_PROMPTS = [
  {
    title: 'Web3 AI Economy',
    text: 'Autonomous AI agents require machine-to-machine financial rails without traditional human credit card barriers. Algorand provides sub-3-second finality with sub-cent transaction fees, making it the premier settlement layer for AI agent micropayments through the x402 HTTP payment standard.'
  },
  {
    title: 'Algorand Puya Architecture',
    text: 'Algorand Python (PuyaPy) allows developers to author native Algorand smart contracts directly in Python with full ARC-4 and ARC-56 ABI compatibility. The contracts compile to optimized TEAL bytecode, offering type-safe box storage, global state tracking, and deterministic on-chain execution.'
  },
  {
    title: 'x402 Micropayment Protocol',
    text: 'The x402 protocol leverages the standard HTTP 402 Payment Required status code to enable pay-per-request API services. When a buyer agent queries a protected endpoint, the server responds with payment parameters, the client signs an Algorand transfer, and retries the request with cryptographic proof.'
  }
];

export default function AgentPayMarketplace() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [inputText, setInputText] = useState(SAMPLE_PROMPTS[0].text);
  const [currentTask, setCurrentTask] = useState<TaskResponse | null>(null);
  const [taskHistory, setTaskHistory] = useState<TaskResponse[]>([]);
  const [copied, setCopied] = useState<string | null>(null);
  const [activeStepIndex, setActiveStepIndex] = useState<number>(0);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 8000);
    return () => clearInterval(interval);
  }, []);

  async function loadData() {
    try {
      setLoading(true);
      const [h, s, a] = await Promise.all([
        checkBackendHealth(),
        fetchStats().catch(() => null),
        fetchAgents().catch(() => [])
      ]);
      setHealth(h);
      if (s) setStats(s);
      if (a) setAgents(a);
    } catch (err) {
      console.error('Error loading data:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleRunTask() {
    if (!inputText.trim() || executing) return;
    try {
      setExecuting(true);
      setErrorMsg(null);
      setActiveStepIndex(1);

      // Trigger simulated progress step animations while backend processes real transaction
      const stepTimer1 = setTimeout(() => setActiveStepIndex(3), 600);
      const stepTimer2 = setTimeout(() => setActiveStepIndex(4), 1400);

      const task = await submitTask(inputText, 'summary-agent');
      
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      setActiveStepIndex(7);
      setCurrentTask(task);
      setTaskHistory(prev => [task, ...prev.slice(0, 4)]);
      loadData();
    } catch (err: any) {
      console.error('Task execution error:', err);
      setErrorMsg(err.message || 'Execution failed');
      setActiveStepIndex(0);
    } finally {
      setExecuting(false);
    }
  }

  function copyToClipboard(text: string, key: string) {
    navigator.clipboard.writeText(text);
    setCopied(key);
    setTimeout(() => setCopied(null), 2000);
  }

  return (
    <div className="min-h-screen bg-[#080c14] text-slate-100 pb-20 relative overflow-hidden font-sans">
      {/* Background Ambient Glows */}
      <div className="absolute -top-40 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute top-1/3 right-10 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-20 left-1/3 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />

      {/* ---------------- Navigation Bar ---------------- */}
      <header className="border-b border-cyan-500/10 backdrop-blur-xl sticky top-0 z-50 bg-[#080c14]/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 p-[1px] shadow-lg shadow-cyan-500/20">
              <div className="w-full h-full bg-[#0a0f1d] rounded-xl flex items-center justify-center">
                <Bot className="w-5 h-5 text-cyan-400" />
              </div>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
                  AgentPay
                </span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
                  A2A + x402
                </span>
              </div>
              <p className="text-[10px] text-slate-400">Algorand AI Agent Marketplace</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            {/* Algorand TestNet Status Badge */}
            <div className="hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs text-slate-300">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>Algorand TestNet</span>
              {stats?.app_id ? (
                <a
                  href={`https://lora.algokit.io/testnet/application/${stats.app_id}`}
                  target="_blank"
                  rel="noreferrer"
                  className="text-cyan-400 hover:text-cyan-300 underline font-mono ml-1"
                >
                  App #{stats.app_id}
                </a>
              ) : null}
            </div>

            {/* TestNet Faucet Button */}
            <a
              href="https://bank.testnet.algorand.network/"
              target="_blank"
              rel="noreferrer"
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 text-xs text-cyan-300 transition"
            >
              <Coins className="w-3.5 h-3.5" />
              <span>Get TestNet ALGO</span>
              <ExternalLink className="w-3 h-3 ml-0.5" />
            </a>
          </div>
        </div>
      </header>

      {/* ---------------- Main Content ---------------- */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 space-y-10">
        {/* Hero Section */}
        <section className="text-center space-y-4 max-w-3xl mx-auto">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-500/30 text-cyan-400 text-xs">
            <Sparkles className="w-3.5 h-3.5 animate-spin" />
            <span>Autonomous Machine-to-Machine Micro-Economy</span>
          </div>
          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-white leading-tight">
            AI Agents Paying AI Agents <br />
            <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-indigo-400 bg-clip-text text-transparent">
              via x402 on Algorand
            </span>
          </h1>
          <p className="text-slate-400 text-sm sm:text-base">
            Submit a task from the <strong>Buyer Agent</strong>. The <strong>Summary Agent</strong> challenges with HTTP 402, accepts <strong>0.01 USDC</strong> micropayment settlement on Algorand TestNet, and records task metrics on the <strong>AgentPayRegistry</strong> smart contract.
          </p>
        </section>

        {/* ---------------- Metrics Dashboard ---------------- */}
        <section className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="glass-panel p-4 rounded-2xl border border-slate-800/80 relative overflow-hidden">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-medium">Registered Agents</span>
              <Bot className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="text-2xl font-bold text-white">
              {stats?.total_agents || 1}
            </div>
            <span className="text-[10px] text-cyan-400 font-mono">SummaryAgent Online</span>
          </div>

          <div className="glass-panel p-4 rounded-2xl border border-slate-800/80 relative overflow-hidden">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-medium">Active Services</span>
              <Cpu className="w-4 h-4 text-blue-400" />
            </div>
            <div className="text-2xl font-bold text-white">
              {stats?.total_services || 1}
            </div>
            <span className="text-[10px] text-blue-400 font-mono">Text Summarization</span>
          </div>

          <div className="glass-panel p-4 rounded-2xl border border-slate-800/80 relative overflow-hidden">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-medium">Completed Tasks</span>
              <Activity className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-bold text-emerald-400">
              {stats?.total_tasks || 0}
            </div>
            <span className="text-[10px] text-slate-400 font-mono">Settled on TestNet</span>
          </div>

          <div className="glass-panel p-4 rounded-2xl border border-slate-800/80 relative overflow-hidden">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-medium">Settled Volume</span>
              <Coins className="w-4 h-4 text-purple-400" />
            </div>
            <div className="text-2xl font-bold text-purple-300">
              ${(stats?.total_volume_usd || 0).toFixed(2)} <span className="text-xs text-slate-400">USDC</span>
            </div>
            <span className="text-[10px] text-purple-400 font-mono">x402 Micropayments</span>
          </div>
        </section>

        {/* ---------------- Two-Column Layout: Agent Showcase & Interactive Task Runner ---------------- */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* LEFT: Agent Showcase Card (4 Cols) */}
          <section className="lg:col-span-4 space-y-6">
            <div className="text-xs uppercase tracking-wider font-bold text-slate-400 flex items-center space-x-2">
              <Bot className="w-4 h-4 text-cyan-400" />
              <span>Available Marketplace Agents</span>
            </div>

            <div className="glass-panel-glow p-6 rounded-2xl relative overflow-hidden border border-cyan-500/30">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-500/20 border border-cyan-500/40 flex items-center justify-center">
                    <Bot className="w-6 h-6 text-cyan-300" />
                  </div>
                  <div>
                    <h3 className="font-bold text-white text-lg">Summary Agent</h3>
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                      ● Active & Available
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-extrabold text-cyan-400 font-mono">0.01 USDC</div>
                  <span className="text-[10px] text-slate-400">per summary</span>
                </div>
              </div>

              <p className="text-slate-300 text-xs mt-4 leading-relaxed">
                Autonomous seller agent providing high-precision text summarization with x402 HTTP payment verification and Algorand TestNet settlement.
              </p>

              <div className="mt-5 pt-4 border-t border-slate-800 space-y-2 text-xs">
                <div className="flex justify-between text-slate-400">
                  <span>Network:</span>
                  <span className="text-slate-200 font-medium">Algorand TestNet</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Protocol:</span>
                  <span className="text-cyan-300 font-mono">x402 (HTTP 402)</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Smart Contract:</span>
                  <span className="text-slate-200 font-mono">AgentPayRegistry</span>
                </div>
                <div className="flex items-center justify-between text-slate-400 pt-1">
                  <span>Address:</span>
                  <button
                    onClick={() => copyToClipboard(agents[0]?.address || 'SummaryAgent', 'addr')}
                    className="text-[11px] font-mono text-cyan-400 hover:text-cyan-300 flex items-center space-x-1"
                  >
                    <span>{agents[0]?.address ? `${agents[0].address.slice(0, 6)}...${agents[0].address.slice(-4)}` : 'SummaryAgent'}</span>
                    {copied === 'addr' ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                  </button>
                </div>
              </div>
            </div>

            {/* A2A Architecture Breakdown */}
            <div className="glass-panel p-5 rounded-2xl border border-slate-800/80 space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-1.5">
                <Layers className="w-4 h-4 text-blue-400" />
                <span>A2A + x402 Protocol Flow</span>
              </h4>
              <div className="space-y-2 text-xs text-slate-400">
                <div className="flex items-center space-x-2">
                  <span className="w-5 h-5 rounded-full bg-slate-800 text-cyan-400 flex items-center justify-center font-bold text-[10px]">1</span>
                  <span><strong>BuyerAgent</strong> receives user prompt</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="w-5 h-5 rounded-full bg-slate-800 text-cyan-400 flex items-center justify-center font-bold text-[10px]">2</span>
                  <span>Sends A2A request to <strong>SummaryAgent</strong></span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="w-5 h-5 rounded-full bg-slate-800 text-cyan-400 flex items-center justify-center font-bold text-[10px]">3</span>
                  <span>SummaryAgent replies with <strong>HTTP 402</strong></span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="w-5 h-5 rounded-full bg-slate-800 text-cyan-400 flex items-center justify-center font-bold text-[10px]">4</span>
                  <span>BuyerAgent pays <strong>0.01 USDC</strong> on Algorand</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="w-5 h-5 rounded-full bg-slate-800 text-cyan-400 flex items-center justify-center font-bold text-[10px]">5</span>
                  <span>Request retried with payment proof hash</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="w-5 h-5 rounded-full bg-slate-800 text-cyan-400 flex items-center justify-center font-bold text-[10px]">6</span>
                  <span>Summary returned & smart contract updated</span>
                </div>
              </div>
            </div>
          </section>

          {/* RIGHT: Live Interactive Task Runner & Pipeline Visualizer (8 Cols) */}
          <section className="lg:col-span-8 space-y-6">
            <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-5">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <FileText className="w-4 h-4 text-cyan-400" />
                  <h3 className="font-bold text-white text-base">Execute A2A Task</h3>
                </div>
                <span className="text-xs text-slate-400 font-mono">Price: 0.01 USDC</span>
              </div>

              {/* Sample Prompt Selector Buttons */}
              <div className="space-y-2">
                <span className="text-xs text-slate-400">Quick Test Prompts:</span>
                <div className="flex flex-wrap gap-2">
                  {SAMPLE_PROMPTS.map((prompt, idx) => (
                    <button
                      key={idx}
                      onClick={() => setInputText(prompt.text)}
                      className="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-[11px] text-slate-300 transition"
                    >
                      {prompt.title}
                    </button>
                  ))}
                </div>
              </div>

              {/* Text Input Area */}
              <div className="space-y-2">
                <textarea
                  rows={4}
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="Enter text for the AI Agent to summarize..."
                  className="w-full bg-[#0a0f1d] border border-slate-700 rounded-xl p-3.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition resize-none"
                />
                <div className="flex justify-between items-center text-xs text-slate-500">
                  <span>{inputText.split(/\s+/).filter(Boolean).length} words</span>
                  <span>Target: SummaryAgent</span>
                </div>
              </div>

              {/* Action Trigger Button */}
              <button
                onClick={handleRunTask}
                disabled={executing || !inputText.trim()}
                className={`w-full py-3 px-4 rounded-xl font-bold text-sm flex items-center justify-center space-x-2 transition ${
                  executing
                    ? 'bg-slate-800 text-slate-400 cursor-not-allowed'
                    : 'bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white shadow-lg shadow-cyan-500/20'
                }`}
              >
                {executing ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin text-cyan-400" />
                    <span>Processing A2A x402 Micropayment Flow...</span>
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    <span>Ask Agent & Settle 0.01 USDC on Algorand</span>
                  </>
                )}
              </button>

              {errorMsg && (
                <div className="p-3 rounded-xl bg-red-950/50 border border-red-500/30 text-xs text-red-300">
                  {errorMsg}
                </div>
              )}
            </div>

            {/* ---------------- LIVE STEP-BY-STEP FLOW VISUALIZER ---------------- */}
            <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-2">
                <Activity className="w-4 h-4 text-cyan-400" />
                <span>Live Transaction Pipeline & Execution Trail</span>
              </h4>

              <div className="space-y-3">
                {[
                  {
                    step: 1,
                    title: '1. User Task Received by BuyerAgent',
                    desc: 'Buyer agent initialized task and identified target service.',
                    active: activeStepIndex >= 1
                  },
                  {
                    step: 2,
                    title: '2. A2A Request Dispatched',
                    desc: 'Buyer agent sent standard A2A message payload to SummaryAgent.',
                    active: activeStepIndex >= 2
                  },
                  {
                    step: 3,
                    title: '3. HTTP 402 Payment Required Received',
                    desc: 'SummaryAgent responded with 402 challenge requesting 0.01 USDC.',
                    active: activeStepIndex >= 3
                  },
                  {
                    step: 4,
                    title: '4. x402 Payment Signed & Broadcast',
                    desc: 'Buyer agent signed Algorand TestNet transaction for payment settlement.',
                    active: activeStepIndex >= 4
                  },
                  {
                    step: 5,
                    title: '5. Algorand TestNet Settlement Confirmed',
                    desc: 'Payment confirmed in blockchain round. Payment proof header attached.',
                    active: activeStepIndex >= 5
                  },
                  {
                    step: 6,
                    title: '6. AI Task Executed & Summary Delivered',
                    desc: 'SummaryAgent verified on-chain proof and synthesized AI summary.',
                    active: activeStepIndex >= 6
                  },
                  {
                    step: 7,
                    title: '7. Smart Contract Registry Updated',
                    desc: 'AgentPayRegistry application recorded task count and payment volume.',
                    active: activeStepIndex >= 7
                  }
                ].map((item) => (
                  <div
                    key={item.step}
                    className={`flex items-start space-x-3 p-2.5 rounded-xl transition ${
                      item.active ? 'bg-cyan-950/30 border border-cyan-500/20' : 'opacity-40'
                    }`}
                  >
                    <div className="mt-0.5">
                      {item.active ? (
                        <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0" />
                      ) : (
                        <div className="w-4 h-4 rounded-full border border-slate-600 shrink-0" />
                      )}
                    </div>
                    <div className="space-y-0.5 text-xs">
                      <p className={`font-semibold ${item.active ? 'text-cyan-200' : 'text-slate-400'}`}>
                        {item.title}
                      </p>
                      <p className="text-[11px] text-slate-400">{item.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* ---------------- RESULT CARD ---------------- */}
            {currentTask && (
              <div className="glass-panel-glow p-6 rounded-2xl border border-cyan-500/40 space-y-4 animate-slide-up">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <div className="flex items-center space-x-2">
                    <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                    <span className="font-bold text-white text-sm">AI Task Completed & Settled</span>
                  </div>
                  <span className="text-xs font-mono text-cyan-300">0.01 USDC Settled</span>
                </div>

                {/* AI Summary Text */}
                <div className="p-4 rounded-xl bg-[#0a0f1d] border border-slate-700/80 text-slate-200 text-sm leading-relaxed">
                  <div className="text-[10px] uppercase font-bold text-cyan-400 mb-1">Generated AI Summary</div>
                  {currentTask.summary_result}
                </div>

                {/* Blockchain Proof Badges */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                  {currentTask.tx_id && (
                    <a
                      href={`https://lora.algokit.io/testnet/transaction/${currentTask.tx_id}`}
                      target="_blank"
                      rel="noreferrer"
                      className="flex items-center justify-between p-3 rounded-xl bg-slate-900/90 border border-cyan-500/30 hover:border-cyan-500 text-xs text-cyan-300 transition"
                    >
                      <div className="truncate mr-2">
                        <span className="text-[10px] text-slate-400 block">Algorand Transaction ID</span>
                        <span className="font-mono">{currentTask.tx_id.slice(0, 12)}...{currentTask.tx_id.slice(-6)}</span>
                      </div>
                      <ExternalLink className="w-4 h-4 shrink-0 text-cyan-400" />
                    </a>
                  )}

                  {currentTask.app_id ? (
                    <a
                      href={`https://lora.algokit.io/testnet/application/${currentTask.app_id}`}
                      target="_blank"
                      rel="noreferrer"
                      className="flex items-center justify-between p-3 rounded-xl bg-slate-900/90 border border-blue-500/30 hover:border-blue-500 text-xs text-blue-300 transition"
                    >
                      <div className="truncate mr-2">
                        <span className="text-[10px] text-slate-400 block">Smart Contract App ID</span>
                        <span className="font-mono">App #{currentTask.app_id}</span>
                      </div>
                      <ExternalLink className="w-4 h-4 shrink-0 text-blue-400" />
                    </a>
                  ) : null}
                </div>
              </div>
            )}
          </section>
        </div>

        {/* ---------------- RECENT TASK HISTORY ---------------- */}
        {taskHistory.length > 0 && (
          <section className="space-y-4">
            <h3 className="text-xs uppercase font-bold tracking-wider text-slate-400 flex items-center space-x-2">
              <Database className="w-4 h-4 text-cyan-400" />
              <span>Recent Settled Tasks Ledger</span>
            </h3>

            <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-900/80 border-b border-slate-800 text-slate-400 uppercase text-[10px]">
                  <tr>
                    <th className="p-3">Task ID</th>
                    <th className="p-3">Agent</th>
                    <th className="p-3">Price</th>
                    <th className="p-3">Transaction</th>
                    <th className="p-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {taskHistory.map((t) => (
                    <tr key={t.task_id} className="hover:bg-slate-800/30 transition">
                      <td className="p-3 font-mono text-cyan-400">{t.task_id}</td>
                      <td className="p-3 text-slate-200">SummaryAgent</td>
                      <td className="p-3 font-mono text-slate-300">${t.price_usd} USDC</td>
                      <td className="p-3 font-mono">
                        {t.tx_id ? (
                          <a
                            href={`https://lora.algokit.io/testnet/transaction/${t.tx_id}`}
                            target="_blank"
                            rel="noreferrer"
                            className="text-cyan-400 hover:underline flex items-center space-x-1"
                          >
                            <span>{t.tx_id.slice(0, 8)}...</span>
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        ) : (
                          '—'
                        )}
                      </td>
                      <td className="p-3">
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                          ✓ Settled
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}
      </main>

      {/* ---------------- Footer ---------------- */}
      <footer className="mt-20 border-t border-slate-800/80 text-center py-6 text-xs text-slate-500 space-y-2">
        <p>AgentPay — A2A + x402 + Algorand AI Agent Marketplace MVP</p>
        <p className="text-[11px] text-slate-600">Built for Algorand TestNet • Powered by PuyaPy & x402 Protocol</p>
      </footer>
    </div>
  );
}
