"use client";
import { useState } from "react";
import { githubApi } from "@/lib/api";
import { Sparkles, Star, GitFork, CheckCircle2, AlertTriangle } from "lucide-react";
import { GithubIcon } from "@/components/Icons";
import toast from "react-hot-toast";

export default function GitHubPage() {
  const [username, setUsername] = useState("octocat");
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim()) return;
    setLoading(true);
    try {
      const res = await githubApi.analyze(username);
      setAnalysis(res.data?.analysis_data);
      toast.success("GitHub profile analyzed!");
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Failed to analyze GitHub profile");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <GithubIcon className="text-[var(--teal)]" /> GitHub Profile Analyzer
        </h1>
        <p className="text-[var(--subtext)] text-sm mt-1">
          Audit contribution health, README completeness, repo quality, and recruiter readiness.
        </p>
      </div>

      <form onSubmit={handleAnalyze} className="glass p-4 rounded-xl flex gap-3">
        <input
          type="text"
          className="input flex-1"
          placeholder="GitHub Username (e.g., torvalds)..."
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <button type="submit" disabled={loading} className="btn-primary shrink-0">
          <Sparkles size={16} /> Audit Profile
        </button>
      </form>

      {analysis && (
        <div className="space-y-6">
          {/* Profile Overview */}
          <div className="glass p-6 rounded-2xl flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold">@{analysis.username}</h2>
              <p className="text-xs text-[var(--subtext)]">{analysis.bio}</p>
              <div className="flex gap-4 mt-3 text-xs text-[var(--overlay0)]">
                <span>⭐ {analysis.total_stars} Total Stars</span>
                <span>📦 {analysis.public_repos} Repos</span>
              </div>
            </div>
            <div className="score-ring flex items-center justify-center rounded-full border-4 border-[var(--teal)] text-3xl font-bold text-[var(--teal)]">
              {analysis.ai_analysis?.overall_score ?? 60}%
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Strengths */}
            <div className="glass p-6 rounded-2xl space-y-3">
              <h3 className="font-semibold text-[var(--green)] flex items-center gap-2">
                <CheckCircle2 size={18} /> Profile Strengths
              </h3>
              <ul className="text-xs text-[var(--subtext)] space-y-2 list-disc pl-4">
                {analysis.ai_analysis?.strengths?.map((s: string, i: number) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>

            {/* Improvement Suggestions */}
            <div className="glass p-6 rounded-2xl space-y-3">
              <h3 className="font-semibold text-[var(--pink)] flex items-center gap-2">
                <AlertTriangle size={18} /> Actionable Suggestions
              </h3>
              <div className="space-y-2">
                {analysis.ai_analysis?.suggestions?.map((item: any, i: number) => (
                  <div key={i} className="p-3 rounded-lg bg-[var(--surface0)] text-xs">
                    <p className="font-medium text-[var(--text)]">{item.suggestion}</p>
                    <p className="text-[var(--overlay0)] mt-0.5">{item.reason}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
