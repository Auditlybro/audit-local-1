export default function Loading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-navy-500">
      <div className="flex flex-col items-center gap-3">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-gold border-t-transparent" aria-hidden />
        <p className="text-slate-400">Loading…</p>
      </div>
    </div>
  );
}
