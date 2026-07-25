"use client";
import { useState } from "react";
import { interviewApi } from "@/lib/api";
import { Mic, Sparkles, CheckCircle2, RefreshCw } from "lucide-react";
import toast from "react-hot-toast";

export default function InterviewPage() {
  const [topic, setTopic] = useState("Data Structures & Algorithms");
  const [session, setSession] = useState<any>(null);
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [evaluating, setEvaluating] = useState(false);

  const getQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setAnswer("");
    try {
      const res = await interviewApi.getQuestion(topic);
      setSession(res.data);
    } catch (err) {
      toast.error("Failed to generate question");
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!answer.trim() || !session) return;
    setEvaluating(true);
    try {
      const res = await interviewApi.evaluate(session.id, answer);
      setSession(res.data);
      toast.success("Answer evaluated!");
    } catch (err) {
      toast.error("Evaluation failed");
    } finally {
      setEvaluating(false);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Mic className="text-[var(--pink)]" /> Mock Interview Simulator
        </h1>
        <p className="text-[var(--subtext)] text-sm mt-1">
          Practice technical & behavioral questions. Groq AI evaluates confidence, accuracy, and grammar.
        </p>
      </div>

      <form onSubmit={getQuestion} className="glass p-4 rounded-xl flex gap-3">
        <input
          type="text"
          className="input flex-1"
          placeholder="Topic (e.g. System Design, Python, Behavior)..."
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
        />
        <button type="submit" disabled={loading} className="btn-primary shrink-0">
          {loading ? <RefreshCw className="animate-spin" size={16} /> : <Sparkles size={16} />} Get Question
        </button>
      </form>

      {session && (
        <div className="glass p-8 rounded-2xl space-y-6">
          <div>
            <span className="badge badge-pink text-xs uppercase font-semibold">Question</span>
            <h2 className="text-xl font-semibold mt-2 text-[var(--text)]">{session.question}</h2>
          </div>

          <div className="space-y-3">
            <label className="block text-xs text-[var(--subtext)]">Your Response</label>
            <textarea
              rows={5}
              className="input w-full resize-none"
              placeholder="Type your structured answer here..."
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              disabled={Boolean(session.feedback)}
            />
          </div>

          {!session.feedback && (
            <button
              onClick={submitAnswer}
              disabled={!answer.trim() || evaluating}
              className="btn-primary w-full justify-center py-3"
            >
              {evaluating ? "Evaluating Answer..." : "Submit Answer for Feedback"}
            </button>
          )}

          {session.feedback && (
            <div className="border-t border-[var(--surface0)] pt-6 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-lg flex items-center gap-2">
                  <CheckCircle2 size={18} className="text-[var(--green)]" /> AI Feedback & Scoring
                </h3>
                <span className="text-2xl font-bold text-[var(--blue)]">{session.score}/100</span>
              </div>
              <p className="text-xs text-[var(--subtext)] leading-relaxed">
                {session.feedback.overall_feedback}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
