"use client";
import { useState, useEffect } from "react";
import { projectsApi } from "@/lib/api";
import { Lightbulb, ExternalLink, Sparkles, Layers } from "lucide-react";
import toast from "react-hot-toast";

export default function ProjectsPage() {
  const [skills, setSkills] = useState("Python, React, FastAPI");
  const [goal, setGoal] = useState("Full Stack Developer");
  const [loading, setLoading] = useState(false);
  const [projects, setProjects] = useState<any[]>([]);

  const handleFetch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setLoading(true);
    try {
      const res = await projectsApi.recommend({
        skills: skills.split(",").map((s) => s.trim()),
        goal,
      });
      setProjects(res.data?.projects || []);
      toast.success("Generated project ideas!");
    } catch (err) {
      toast.error("Failed to recommend projects");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleFetch();
  }, []);

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Lightbulb className="text-[var(--yellow)]" /> Project Recommendation Engine
        </h1>
        <p className="text-[var(--subtext)] text-sm mt-1">
          Generate tailored project ideas with full tech stacks and GitHub resources to build your portfolio.
        </p>
      </div>

      <form onSubmit={handleFetch} className="glass p-6 rounded-2xl grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-xs text-[var(--subtext)] mb-1">Your Skills</label>
          <input className="input" value={skills} onChange={(e) => setSkills(e.target.value)} />
        </div>
        <div>
          <label className="block text-xs text-[var(--subtext)] mb-1">Target Goal</label>
          <input className="input" value={goal} onChange={(e) => setGoal(e.target.value)} />
        </div>
        <div className="flex items-end">
          <button type="submit" disabled={loading} className="btn-primary w-full justify-center">
            <Sparkles size={16} /> Recommend Projects
          </button>
        </div>
      </form>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {projects.map((p) => (
          <div key={p.id} className="glass p-6 rounded-2xl card-hover flex flex-col justify-between space-y-4">
            <div>
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-bold text-lg text-[var(--text)]">{p.title}</h3>
                <span className="badge badge-yellow text-xs">{p.difficulty}</span>
              </div>
              <p className="text-xs text-[var(--subtext)] leading-relaxed">{p.description}</p>
            </div>

            <div className="space-y-3">
              <div>
                <span className="text-[10px] text-[var(--overlay0)] uppercase font-semibold">Tech Stack</span>
                <div className="flex flex-wrap gap-1.5 mt-1">
                  {p.tech_stack?.map((t: string) => (
                    <span key={t} className="badge badge-blue text-[10px]">{t}</span>
                  ))}
                </div>
              </div>

              {p.github_starter && (
                <a
                  href={p.github_starter}
                  target="_blank"
                  rel="noreferrer"
                  className="btn-secondary text-xs w-full justify-center py-2"
                >
                  Find Starter Repos <ExternalLink size={12} />
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
