"use client";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html lang="en" className="dark">
      <body style={{ margin: 0, fontFamily: "system-ui, sans-serif", background: "#0B1120", color: "#e2e8f0", minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", padding: 24 }}>
        <div style={{ maxWidth: 400, textAlign: "center" }}>
          <h2 style={{ fontSize: "1.25rem", fontWeight: 700, color: "#C9A84C" }}>Something went wrong</h2>
          <p style={{ marginTop: 8, fontSize: "0.875rem", color: "#94a3b8" }}>
            {error?.message || "An unexpected error occurred."}
          </p>
          <button
            type="button"
            onClick={() => reset()}
            style={{
              marginTop: 24,
              width: "100%",
              padding: "10px 16px",
              borderRadius: 8,
              background: "#C9A84C",
              color: "#0B1120",
              fontWeight: 500,
              border: "none",
              cursor: "pointer",
            }}
          >
            Try again
          </button>
        </div>
      </body>
    </html>
  );
}
