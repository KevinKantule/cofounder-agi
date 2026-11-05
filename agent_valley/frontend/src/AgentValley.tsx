import type { AgentEvent } from "./types";
import { AgentSprite } from "./AgentSprite";

const zones: Record<string, [number, number]> = { cerebro: [18, 22], escudo: [76, 20], hipocampo: [17, 74], mercado: [77, 74], laboratorio: [47, 48], camara_pruebas: [48, 82] };
const fallback: [number, number] = [48, 48];
export function AgentValley({ events }: { events: AgentEvent[] }) {
  const latest = Object.values(events.reduce<Record<string, AgentEvent>>((all, event) => ({ ...all, [event.agent_id]: event }), {}));
  return <main className="valley"><div className="stars" />
    {Object.entries(zones).map(([name, [x, y]]) => <div className="zone" key={name} style={{ left: `${x}%`, top: `${y}%` }}>{name.replace("_", " ")}</div>)}
    {latest.map(event => { const [x, y] = zones[event.destination] ?? fallback; return <AgentSprite key={event.agent_id} event={event} x={x} y={y} />; })}
    <footer>{events.length ? events.at(-1)?.message : "Esperando telemetría del motor…"}</footer>
  </main>;
}
