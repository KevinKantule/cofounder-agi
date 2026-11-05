export type AgentStatus = "idle" | "walking" | "working" | "success" | "error" | "awaiting_approval";
export interface AgentEvent { event_id: string; timestamp: string; agent_id: string; status: AgentStatus; destination: string; message: string; metadata: Record<string, unknown>; }
