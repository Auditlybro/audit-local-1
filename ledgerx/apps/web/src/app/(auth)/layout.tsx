import { ThemeToggle } from "@/components/ui/ThemeToggle";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-navy p-4 relative">
      <div className="absolute top-4 right-4 w-12">
        <ThemeToggle collapsed={true} />
      </div>
      <div className="w-full max-w-md">{children}</div>
    </div>
  );
}
