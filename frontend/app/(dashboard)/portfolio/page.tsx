"use client";
import { useState } from "react";
import { phase3Api } from "@/lib/api";
import { Globe, Sparkles, Layout, ShieldCheck, Zap, Eye, CheckCircle2, AlertTriangle } from "lucide-react";
import toast from "react-hot-toast";

export default function PortfolioPage() {
  const [url, setUrl] = useState("https://my-portfolio-demo.vercel.app");
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<any>(null);

  const handleAudit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;
    setLoading(true);
    try {
      const res = await phase3Api.reviewPortfolio(url);
      setReport(res.data);
      toast.success("Portfolio audit complete!");
    } catch (err: any) {
      toast.error("Failed to audit portfolio site");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Globe className="text-[var(--mauve)]" /> AI Portfolio Reviewer
        </h1>
        <p className="text-[var(--subtext)] text-sm mt-1">
          Enter your portfolio site URL to analyze UI/UX, responsiveness, SEO tags, performance, and missing sections.
        </p>
      </div>

      <form onSubmit={handleAudit} className="glass p-4 rounded-xl flex gap-3">
        <input
          type="text"
          className="input flex-1"
          placeholder="https://yourname.dev..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <button type="submit" disabled={loading} className="btn-primary shrink-0">
          <Sparkles size={16} /> Audit Site
        </button>
      </form>

      {report && (
        <div className="space-y-6">
          {/* Header score cards */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="glass p-4 rounded-xl text-center">
              <span className="text-xs text-[var(--overlay0)]">Overall</span>
              <div className="text-2xl font-bold text-[var(--blue)] mt-1">{report.overall_score}%</div>
            </div>
            <div className="glass p-4 rounded-xl text-center">
              <span className="text-xs text-[var(--overlay0)]">UI / UX</span>
              <div className="text-2xl font-bold text-[var(--mauve)] mt-1">{report.ui_ux_score}%</div>
            </div>
            <div className="glass p-4 rounded-xl text-center">
              <span className="text-xs text-[var(--overlay0)]">SEO</span>
              <div className="text-2xl font-bold text-[var(--green)] mt-1">{report.seo_score}%</div>
            </div>
            <div className="glass p-4 rounded-xl text-center">
              <span className="text-xs text-[var(--overlay0)]">Performance</span>
              <div className="text-2xl font-bold text-[var(--yellow)] mt-1">{report.performance_score}%</div>
            </div>
            <div className="glass p-4 rounded-xl text-center">
              <span className="text-xs text-[var(--overlay0)]">Accessibility</span>
              <div className="text-2xl font-bold text-[var(--teal)] mt-1">{report.accessibility_score}%</div>
            </div>
          </div>

          {/* Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="glass p-6 rounded-2xl space-y-3">
              <h3 className="font-semibold text-[var(--green)] flex items-center gap-2">
                <CheckCircle2 size={18} /> Strengths
              </h3>
              <ul className="text-xs text-[var(--subtext)] space-y-2 list-disc pl-4">
                {report.strengths?.map((s: string, i: number) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>

            <div className="glass p-6 rounded-2xl space-y-3">
              <h3 className="font-semibold text-[var(--pink)] flex items-center gap-2">
                <AlertTriangle size={18} /> Missing Essential Sections
              </h3>
              <ul className="text-xs text-[var(--subtext)] space-y-2 list-disc pl-4">
                {report.missing_sections?.map((m: string, i: number) => (
                  <li key={i}>{m}</li>
                ))}
              </ul>
            </div>
          </div>

          {/* Improvement Solutions */}
          <div className="glass p-6 rounded-2xl space-y-4">
            <h3 className="font-semibold text-lg flex items-center gap-2">
              <Sparkles size={18} className="text-[var(--yellow)]" /> Actionable Fixes & Code Improvements
            </h3>
            <div className="space-y-3">
              {report.improvements?.map((item: any, i: number) => (
                <div key={i} className="p-4 rounded-xl bg-[var(--surface0)] text-xs space-y-1">
                  <div className="flex justify-between items-center">
                    <span className="badge badge-mauve uppercase font-semibold text-[10px]">{item.category}</span>
                  </div>
                  <p className="font-semibold text-[var(--text)] text-sm">{item.issue}</p>
                  <p className="text-[var(--subtext)]">{item.solution}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
