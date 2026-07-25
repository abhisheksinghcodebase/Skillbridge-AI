"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import {
  Brain, FileText, Map, Lightbulb, Mic,
  BarChart3, Briefcase, LogOut, User, Menu, X, Zap, Globe, Sparkles
} from "lucide-react";
import { GithubIcon } from "@/components/Icons";
import { useState } from "react";
import { clsx } from "clsx";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: BarChart3 },
  { href: "/resume", label: "Resume Analyzer", icon: FileText },
  { href: "/mentor", label: "AI Mentor", icon: Brain },
  { href: "/roadmap", label: "Roadmap", icon: Map },
  { href: "/projects", label: "Projects", icon: Lightbulb },
  { href: "/github", label: "GitHub Analyzer", icon: GithubIcon },
  { href: "/interview", label: "Mock Interview", icon: Mic },
  { href: "/tracker", label: "Learning Tracker", icon: BarChart3 },
  { href: "/jobs", label: "Job Matching", icon: Briefcase },
  { href: "/portfolio", label: "Portfolio Audit", icon: Globe },
  { href: "/tools", label: "AI Career Tools", icon: Sparkles },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();
  const [collapsed, setCollapsed] = useState(false);

  const handleLogout = () => {
    logout();
    router.push("/");
  };

  return (
    <aside
      className={clsx(
        "flex flex-col h-screen sticky top-0 transition-all duration-300 ease-in-out",
        "border-r border-[var(--surface0)]",
        collapsed ? "w-16" : "w-60"
      )}
      style={{ background: "var(--mantle)" }}
    >
      {/* Logo */}
      <div className="flex items-center justify-between p-4 border-b border-[var(--surface0)]">
        {!collapsed && (
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center"
              style={{ background: "var(--gradient-primary)" }}>
              <Zap size={16} className="text-[var(--crust)]" />
            </div>
            <span className="font-bold text-sm gradient-text">SkillBridge AI</span>
          </Link>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="btn-ghost p-1.5 ml-auto"
        >
          {collapsed ? <Menu size={18} /> : <X size={18} />}
        </button>
      </div>

      {/* Nav Items */}
      <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-1">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || pathname.startsWith(href + "/");
          return (
            <Link
              key={href}
              href={href}
              className={clsx(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150",
                active
                  ? "bg-[rgba(137,180,250,0.12)] text-[var(--blue)] border-l-2 border-[var(--blue)] pl-[10px]"
                  : "text-[var(--subtext)] hover:bg-[var(--surface0)] hover:text-[var(--text)]"
              )}
              title={collapsed ? label : undefined}
            >
              <Icon size={18} className="shrink-0" />
              {!collapsed && <span>{label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* User Footer */}
      <div className="p-3 border-t border-[var(--surface0)] space-y-1">
        {user && !collapsed && (
          <div className="flex items-center gap-3 px-3 py-2 mb-1">
            <div className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0"
              style={{ background: "var(--gradient-primary)", color: "var(--crust)" }}>
              {user.name[0].toUpperCase()}
            </div>
            <div className="overflow-hidden">
              <p className="text-sm font-medium text-[var(--text)] truncate">{user.name}</p>
              <p className="text-xs text-[var(--overlay0)] truncate">{user.email}</p>
            </div>
          </div>
        )}
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2 w-full rounded-lg text-sm text-[var(--subtext)] hover:bg-[var(--surface0)] hover:text-[var(--pink)] transition-all"
          title={collapsed ? "Logout" : undefined}
        >
          <LogOut size={18} className="shrink-0" />
          {!collapsed && <span>Logout</span>}
        </button>
      </div>
    </aside>
  );
}
