import requests


class Evaluator:
    def __init__(self):
        self.sections = ['title', 'job_type', 'skills', 'description']
        self.ollama_endpoint = "http://10.10.10.5:11434/api/chat"


    @staticmethod
    def load_txt(path: str) -> str:
      with open(path, "r", encoding="utf-8") as text_file:
        return text_file.read().strip()


    def load_job_string(self, data: dict):
      string = ''
      for section in self.sections:
        value = data.get(section)
        if value:
          string += data[section]
          string += '\n'
      return string


    def send_chat(self, prompt: str, model: str = "gemma3:12b") -> str:
      payload = {
        "model": model,
        "messages": [
          {"role": "user", "content": prompt}
        ],
        "stream": False
      }
      response = requests.post(self.ollama_endpoint, json=payload, timeout=120)
      response.raise_for_status()
      data = response.json()
      content = data["message"]["content"]
      return content.strip()


    def get_advice(self, data: list):
        user_preference = self.load_txt('user_data/user_preference.txt')
        for d in range(len(data)):
            job_dict = data[d]
            if job_dict.get("should_apply") in ("apply", "pass"):
                continue
            job_information = self.load_job_string(job_dict)
            prompt = (
                "You are a hiring-screening classifier. Decide whether the candidate is a match for this job.\n\n"
                "Rules:\n"
                "- The FIRST word of your reply MUST be exactly either: apply or pass (lowercase).\n"
                "- Output MUST be exactly 2 lines.\n"
                "- Line 1: apply or pass only.\n"
                "- Line 2: a brief reason (max 40 words), "
                "referencing only evidence from the candidate context and job description.\n\n"
                f"Candidate Context:\n{user_preference}\n\n"
                f"Job (JSON):\n{job_information}\n\n"
                "Decision criteria:\n"
                "- apply only if the candidate meets most core requirements and has no major missing blockers.\n"
                "- pass if key requirements are missing or the role is clearly misaligned."
            )
            max_attempts = 3
            attempt = 0
            decision = None
            answer = None
            while attempt < max_attempts:
                answer = self.send_chat(prompt, model="gemma3:12b")
                first_line = answer.splitlines()[0].strip().lower()
                decision = first_line.split()[0]
                if decision in ("apply", "pass"):
                    break
                attempt += 1
            if decision not in ("apply", "pass"):
                decision = "error"
            job_dict["should_apply"] = decision
            job_dict["answer"] = answer
        return data