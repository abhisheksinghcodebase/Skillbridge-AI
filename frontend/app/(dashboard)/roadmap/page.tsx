"use client";
import { useState, useEffect } from "react";
import { roadmapApi } from "@/lib/api";
import { Map, Sparkles, CheckCircle2, Circle, Clock, ArrowRight } from "lucide-react";
import toast from "react-hot-toast";

export default function RoadmapPage() {
  const [goal, setGoal] = useState("Machine Learning Engineer");
  const [loading, setLoading] = useState(false);
  const [roadmap, setRoadmap] = useState<any>(null);
  const [list, setList] = useState<any[]>([]);

  useEffect(() => {
    async function loadRoadmaps() {
      try {
        const res = await roadmapApi.list();
        setList(res.data);
        if (res.data.length > 0) setRoadmap(res.data[0]);
      } catch (err) {}
    }
    loadRoadmaps();
  }, []);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!goal.trim()) return;
    setLoading(true);
    try {
      const res = await roadmapApi.generate(goal);
      setRoadmap(res.data);
      setList((prev) => [res.data, ...prev]);
      toast.success("Roadmap generated!");
    } catch (err: any) {
      toast.error("Failed to generate roadmap");
    } finally {
      setLoading(false);
    }
  };

  const toggleNode = async (nodeId: string, currentVal: boolean) => {
    if (!roadmap) return;
    try {
      const res = await roadmapApi.updateProgress(roadmap.id, nodeId, !currentVal);
      setRoadmap(res.data);
    } catch (err) {}
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Map className="text-[var(--green)]" /> Personalized Learning Roadmap
        </h1>
        <p className="text-[var(--subtext)] text-sm mt-1">
          Enter a career goal (e.g., Full Stack Dev, ML Engineer) and AI will structure a phased learning tree.
        </p>
      </div>

      {/* Input */}
      <form onSubmit={handleGenerate} className="glass p-4 rounded-xl flex gap-3">
        <input
          type="text"
          className="input flex-1"
          placeholder="Target Role (e.g. DevOps Engineer, Data Scientist)..."
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
        />
        <button type="submit" disabled={loading} className="btn-primary shrink-0">
          <Sparkles size={16} /> Generate Roadmap
        </button>
      </form>

      {/* Roadmap Tree View */}
      {roadmap && (
        <div className="space-y-6">
          <div className="glass p-6 rounded-2xl flex justify-between items-center">
            <div>
              <h2 className="text-xl font-bold">{roadmap.goal}</h2>
              <p className="text-xs text-[var(--subtext)]">Est. {roadmap.roadmap_data?.estimated_months || 6} Months Path</p>
            </div>
            <span className="badge badge-green">Active Goal</span>
          </div>

          <div className="space-y-6">
            {roadmap.roadmap_data?.phases?.map((phase: any) => (
              <div key={phase.phase} className="glass p-6 rounded-2xl space-y-4">
                <div className="flex items-center justify-between border-b border-[var(--surface0)] pb-3">
                  <h3 className="font-semibold text-lg text-[var(--blue)]">
                    Phase {phase.phase}: {phase.title}
                  </h3>
                  <span className="text-xs text-[var(--subtext)] flex items-center gap-1">
                    <Clock size={12} /> {phase.duration_weeks} Weeks
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {phase.nodes?.map((node: any) => {
                    const isDone = Boolean(roadmap.progress?.[node.id]);
                    return (
                      <div
                        key={node.id}
                        onClick={() => toggleNode(node.id, isDone)}
                        className={`p-4 rounded-xl cursor-pointer transition-all border ${
                          isDone
                            ? "bg-[rgba(166,227,161,0.1)] border-[var(--green)]"
                            : "bg-[var(--surface0)] border-[var(--surface1)] hover:border-[var(--blue)]"
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <h4 className="font-semibold text-sm flex items-center gap-2">
                            {isDone ? (
                              <CheckCircle2 size={16} className="text-[var(--green)]" />
                            ) : (
                              <Circle size={16} className="text-[var(--subtext)]" />
                            )}
                            {node.title}
                          </h4>
                          <span className="badge badge-blue text-[10px]">{node.difficulty}</span>
                        </div>
                        <p className="text-xs text-[var(--subtext)] mt-2">{node.description}</p>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
