import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { Sparkles, Mail, Lock, User as UserIcon, ArrowRight } from "lucide-react";
import { useStore } from "@/lib/store";
import { authAPI } from "@/lib/api";
import { toast } from "sonner";

export const Route = createFileRoute("/auth")({
  head: () => ({ meta: [{ title: "intelligent-flashcards" }] }),
  component: AuthPage,
});

function AuthPage() {
  const { setUser } = useStore();
  const navigate = useNavigate();
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (mode === "signup") {
      if (!name || !email || !password) return toast.error("Please fill all fields");
      if (password !== confirm) return toast.error("Passwords don't match");
      try {
        const data = await authAPI.signup(email, password, name);
        setUser({ name: data.user.name, email: data.user.email });
        toast.success("Welcome to Smart Flashcard AI 🎉");
        navigate({ to: "/dashboard" });
      } catch (error: any) {
        toast.error(error.message || "Signup failed");
      }
    } else {
      if (!email || !password) return toast.error("Please enter your credentials");
      try {
        const data = await authAPI.login(email, password);
        setUser({ name: data.user.name, email: data.user.email });
        toast.success("Welcome back!");
        navigate({ to: "/dashboard" });
      } catch (error: any) {
        toast.error(error.message || "Login failed");
      }
    }
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center px-4 py-12 bg-background overflow-hidden">
      <div className="absolute inset-0 bg-aurora opacity-60" />
      <div className="absolute -top-20 -left-20 w-96 h-96 rounded-full bg-primary/30 blur-3xl animate-blob" />
      <div className="absolute -bottom-20 -right-20 w-96 h-96 rounded-full bg-accent/40 blur-3xl animate-blob" style={{ animationDelay: "4s" }} />

      <div className="relative z-10 w-full max-w-md animate-scale-in">
        <Link to="/" className="flex items-center gap-3 justify-center mb-8">
          <div className="w-11 h-11 rounded-xl bg-gradient-primary flex items-center justify-center shadow-glow">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <span className="font-display font-bold text-xl">Smart Flashcard AI</span>
        </Link>

        <div className="rounded-3xl glass shadow-elegant p-8">
          <div className="flex p-1 rounded-xl bg-muted/60 mb-6">
            <button
              onClick={() => setMode("login")}
              className={`flex-1 py-2 text-sm font-semibold rounded-lg transition-all ${
                mode === "login" ? "bg-card shadow-soft" : "text-muted-foreground"
              }`}
            >
              Login
            </button>
            <button
              onClick={() => setMode("signup")}
              className={`flex-1 py-2 text-sm font-semibold rounded-lg transition-all ${
                mode === "signup" ? "bg-card shadow-soft" : "text-muted-foreground"
              }`}
            >
              Sign up
            </button>
          </div>

          <h1 className="font-display font-bold text-2xl mb-1">
            {mode === "login" ? "Welcome back" : "Create your account"}
          </h1>
          <p className="text-sm text-muted-foreground mb-6">
            {mode === "login" ? "Sign in to continue your study journey." : "Start learning smarter in seconds."}
          </p>

          <form onSubmit={submit} className="space-y-4">
            {mode === "signup" && (
              <Field icon={UserIcon} label="Full Name" value={name} onChange={setName} placeholder="Ada Lovelace" />
            )}
            <Field icon={Mail} label="Email" type="email" value={email} onChange={setEmail} placeholder="you@example.com" />
            <Field icon={Lock} label="Password" type="password" value={password} onChange={setPassword} placeholder="••••••••" />
            {mode === "signup" && (
              <Field icon={Lock} label="Confirm Password" type="password" value={confirm} onChange={setConfirm} placeholder="••••••••" />
            )}

            {mode === "login" && (
              <div className="text-right">
                <button type="button" className="text-xs text-primary hover:underline" onClick={() => toast.info("Reset link sent (demo)")}>
                  Forgot password?
                </button>
              </div>
            )}

            <button
              type="submit"
              className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-primary px-5 py-3 text-sm font-semibold text-white shadow-elegant hover:shadow-glow transition-all"
            >
              {mode === "login" ? "Login" : "Create Account"}
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          <p className="text-center text-sm text-muted-foreground mt-6">
            {mode === "login" ? "New here? " : "Already have an account? "}
            <button onClick={() => setMode(mode === "login" ? "signup" : "login")} className="text-primary font-medium hover:underline">
              {mode === "login" ? "Create an account" : "Sign in"}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}

function Field({
  icon: Icon, label, value, onChange, type = "text", placeholder,
}: {
  icon: React.ComponentType<{ className?: string }>; label: string; value: string;
  onChange: (v: string) => void; type?: string; placeholder?: string;
}) {
  return (
    <label className="block">
      <span className="text-xs font-medium text-muted-foreground mb-1.5 block">{label}</span>
      <div className="relative">
        <Icon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="w-full rounded-xl bg-card border border-input pl-10 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring transition-all"
        />
      </div>
    </label>
  );
}
