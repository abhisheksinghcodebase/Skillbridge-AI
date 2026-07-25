"use client";
import { useState } from "react";
import { jobsApi } from "@/lib/api";
import { Briefcase, Sparkles, MapPin, ExternalLink, CheckCircle2 } from "lucide-react";
import toast from "react-hot-toast";

export default function JobsPage() {
  const [skills, setSkills] = useState("Python, React, FastAPI, SQL");
  const [location, setLocation] = useState("Remote");
  const [loading, setLoading] = useState(false);
  const [matches, setMatches] = useState<any[]>([]);

  const handleMatch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setLoading(true);
    try {
      const res = await jobsApi.match({
        skills: skills.split(",").map((s) => s.trim()),
        location,
      });
      setMatches(res.data?.matches || []);
      toast.success("Found job matches!");
    } catch (err) {
      toast.error("Failed to match jobs");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Briefcase className="text-[var(--lavender)]" /> AI Job & Internship Matcher
        </h1>
        <p className="text-[var(--subtext)] text-sm mt-1">
          Calculate skill match percentages, identify missing requirements, and get direct apply links.
        </p>
      </div>

      <form onSubmit={handleMatch} className="glass p-4 rounded-xl flex gap-3">
        <input
          type="text"
          className="input flex-1"
          placeholder="Skills (comma separated)..."
          value={skills}
          onChange={(e) => setSkills(e.target.value)}
        />
        <input
          type="text"
          className="input w-48"
          placeholder="Location preference..."
          value={location}
          onChange={(e) => setLocation(e.target.value)}
        />
        <button type="submit" disabled={loading} className="btn-primary shrink-0">
          <Sparkles size={16} /> Match Jobs
        </button>
      </form>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {matches.map((j) => (
          <div key={j.id} className="glass p-6 rounded-2xl space-y-4">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-bold text-lg">{j.title}</h3>
                <p className="text-xs text-[var(--subtext)] flex items-center gap-1 mt-0.5">
                  <MapPin size={12} /> {j.location} · {j.company_type}
                </p>
              </div>
              <div className="text-right">
                <span className="text-2xl font-bold text-[var(--green)]">{j.match_percent}%</span>
                <p className="text-[10px] text-[var(--overlay0)]">Skill Match</p>
              </div>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex flex-wrap gap-1">
                {j.required_skills?.map((s: string) => (
                  <span key={s} className="badge badge-green text-[10px]">{s}</span>
                ))}
                {j.missing_skills?.map((s: string) => (
                  <span key={s} className="badge badge-red text-[10px]">Missing: {s}</span>
                ))}
              </div>
            </div>

            <a
              href={`https://www.linkedin.com/jobs/search/?keywords=${encodeURIComponent(j.title)}`}
              target="_blank"
              rel="noreferrer"
              className="btn-secondary text-xs w-full justify-center py-2"
            >
              Apply on LinkedIn / Naukri <ExternalLink size={12} />
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}
