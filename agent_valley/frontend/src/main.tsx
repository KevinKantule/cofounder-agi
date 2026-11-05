import { StrictMode, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { Streamlit } from "streamlit-component-lib";
import { AgentValley } from "./AgentValley";
import type { AgentEvent } from "./types";
import "./styles.css";

function App() {
  const [events, setEvents] = useState<AgentEvent[]>([]);
  useEffect(() => {
    const onRender = (event: Event) => {
      const args = (event as CustomEvent<{ args: { events?: AgentEvent[] } }>).detail.args;
      setEvents(args.events ?? []);
      Streamlit.setFrameHeight(410);
    };
    Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);
    Streamlit.setComponentReady();
    return () => Streamlit.events.removeEventListener(Streamlit.RENDER_EVENT, onRender);
  }, []);
  return <AgentValley events={events} />;
}
createRoot(document.getElementById("root")!).render(<StrictMode><App /></StrictMode>);
