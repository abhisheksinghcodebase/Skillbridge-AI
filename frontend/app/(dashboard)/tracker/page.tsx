"use client";
import { useState, useEffect } from "react";
import { trackerApi } from "@/lib/api";
import { BarChart3, Plus, CheckCircle2, Clock } from "lucide-react";
import toast from "react-hot-toast";

export default function TrackerPage() {
  const [skills, setSkills] = useState<any[]>([]);
  const [newSkill, setNewSkill] = useState("");
  const [category, setCategory] = useState("Languages");

  useEffect(() => {
    async function load() {
      try {
        const res = await trackerApi.getAll();
        setSkills(res.data);
      } catch (err) {}
    }
    load();
  }, []);

  const addSkill = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSkill.trim()) return;
    try {
      const res = await trackerApi.add({
        skill_name: newSkill,
        category,
        progress_percent: 25,
        status: "in_progress",
      });
      setSkills((prev) => [...prev, res.data]);
      setNewSkill("");
      toast.success("Skill added!");
    } catch (err) {
      toast.error("Failed to add skill");
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <BarChart3 className="text-[var(--yellow)]" /> Learning Progress Tracker
        </h1>
        <p className="text-[var(--subtext)] text-sm mt-1">
          Monitor your skill mastery, completion percentage, and active focus areas.
        </p>
      </div>

      <form onSubmit={addSkill} className="glass p-4 rounded-xl flex gap-3">
        <input
          type="text"
          className="input flex-1"
          placeholder="New skill to track (e.g. Docker, TypeScript)..."
          value={newSkill}
          onChange={(e) => setNewSkill(e.target.value)}
        />
        <select className="input w-44" value={category} onChange={(e) => setCategory(e.target.value)}>
          <option value="Languages">Languages</option>
          <option value="Frameworks">Frameworks</option>
          <option value="DevOps">DevOps</option>
          <option value="CS Core">CS Core</option>
        </select>
        <button type="submit" className="btn-primary shrink-0">
          <Plus size={16} /> Add Skill
        </button>
      </form>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {skills.map((s) => (
          <div key={s.id} className="glass p-5 rounded-xl space-y-3">
            <div className="flex justify-between items-center">
              <h3 className="font-semibold text-base">{s.skill_name}</h3>
              <span className="badge badge-yellow text-xs">{s.category || "General"}</span>
            </div>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${s.progress_percent}%` }} />
            </div>
            <div className="flex justify-between text-xs text-[var(--overlay0)]">
              <span>{s.progress_percent}% Completed</span>
              <span className="capitalize">{s.status.replace("_", " ")}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
