import { useState, useCallback } from "react";
import { invoke } from "@tauri-apps/api/core";

const WEB_URL = import.meta.env.VITE_API_URL || "http://localhost:3000";

type SyncStatus = "synced" | "pending" | "offline";

function App() {
  const [syncStatus, setSyncStatus] = useState<SyncStatus>("synced");
  const [aiMode, setAiMode] = useState<"local" | "cloud">("local");
  const [isTauri, setIsTauri] = useState(false);
  React.useEffect(() => {
    setIsTauri(!!(typeof window !== "undefined" && (window as unknown as { __TAURI__?: unknown }).__TAURI__));
  }, []);

  const openFile = useCallback(async () => {
    try {
      const path = await invoke<string | null>("open_file_dialog");
      if (path) return path;
    } catch (e) {
      console.error(e);
    }
    return null;
  }, []);

  const saveFile = useCallback(async (data: string, filename: string) => {
    try {
      const path = await invoke<string | null>("save_file_dialog", { data, filename });
      return path;
    } catch (e) {
      console.error(e);
      return null;
    }
  }, []);

  const getLocalIp = useCallback(async () => {
    try {
      return await invoke<string>("get_local_ip");
    } catch {
      return null;
    }
  }, []);

  const checkTally = useCallback(async () => {
    try {
      return await invoke<boolean>("check_tally_running");
    } catch {
      return false;
    }
  }, []);

  const checkOllama = useCallback(async () => {
    try {
      return await invoke<boolean>("check_ollama_status");
    } catch {
      return false;
    }
  }, []);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      {/* Top bar: sync status + AI mode (when in Tauri) */}
      <header
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          padding: "8px 16px",
          background: "#1e293b",
          color: "#fff",
          minHeight: 40,
        }}
      >
        <span style={{ fontWeight: 600 }}>LedgerX</span>
        <span
          style={{
            width: 8,
            height: 8,
            borderRadius: "50%",
            background: syncStatus === "synced" ? "#22c55e" : syncStatus === "offline" ? "#ef4444" : "#eab308",
          }}
          title={syncStatus === "synced" ? "Synced" : syncStatus === "offline" ? "Offline" : "Pending sync"}
        />
        <span style={{ fontSize: 12, opacity: 0.8 }}>
          {syncStatus === "synced" ? "Synced" : syncStatus === "offline" ? "Offline — using local SQLite" : "Sync pending"}
        </span>
        {isTauri && (
          <>
            <select
              value={aiMode}
              onChange={(e) => setAiMode(e.target.value as "local" | "cloud")}
              style={{ marginLeft: "auto", padding: "4px 8px", borderRadius: 4 }}
            >
              <option value="local">AI: Local (Ollama)</option>
              <option value="cloud">AI: Cloud</option>
            </select>
          </>
        )}
      </header>
      {/* Embed web frontend */}
      <iframe
        title="LedgerX Web"
        src={WEB_URL}
        style={{ flex: 1, border: "none", width: "100%" }}
      />
    </div>
  );
}

export default App;
