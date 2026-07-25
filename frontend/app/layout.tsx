import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "react-hot-toast";
import { AuthProvider } from "@/contexts/AuthContext";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "SkillBridge AI — Your AI Career Mentor",
  description:
    "AI-powered career mentoring platform for students. Resume analysis, roadmaps, mock interviews, GitHub analyzer, and job matching — all in one place.",
  keywords: ["career mentor", "resume analyzer", "AI", "students", "internship", "roadmap"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans antialiased`}>
        <AuthProvider>
          {children}
          <Toaster
            position="top-right"
            toastOptions={{
              style: {
                background: "#1e1e2e",
                color: "#cdd6f4",
                border: "1px solid #313244",
              },
            }}
          />
        </AuthProvider>
      </body>
    </html>
  );
}
