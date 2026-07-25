"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import Link from "next/link";
import {
  FileText, Brain, Map, Lightbulb, Mic, BarChart3, Briefcase,
  ArrowRight, Sparkles, CheckCircle2, Clock, AlertTriangle, TrendingUp
} from "lucide-react";
import { GithubIcon } from "@/components/Icons";
import { resumeApi, roadmapApi, trackerApi } from "@/lib/api";

export default function DashboardPage() {
  const { user } = useAuth();
  const [resumeData, setResumeData] = useState<any>(null);
  const [roadmaps, setRoadmaps] = useState<any[]>([]);
  const [skills, setSkills] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [resRes, roadRes, trkRes] = await Promise.allSettled([
          resumeApi.latest(),
          roadmapApi.list(),
          trackerApi.getAll(),
        ]);

        if (resRes.status === "fulfilled") setResumeData(resRes.value.data);
        if (roadRes.status === "fulfilled") setRoadmaps(roadRes.value.data);
        if (trkRes.status === "fulfilled") setSkills(trkRes.value.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const quickActions = [
    { title: "Analyze Resume", desc: "Upload PDF & check ATS score", href: "/resume", icon: FileText, color: "var(--blue)" },
    { title: "AI Mentor Chat", desc: "Ask questions to Groq LLM", href: "/mentor", icon: Brain, color: "var(--mauve)" },
    { title: "Personalized Roadmap", desc: "Generate role-based steps", href: "/roadmap", icon: Map, color: "var(--green)" },
    { title: "Project Ideas", desc: "Get curated portfolio ideas", href: "/projects", icon: Lightbulb, color: "var(--yellow)" },
    { title: "GitHub Audit", desc: "Check profile & READMEs", href: "/github", icon: GithubIcon, color: "var(--teal)" },
    { title: "Mock Interview", desc: "Practice & get feedback", href: "/interview", icon: Mic, color: "var(--pink)" },
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass p-6 rounded-2xl">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold">
            Welcome back, <span className="gradient-text">{user?.name}</span> 👋
          </h1>
          <p className="text-sm text-[var(--subtext)] mt-1">
            {user?.college ? `${user.college} · ${user.branch || "CS"} (${user.year || "Student"})` : "Track your AI career readiness"}
          </p>
        </div>
        <Link href="/mentor" className="btn-primary shrink-0 self-start md:self-auto">
          <Sparkles size={16} /> Chat with AI Mentor
        </Link>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* ATS Score */}
        <div className="glass p-5 rounded-xl space-y-2">
          <div className="flex items-center justify-between text-xs text-[var(--overlay0)]">
            <span>Resume ATS Score</span>
            <FileText size={16} className="text-[var(--blue)]" />
          </div>
          <div className="text-3xl font-bold text-[var(--text)]">
            {resumeData?.ats_score ?? "--"}<span className="text-sm font-normal text-[var(--subtext)]">/100</span>
          </div>
          <div className="text-xs text-[var(--subtext)]">
            {resumeData ? (resumeData.ats_score > 75 ? "Great ATS readiness!" : "Needs keyword optimization") : "No resume uploaded yet"}
          </div>
        </div>

        {/* Active Roadmap */}
        <div className="glass p-5 rounded-xl space-y-2">
          <div className="flex items-center justify-between text-xs text-[var(--overlay0)]">
            <span>Active Goal</span>
            <Map size={16} className="text-[var(--green)]" />
          </div>
          <div className="text-xl font-bold text-[var(--text)] truncate">
            {roadmaps[0]?.goal || "No goal set"}
          </div>
          <div className="text-xs text-[var(--subtext)]">
            {roadmaps[0] ? `${roadmaps[0].roadmap_data?.phases?.length || 0} Phased steps` : "Generate your first roadmap"}
          </div>
        </div>

        {/* Skills Tracked */}
        <div className="glass p-5 rounded-xl space-y-2">
          <div className="flex items-center justify-between text-xs text-[var(--overlay0)]">
            <span>Skills Tracked</span>
            <TrendingUp size={16} className="text-[var(--yellow)]" />
          </div>
          <div className="text-3xl font-bold text-[var(--text)]">
            {skills.length}
          </div>
          <div className="text-xs text-[var(--subtext)]">
            {skills.filter(s => s.status === "completed").length} completed
          </div>
        </div>

        {/* GitHub Audit */}
        <div className="glass p-5 rounded-xl space-y-2">
          <div className="flex items-center justify-between text-xs text-[var(--overlay0)]">
            <span>GitHub Connected</span>
            <GithubIcon size={16} className="text-[var(--teal)]" />
          </div>
          <div className="text-xl font-bold text-[var(--text)] truncate">
            {user?.github_username ? `@${user.github_username}` : "Not linked"}
          </div>
          <div className="text-xs text-[var(--subtext)]">
            {user?.github_username ? "Profile synced" : "Link profile to audit"}
          </div>
        </div>
      </div>

      {/* Quick Actions Grid */}
      <div>
        <h2 className="text-lg font-semibold mb-4 text-[var(--text)]">Quick Actions</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {quickActions.map(({ title, desc, href, icon: Icon, color }) => (
            <Link
              key={href}
              href={href}
              className="glass p-5 rounded-xl card-hover flex items-start gap-4 group"
            >
              <div className="p-3 rounded-lg shrink-0" style={{ background: "var(--surface0)" }}>
                <Icon size={22} style={{ color }} />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-[var(--text)] group-hover:text-[var(--blue)] transition-colors flex items-center justify-between">
                  {title}
                  <ArrowRight size={14} className="opacity-0 group-hover:opacity-100 transition-opacity" />
                </h3>
                <p className="text-xs text-[var(--subtext)] mt-1">{desc}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Recent Resume Insights */}
      {resumeData && (
        <div className="glass p-6 rounded-2xl space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-[var(--text)] flex items-center gap-2">
              <FileText size={18} className="text-[var(--blue)]" /> Latest Resume Analysis
            </h2>
            <Link href="/resume" className="text-xs text-[var(--blue)] hover:underline">
              View Full Report →
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl" style={{ background: "var(--surface0)" }}>
              <h4 className="text-xs font-semibold text-[var(--green)] mb-2 flex items-center gap-1.5">
                <CheckCircle2 size={14} /> Strong Skills Detected
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {resumeData.strong_skills?.map((s: string) => (
                  <span key={s} className="badge badge-green text-xs">{s}</span>
                )) || <span className="text-xs text-[var(--overlay0)]">None</span>}
              </div>
            </div>

            <div className="p-4 rounded-xl" style={{ background: "var(--surface0)" }}>
              <h4 className="text-xs font-semibold text-[var(--pink)] mb-2 flex items-center gap-1.5">
                <AlertTriangle size={14} /> Missing ATS Keywords
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {resumeData.missing_keywords?.map((k: string) => (
                  <span key={k} className="badge badge-red text-xs">{k}</span>
                )) || <span className="text-xs text-[var(--overlay0)]">None</span>}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
