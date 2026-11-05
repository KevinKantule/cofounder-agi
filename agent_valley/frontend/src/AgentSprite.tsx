import { motion } from "framer-motion";
import type { AgentEvent } from "./types";

const palette = { idle: "#8b9bb4", walking: "#5eead4", working: "#818cf8", success: "#86efac", error: "#fb7185", awaiting_approval: "#fbbf24" };
export function AgentSprite({ event, x, y }: { event: AgentEvent; x: number; y: number }) {
  return <motion.div className="agent" animate={{ left: `${x}%`, top: `${y}%` }} transition={{ type: "spring", stiffness: 55, damping: 14 }} style={{ borderColor: palette[event.status] }} title={`${event.agent_id}: ${event.message || event.status}`}>
    <span className="bot">◉</span><span>{event.agent_id}</span><small>{event.status}</small>
  </motion.div>;
}
