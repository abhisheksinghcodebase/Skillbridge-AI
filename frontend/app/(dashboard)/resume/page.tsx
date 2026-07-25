"use client";
import { useState, useEffect } from "react";
import { resumeApi } from "@/lib/api";
import { Upload, FileText, CheckCircle2, AlertCircle, Sparkles, RefreshCw, Layers } from "lucide-react";
import toast from "react-hot-toast";

export default function ResumePage() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);
  const [fetching, setFetching] = useState(true);

  useEffect(() => {
    async function loadLatest() {
      try {
        const res = await resumeApi.latest();
        setAnalysis(res.data);
      } catch (err) {
        // No resume yet
      } finally {
        setFetching(false);
      }
    }
    loadLatest();
  }, []);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    try {
      const res = await resumeApi.upload(file);
      setAnalysis(res.data);
      toast.success("Resume analyzed successfully!");
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Resume Analyzer & ATS Checker</h1>
        <p className="text-[var(--subtext)] text-sm mt-1">
          Upload your resume PDF to extract skills, calculate ATS score, and receive AI improvement tips.
        </p>
      </div>

      {/* Upload Box */}
      <div className="glass p-8 rounded-2xl">
        <form onSubmit={handleUpload} className="space-y-4">
          <div className="border-2 border-dashed border-[var(--surface1)] hover:border-[var(--blue)] transition-colors rounded-xl p-8 text-center cursor-pointer flex flex-col items-center justify-center gap-3">
            <Upload size={32} className="text-[var(--blue)]" />
            <div>
              <p className="text-sm font-medium">
                {file ? file.name : "Click or drag resume PDF here"}
              </p>
              <p className="text-xs text-[var(--overlay0)] mt-1">PDF up to 10MB</p>
            </div>
            <input
              type="file"
              accept=".pdf"
              className="hidden"
              id="resume-input"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
            />
            <label htmlFor="resume-input" className="btn-secondary text-xs">
              Select File
            </label>
          </div>

          <button
            type="submit"
            disabled={!file || loading}
            className="btn-primary w-full justify-center py-3"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <RefreshCw size={16} className="animate-spin" /> Analyzing Resume with Groq AI…
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <Sparkles size={16} /> Run Full Analysis
              </span>
            )}
          </button>
        </form>
      </div>

      {/* Results View */}
      {analysis && (
        <div className="space-y-6">
          {/* Score Header */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="glass p-6 rounded-2xl flex items-center gap-6">
              <div className="score-ring flex items-center justify-center rounded-full border-4 border-[var(--blue)] text-3xl font-bold text-[var(--blue)] shrink-0">
                {analysis.resume_score ?? 70}%
              </div>
              <div>
                <h3 className="font-semibold text-lg">Overall Resume Score</h3>
                <p className="text-xs text-[var(--subtext)] mt-1">
                  Based on structure, project impact, formatting, and grammar clarity.
                </p>
              </div>
            </div>

            <div className="glass p-6 rounded-2xl flex items-center gap-6">
              <div className="score-ring flex items-center justify-center rounded-full border-4 border-[var(--green)] text-3xl font-bold text-[var(--green)] shrink-0">
                {analysis.ats_score ?? 65}%
              </div>
              <div>
                <h3 className="font-semibold text-lg">ATS Compatibility Score</h3>
                <p className="text-xs text-[var(--subtext)] mt-1">
                  Measures readability by Applicant Tracking Systems and keyword match.
                </p>
              </div>
            </div>
          </div>

          {/* Detailed Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Strong Skills */}
            <div className="glass p-6 rounded-2xl space-y-3">
              <h3 className="font-semibold text-[var(--green)] flex items-center gap-2">
                <CheckCircle2 size={18} /> Strong Skills Detected
              </h3>
              <div className="flex flex-wrap gap-2">
                {analysis.strong_skills?.map((s: string) => (
                  <span key={s} className="badge badge-green">{s}</span>
                ))}
              </div>
            </div>

            {/* Weak Skills */}
            <div className="glass p-6 rounded-2xl space-y-3">
              <h3 className="font-semibold text-[var(--yellow)] flex items-center gap-2">
                <AlertCircle size={18} /> Weak / Missing Skills
              </h3>
              <div className="flex flex-wrap gap-2">
                {analysis.weak_skills?.map((s: string) => (
                  <span key={s} className="badge badge-yellow">{s}</span>
                ))}
              </div>
            </div>

            {/* Formatting & Grammar */}
            <div className="glass p-6 rounded-2xl space-y-3">
              <h3 className="font-semibold text-[var(--mauve)] flex items-center gap-2">
                <Layers size={18} /> Formatting & Style Suggestions
              </h3>
              <ul className="text-xs text-[var(--subtext)] space-y-2 list-disc pl-4">
                {analysis.formatting_suggestions?.map((tip: string, i: number) => (
                  <li key={i}>{tip}</li>
                ))}
              </ul>
            </div>

            {/* Actionable Improvement Tips */}
            <div className="glass p-6 rounded-2xl space-y-3">
              <h3 className="font-semibold text-[var(--blue)] flex items-center gap-2">
                <Sparkles size={18} /> AI Action Plan
              </h3>
              <ul className="text-xs text-[var(--subtext)] space-y-2 list-disc pl-4">
                {analysis.improvement_tips?.map((tip: string, i: number) => (
                  <li key={i}>{tip}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
