"use client";
import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import Link from "next/link";
import toast from "react-hot-toast";
import { Eye, EyeOff, Zap, ArrowRight, User, Mail, Lock, GraduationCap } from "lucide-react";

const YEARS = ["1st Year", "2nd Year", "3rd Year", "4th Year", "Graduated", "Bootcamp"];

export default function RegisterPage() {
  const { register } = useAuth();
  const router = useRouter();
  const [form, setForm] = useState({
    name: "", email: "", password: "", college: "", branch: "", year: ""
  });
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);

  const set = (key: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm((f) => ({ ...f, [key]: e.target.value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (form.password.length < 8) {
      toast.error("Password must be at least 8 characters");
      return;
    }
    setLoading(true);
    try {
      await register(form);
      toast.success("Account created! Welcome to SkillBridge AI 🎉");
      router.push("/dashboard");
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="hero-bg min-h-screen flex items-center justify-center p-4 py-12">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2 justify-center">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ background: "var(--gradient-primary)" }}>
              <Zap size={20} className="text-[var(--crust)]" />
            </div>
            <span className="text-xl font-bold gradient-text">SkillBridge AI</span>
          </Link>
          <h1 className="text-2xl font-bold mt-6 mb-1">Create your account</h1>
          <p className="text-[var(--subtext)] text-sm">Start your AI-powered career journey</p>
        </div>

        <div className="glass p-8 space-y-4">
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Name */}
            <div>
              <label className="block text-sm font-medium mb-2 text-[var(--subtext)]">Full Name</label>
              <div className="relative">
                <User size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--overlay0)]" />
                <input className="input pl-9" placeholder="John Doe" value={form.name}
                  onChange={set("name")} required />
              </div>
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium mb-2 text-[var(--subtext)]">Email</label>
              <div className="relative">
                <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--overlay0)]" />
                <input type="email" className="input pl-9" placeholder="you@example.com"
                  value={form.email} onChange={set("email")} required />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium mb-2 text-[var(--subtext)]">Password</label>
              <div className="relative">
                <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--overlay0)]" />
                <input type={showPass ? "text" : "password"} className="input pl-9 pr-10"
                  placeholder="Min 8 characters" value={form.password} onChange={set("password")} required />
                <button type="button" onClick={() => setShowPass(!showPass)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--overlay0)] hover:text-[var(--text)]">
                  {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            {/* College + Branch */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium mb-2 text-[var(--subtext)]">College</label>
                <input className="input" placeholder="MIT, IIT, etc." value={form.college} onChange={set("college")} />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2 text-[var(--subtext)]">Branch</label>
                <input className="input" placeholder="CS, IT, ECE…" value={form.branch} onChange={set("branch")} />
              </div>
            </div>

            {/* Year */}
            <div>
              <label className="block text-sm font-medium mb-2 text-[var(--subtext)]">Academic Year</label>
              <select className="input" value={form.year} onChange={set("year")}>
                <option value="">Select year…</option>
                {YEARS.map((y) => <option key={y} value={y}>{y}</option>)}
              </select>
            </div>

            <button type="submit" className="btn-primary w-full justify-center py-3 mt-2" disabled={loading}>
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-[var(--crust)] border-t-transparent rounded-full animate-spin" />
                  Creating account…
                </span>
              ) : (
                <span className="flex items-center justify-center gap-2">
                  Create Account <ArrowRight size={16} />
                </span>
              )}
            </button>
          </form>

          <p className="text-center text-sm text-[var(--subtext)]">
            Already have an account?{" "}
            <Link href="/auth/login" className="text-[var(--blue)] hover:underline font-medium">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
