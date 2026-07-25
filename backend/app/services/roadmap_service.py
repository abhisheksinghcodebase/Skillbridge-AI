"""
Roadmap generation service using Groq LLM.
"""
import json
from typing import Optional, List

from app.services.groq_service import groq_service

ROADMAP_PROMPT = """You are an expert career coach and tech educator.
Generate a detailed, structured learning roadmap for the goal provided.
Return a JSON object with this EXACT structure:

{{
  "goal": "...",
  "estimated_months": <integer>,
  "phases": [
    {{
      "phase": 1,
      "title": "Foundation",
      "duration_weeks": 4,
      "nodes": [
        {{
          "id": "node-1",
          "title": "Topic Name",
          "description": "Brief what and why",
          "resources": ["Resource 1", "Resource 2"],
          "difficulty": "beginner|intermediate|advanced",
          "estimated_hours": 20,
          "prerequisites": [],
          "skills_gained": ["skill1", "skill2"]
        }}
      ]
    }}
  ],
  "final_projects": ["Project idea 1", "Project idea 2", "Project idea 3"],
  "job_titles": ["Title 1", "Title 2"],
  "tips": ["Tip 1", "Tip 2"]
}}

Be specific, practical, and realistic. Include 4-6 phases.
Current skills of the student (skip basics they already know): {current_skills}
Goal: {goal}
"""


async def generate_roadmap(goal: str, current_skills: Optional[List[str]] = None) -> dict:
    """Generate a structured learning roadmap for the given career goal."""
    skills_str = ", ".join(current_skills) if current_skills else "None mentioned"

    prompt = ROADMAP_PROMPT.format(goal=goal, current_skills=skills_str)

    messages = [
        {
            "role": "system",
            "content": "You are a career roadmap expert. Always respond with valid JSON only.",
        },
        {"role": "user", "content": prompt},
    ]

    try:
        response = await groq_service.chat_completion(
            messages=messages,
            temperature=0.4,
            max_tokens=4096,
            json_mode=True,
        )
        data = json.loads(response)
        # Ensure goal is included
        data["goal"] = goal
        return data
    except Exception:
        return _mock_roadmap(goal)


def _mock_roadmap(goal: str) -> dict:
    return {
        "goal": goal,
        "estimated_months": 6,
        "phases": [
            {
                "phase": 1,
                "title": "Python Fundamentals",
                "duration_weeks": 4,
                "nodes": [
                    {
                        "id": "node-1",
                        "title": "Python Basics",
                        "description": "Variables, data types, control flow, functions",
                        "resources": ["Python.org Tutorial", "CS50P", "Automate the Boring Stuff"],
                        "difficulty": "beginner",
                        "estimated_hours": 30,
                        "prerequisites": [],
                        "skills_gained": ["Python", "Programming Logic"],
                    },
                    {
                        "id": "node-2",
                        "title": "Data Structures & Algorithms",
                        "description": "Lists, dicts, arrays, sorting, searching",
                        "resources": ["LeetCode Easy problems", "GeeksforGeeks"],
                        "difficulty": "beginner",
                        "estimated_hours": 40,
                        "prerequisites": ["node-1"],
                        "skills_gained": ["DSA", "Problem Solving"],
                    },
                ],
            },
            {
                "phase": 2,
                "title": "Data Science Core",
                "duration_weeks": 6,
                "nodes": [
                    {
                        "id": "node-3",
                        "title": "NumPy & Pandas",
                        "description": "Data manipulation and numerical computing",
                        "resources": ["Kaggle Learn", "Pandas documentation"],
                        "difficulty": "intermediate",
                        "estimated_hours": 25,
                        "prerequisites": ["node-1"],
                        "skills_gained": ["NumPy", "Pandas", "Data Manipulation"],
                    },
                    {
                        "id": "node-4",
                        "title": "Data Visualization",
                        "description": "Matplotlib, Seaborn for exploratory analysis",
                        "resources": ["Matplotlib gallery", "Seaborn tutorial"],
                        "difficulty": "intermediate",
                        "estimated_hours": 15,
                        "prerequisites": ["node-3"],
                        "skills_gained": ["Matplotlib", "Seaborn", "EDA"],
                    },
                ],
            },
            {
                "phase": 3,
                "title": "Machine Learning",
                "duration_weeks": 8,
                "nodes": [
                    {
                        "id": "node-5",
                        "title": "Classical ML",
                        "description": "Scikit-learn, regression, classification, clustering",
                        "resources": ["Scikit-learn docs", "fast.ai", "Hands-on ML book"],
                        "difficulty": "intermediate",
                        "estimated_hours": 60,
                        "prerequisites": ["node-3"],
                        "skills_gained": ["Scikit-learn", "Machine Learning", "Model Evaluation"],
                    },
                ],
            },
        ],
        "final_projects": [
            "Build a sentiment analysis model on Twitter data",
            "Create a house price prediction system",
            "Develop an image classifier with transfer learning",
        ],
        "job_titles": ["ML Engineer", "Data Scientist", "AI Engineer"],
        "tips": [
            "Build projects as you learn each topic",
            "Participate in Kaggle competitions",
            "Read ML papers on ArXiv regularly",
        ],
    }
