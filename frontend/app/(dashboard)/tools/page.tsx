"use client";
import { useState } from "react";
import { phase3Api } from "@/lib/api";
import { FileText, Share2, Sparkles, Copy, Check } from "lucide-react";
import toast from "react-hot-toast";

export default function ToolsPage() {
  const [tab, setTab] = useState<"cover" | "linkedin">("cover");

  // Cover Letter state
  const [role, setRole] = useState("Junior Software Engineer");
  const [company, setCompany] = useState("Google");
  const [jobDesc, setJobDesc] = useState("");
  const [coverOutput, setCoverOutput] = useState("");
  const [loadingCover, setLoadingCover] = useState(false);

  // LinkedIn Post state
  const [projectTitle, setProjectTitle] = useState("SkillBridge AI Career Platform");
  const [techStack, setTechStack] = useState("FastAPI, Next.js, Groq, PostgreSQL");
  const [highlights, setHighlights] = useState("RAG Over Resumes, ATS Analyzer, Mock Interview Simulator");
  const [linkedinOutput, setLinkedinOutput] = useState("");
  const [loadingLinkedin, setLoadingLinkedin] = useState(false);

  const [copied, setCopied] = useState(false);

  const handleCoverLetter = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoadingCover(true);
    try {
      const res = await phase3Api.generateCoverLetter({
        target_role: role,
        company_name: company,
        job_description: jobDesc,
      });
      setCoverOutput(res.data?.cover_letter || "");
      toast.success("Cover letter generated!");
    } catch (err) {
      toast.error("Failed to generate cover letter");
    } finally {
      setLoadingCover(false);
    }
  };

  const handleLinkedIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoadingLinkedin(true);
    try {
      const res = await phase3Api.generateLinkedInPost({
        project_title: projectTitle,
        tech_stack: techStack.split(",").map((s) => s.trim()),
        key_features: highlights,
      });
      setLinkedinOutput(res.data?.linkedin_post || "");
      toast.success("LinkedIn post generated!");
    } catch (err) {
      toast.error("Failed to generate LinkedIn post");
    } finally {
      setLoadingLinkedin(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    toast.success("Copied to clipboard!");
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Sparkles className="text-[var(--mauve)]" /> AI Career Tools
        </h1>
        <p className="text-[var(--subtext)] text-sm mt-1">
          Generate targeted cover letters and high-impact LinkedIn posts tailored to your technical achievements.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-[var(--surface0)] pb-2">
        <button
          onClick={() => setTab("cover")}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${
            tab === "cover" ? "bg-[var(--surface0)] text-[var(--blue)] font-semibold" : "text-[var(--subtext)]"
          }`}
        >
          <FileText size={16} /> AI Cover Letter Generator
        </button>
        <button
          onClick={() => setTab("linkedin")}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${
            tab === "linkedin" ? "bg-[var(--surface0)] text-[var(--mauve)] font-semibold" : "text-[var(--subtext)]"
          }`}
        >
          <Share2 size={16} /> LinkedIn Post Creator
        </button>
      </div>

      {/* Cover Letter Tab */}
      {tab === "cover" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <form onSubmit={handleCoverLetter} className="glass p-6 rounded-2xl space-y-4">
            <h3 className="font-semibold text-lg">Job Details</h3>
            <div>
              <label className="block text-xs text-[var(--subtext)] mb-1">Target Role</label>
              <input className="input" value={role} onChange={(e) => setRole(e.target.value)} required />
            </div>
            <div>
              <label className="block text-xs text-[var(--subtext)] mb-1">Company Name</label>
              <input className="input" value={company} onChange={(e) => setCompany(e.target.value)} required />
            </div>
            <div>
              <label className="block text-xs text-[var(--subtext)] mb-1">Job Description Snippet (Optional)</label>
              <textarea
                rows={4}
                className="input resize-none"
                placeholder="Paste key responsibilities or requirements..."
                value={jobDesc}
                onChange={(e) => setJobDesc(e.target.value)}
              />
            </div>
            <button type="submit" disabled={loadingCover} className="btn-primary w-full justify-center">
              <Sparkles size={16} /> Generate Cover Letter
            </button>
          </form>

          <div className="glass p-6 rounded-2xl space-y-3 relative flex flex-col justify-between">
            <div>
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-semibold text-lg">Generated Cover Letter</h3>
                {coverOutput && (
                  <button onClick={() => copyToClipboard(coverOutput)} className="btn-ghost text-xs">
                    {copied ? <Check size={14} /> : <Copy size={14} />} Copy
                  </button>
                )}
              </div>
              <textarea
                readOnly
                rows={14}
                className="input border-none bg-[var(--surface0)] font-sans text-xs leading-relaxed resize-none w-full p-4 rounded-xl"
                value={coverOutput || "Your AI cover letter will appear here..."}
              />
            </div>
          </div>
        </div>
      )}

      {/* LinkedIn Post Tab */}
      {tab === "linkedin" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <form onSubmit={handleLinkedIn} className="glass p-6 rounded-2xl space-y-4">
            <h3 className="font-semibold text-lg">Project Highlights</h3>
            <div>
              <label className="block text-xs text-[var(--subtext)] mb-1">Project Name</label>
              <input className="input" value={projectTitle} onChange={(e) => setProjectTitle(e.target.value)} required />
            </div>
            <div>
              <label className="block text-xs text-[var(--subtext)] mb-1">Tech Stack</label>
              <input className="input" value={techStack} onChange={(e) => setTechStack(e.target.value)} required />
            </div>
            <div>
              <label className="block text-xs text-[var(--subtext)] mb-1">Key Features / Achievements</label>
              <textarea
                rows={3}
                className="input resize-none"
                value={highlights}
                onChange={(e) => setHighlights(e.target.value)}
              />
            </div>
            <button type="submit" disabled={loadingLinkedin} className="btn-primary w-full justify-center">
              <Sparkles size={16} /> Generate LinkedIn Post
            </button>
          </form>

          <div className="glass p-6 rounded-2xl space-y-3 flex flex-col justify-between">
            <div>
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-semibold text-lg">Generated LinkedIn Post</h3>
                {linkedinOutput && (
                  <button onClick={() => copyToClipboard(linkedinOutput)} className="btn-ghost text-xs">
                    {copied ? <Check size={14} /> : <Copy size={14} />} Copy
                  </button>
                )}
              </div>
              <textarea
                readOnly
                rows={12}
                className="input border-none bg-[var(--surface0)] font-sans text-xs leading-relaxed resize-none w-full p-4 rounded-xl text-[var(--text)]"
                value={linkedinOutput || "Your LinkedIn post content will appear here..."}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
