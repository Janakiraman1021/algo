/**
 * Frontend API client for AgentPay FastAPI Backend
 */

export interface AgentInfo {
  agent_id: string;
  name: string;
  description: string;
  address: string;
  price_usd: number;
  network: string;
  payment_protocol: string;
  status: string;
  services: string[];
}

export interface TaskStep {
  step_number: number;
  name: string;
  description: string;
  status: 'pending' | 'active' | 'completed' | 'failed';
  tx_id?: string;
  timestamp?: string;
}

export interface TaskResponse {
  task_id: string;
  status: string;
  input_text: string;
  summary_result?: string;
  price_usd: number;
  tx_id?: string;
  explorer_url?: string;
  app_id?: number;
  created_at: string;
  completed_at?: string;
  steps: TaskStep[];
  error_message?: string;
}

export interface StatsResponse {
  total_agents: number;
  total_services: number;
  total_tasks: number;
  total_volume_usd: number;
  total_volume_micro: number;
  app_id: number;
  network: string;
  algod_status: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchStats(): Promise<StatsResponse> {
  const res = await fetch(`${API_BASE}/api/stats`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch marketplace statistics');
  return res.json();
}

export async function fetchAgents(): Promise<AgentInfo[]> {
  const res = await fetch(`${API_BASE}/api/agents`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch agent listings');
  return res.json();
}

export async function submitTask(text: string, targetAgent: string = 'summary-agent'): Promise<TaskResponse> {
  const res = await fetch(`${API_BASE}/api/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text,
      target_agent: targetAgent,
      service_id: 'text_summarization'
    })
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || 'Failed to submit A2A task');
  }
  return res.json();
}

export async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE}/api/health`, { cache: 'no-store' });
    return await res.json();
  } catch (err: any) {
    return { status: 'offline', error: err.message };
  }
}
