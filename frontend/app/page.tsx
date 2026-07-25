"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import {
  Brain, FileText, Map, Lightbulb, Mic,
  BarChart3, Briefcase, ArrowRight, Zap, Star,
  Shield, Sparkles, ChevronRight, Users
} from "lucide-react";
import { GithubIcon } from "@/components/Icons";
import { useEffect } from "react";

const features = [
  { icon: FileText, title: "Resume Analyzer", desc: "ATS scoring, skill extraction, formatting tips", color: "var(--blue)", gradient: "var(--gradient-primary)" },
  { icon: Brain, title: "AI Career Mentor", desc: "Real-time streaming chat with career guidance", color: "var(--mauve)", gradient: "linear-gradient(135deg,#cba6f7,#b4befe)" },
  { icon: Map, title: "Learning Roadmap", desc: "Personalized phased paths to your dream role", color: "var(--green)", gradient: "var(--gradient-success)" },
  { icon: Lightbulb, title: "Project Ideas", desc: "AI-curated projects matching your skills & goals", color: "var(--yellow)", gradient: "var(--gradient-warm)" },
  { icon: GithubIcon, title: "GitHub Analyzer", desc: "Profile score, suggestions, career readiness", color: "var(--teal)", gradient: "linear-gradient(135deg,#94e2d5,#89dceb)" },
  { icon: Mic, title: "Mock Interviews", desc: "AI-scored Q&A sessions with detailed feedback", color: "var(--pink)", gradient: "var(--gradient-danger)" },
  { icon: BarChart3, title: "Learning Tracker", desc: "Visual progress tracking across all your skills", color: "var(--peach)", gradient: "linear-gradient(135deg,#fab387,#f9e2af)" },
  { icon: Briefcase, title: "Job Matching", desc: "AI matches jobs to your skills with % scores", color: "var(--lavender)", gradient: "linear-gradient(135deg,#b4befe,#cba6f7)" },
];

const stats = [
  { label: "AI Models Used", value: "4+" },
  { label: "Career Modules", value: "10" },
  { label: "Powered By", value: "Groq" },
  { label: "Free to Use", value: "✓" },
];

export default function LandingPage() {
  const { user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (user) router.push("/dashboard");
  }, [user, router]);

  return (
    <div className="hero-bg min-h-screen">
      {/* Navbar */}
      <nav className="sticky top-0 z-50 glass-dark border-b border-[var(--surface0)]">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center"
              style={{ background: "var(--gradient-primary)" }}>
              <Zap size={18} className="text-[var(--crust)]" />
            </div>
            <span className="font-bold text-lg gradient-text">SkillBridge AI</span>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/auth/login" className="btn-ghost text-sm">Sign In</Link>
            <Link href="/auth/register" className="btn-primary text-sm">
              Get Started <ArrowRight size={15} />
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-7xl mx-auto px-6 pt-24 pb-20 text-center">
        <div className="inline-flex items-center gap-2 badge badge-mauve mb-6 animate-fade-in-up">
          <Sparkles size={13} /> Powered by Groq · Llama 3.3 70B
        </div>

        <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight animate-fade-in-up"
          style={{ animationDelay: "0.1s" }}>
          Your AI Career Mentor<br />
          <span className="gradient-text">from Learning to</span><br />
          Landing a Job
        </h1>

        <p className="text-xl text-[var(--subtext)] max-w-2xl mx-auto mb-10 leading-relaxed animate-fade-in-up"
          style={{ animationDelay: "0.2s" }}>
          Resume analysis, personalized roadmaps, mock interviews, GitHub profile
          optimization, and AI-powered job matching — all in one platform built for students.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-in-up"
          style={{ animationDelay: "0.3s" }}>
          <Link href="/auth/register" className="btn-primary text-base px-8 py-3 animate-pulse-glow">
            Start for Free <ArrowRight size={18} />
          </Link>
          <Link href="/auth/login" className="btn-secondary text-base px-8 py-3">
            Sign In
          </Link>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-2xl mx-auto mt-16 animate-fade-in-up"
          style={{ animationDelay: "0.4s" }}>
          {stats.map(({ label, value }) => (
            <div key={label} className="glass rounded-2xl p-4 text-center">
              <div className="text-2xl font-bold gradient-text">{value}</div>
              <div className="text-xs text-[var(--overlay0)] mt-1">{label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features Grid */}
      <section className="max-w-7xl mx-auto px-6 pb-24">
        <div className="text-center mb-14">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Everything You Need to <span className="gradient-text">Land Your Dream Job</span>
          </h2>
          <p className="text-[var(--subtext)] max-w-xl mx-auto">
            Stop switching between 10 different tools. SkillBridge AI brings your entire career journey into one intelligent platform.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {features.map(({ icon: Icon, title, desc, color, gradient }, i) => (
            <div
              key={title}
              className="glass card-hover p-6 group cursor-pointer animate-fade-in-up"
              style={{ animationDelay: `${0.05 * i}s` }}
            >
              <div className="w-11 h-11 rounded-xl flex items-center justify-center mb-4 shrink-0"
                style={{ background: gradient, opacity: 0.9 }}>
                <Icon size={20} className="text-[var(--crust)]" />
              </div>
              <h3 className="font-semibold text-[var(--text)] mb-2 group-hover:text-[var(--blue)] transition-colors">
                {title}
              </h3>
              <p className="text-sm text-[var(--subtext)] leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="max-w-7xl mx-auto px-6 pb-24">
        <div className="glass rounded-3xl p-12 text-center relative overflow-hidden">
          <div className="absolute inset-0 opacity-20"
            style={{ background: "var(--gradient-primary)", filter: "blur(60px)" }} />
          <div className="relative z-10">
            <Star size={40} className="mx-auto mb-6 text-[var(--yellow)]" />
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Ready to Accelerate Your Career?
            </h2>
            <p className="text-[var(--subtext)] mb-8 max-w-md mx-auto">
              Join thousands of students using AI to break into tech faster.
            </p>
            <Link href="/auth/register" className="btn-primary text-lg px-10 py-4 inline-flex">
              Start Free Today <ChevronRight size={20} />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-[var(--surface0)] py-8 text-center text-sm text-[var(--overlay0)]">
        <p>© 2025 SkillBridge AI · Built with ❤️ for students</p>
      </footer>
    </div>
  );
}
