"""
Factory for LLM client. Provides a mock client if API key is not set,
allowing the app to function in demo mode without an active Groq API key.
"""
from config import settings
from groq import Groq

class MockMessage:
    def __init__(self, content):
        self.content = content

class MockChoice:
    def __init__(self, content):
        self.message = MockMessage(content)

class MockCompletions:
    def create(self, model, messages, **kwargs):
        system_msg = messages[0]["content"] if messages else ""
        if "career coach and ATS specialist" in system_msg:
            content = """{
  "overall_score": 92,
  "match_summary": "Exceptional fit for this AI / ML Engineer role. Your background aligns perfectly with their requirements for Machine Learning and production pipelines.",
  "matched_skills": [
    {"skill": "Machine Learning", "evidence": "Resume projects and experience", "importance": "high"},
    {"skill": "Production deployment", "evidence": "Model deployment experience", "importance": "high"}
  ],
  "skill_gaps": [
    {"skill": "Cloud AI Services (AWS/GCP)", "importance": "medium", "suggestion": "Highlight any cloud platforms you've used for ML workloads"}
  ],
  "emphasis_points": [
    "Emphasize the scale of the models you have deployed",
    "Highlight cross-functional collaboration in productionizing AI"
  ],
  "keywords_to_add": ["Computational Science", "Cloud AI", "On-prem"],
  "red_flags": []
}"""
        elif "resume writer and ATS" in system_msg:
            content = """{
  "full_rewrite": "Aayush Bari\\nAI / ML Engineer\\n\\nEXPERIENCE\\nMachine Learning Engineer\\n- Developed and deployed production-ready Machine Learning (ML) models.\\n- Utilized AI tools to build scalable computational science applications.\\n- Managed cloud and on-prem application pipelines ensuring production-ready quality.\\n",
  "sections": [
    {
      "section_name": "Experience",
      "original": "Worked on various ML models and deployed them.",
      "rewritten": "Developed and deployed production-ready Machine Learning (ML) models, utilizing advanced AI tools to build scalable computational science applications."
    }
  ]
}"""
        elif "cover letter writer" in system_msg:
            content = "Dear Hiring Manager,\n\nI am thrilled to submit my application for the AI / ML Engineer position at Accenture. With over 2 years of dedicated experience in Machine Learning and computational science, I have successfully developed applications and systems that leverage AI tools to deliver measurable business impact.\n\nIn my recent projects, I focused heavily on building production-ready pipelines for both cloud and on-premise environments. I am deeply familiar with the challenges of scaling ML models and ensuring they meet rigorous production quality standards. \n\nI admire Accenture's commitment to cutting-edge AI solutions and would be excited to bring my expertise in machine learning and pipeline architecture to your team.\n\nThank you for considering my application. I look forward to discussing how my skills align with your needs in more detail.\n\nSincerely,\nAayush Bari"
        elif "interview coach" in system_msg:
            content = """{
  "questions": [
    {
      "id": 1,
      "type": "technical",
      "question": "Can you describe a machine learning model you deployed to a production environment?",
      "tests": "Understanding of ML deployment, scalable architecture, and production constraints.",
      "sample_answer": "In my previous role, I developed a predictive model using Python and deployed it via a robust CI/CD pipeline. I containerized the application with Docker and ensured it could run efficiently on both cloud and on-prem environments. The key challenge was latency, which I solved by optimizing the inference script.",
      "tips": "Focus on the end-to-end pipeline rather than just the model training. Mention specific tools like Docker, Kubernetes, or specific cloud services."
    },
    {
      "id": 2,
      "type": "behavioural",
      "question": "Tell me about a time you had to balance production-ready quality with a tight deadline.",
      "tests": "Prioritization, quality assurance under pressure.",
      "sample_answer": "We had a critical delivery for a client where the model needed to be deployed in two weeks. I prioritized the core inference API and set up automated testing for it first. We launched the MVP on time, and then I iteratively added more advanced monitoring and logging in the following sprints.",
      "tips": "Use the STAR method (Situation, Task, Action, Result). Highlight that you don't compromise on core quality but are smart about scope."
    }
  ]
}"""
        else:
            content = "{}"
        
        return type("MockResponse", (), {"choices": [MockChoice(content)]})()

class MockChat:
    def __init__(self):
        self.completions = MockCompletions()

class MockGroq:
    def __init__(self, *args, **kwargs):
        self.chat = MockChat()

_client = None

def get_client() -> Groq:
    global _client
    if _client is None:
        if not settings.groq_api_key or settings.groq_api_key == "your_groq_api_key_here":
            _client = MockGroq()
        else:
            _client = Groq(api_key=settings.groq_api_key)
    return _client
