import os
import requests


class Evaluator:
    def __init__(self):
        self.sections = ['title', 'job_type', 'skills', 'description']
        self.ollama_endpoint = "http://10.10.10.5:11434/api/chat"
        self.user_data = "".join(open(os.path.join('user/data/', f)).read() for f in os.listdir('user/data'))


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


    def get_advice(self, job_dict: dict) -> dict:
        if job_dict.get("should_apply") in ("apply", "pass"):
            return job_dict
        job_information = self.load_job_string(job_dict)
        prompt = (
            "You are a hiring-screening classifier. Decide whether the candidate is a match for this job.\n\n"
            "Rules:\n"
            "- The FIRST word of your reply MUST be exactly either: apply or pass (lowercase).\n"
            "- After the first word, provide a clear explanation referencing evidence from the candidate context and the job description.\n"
            "- The explanation should justify the decision and may include multiple sentences if needed.\n\n"
            f"Candidate Context:\n{self.user_data}\n\n"
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
            decision = None
            words = answer.lower().split()
            if words:
                first_word = words[0].strip(".,:;!?()[]\"'")
                if first_word in ("apply", "pass"):
                    decision = first_word
            if decision:
                break
            attempt += 1
        if decision not in ("apply", "pass"):
            decision = "error"
        job_dict["should_apply"] = decision
        job_dict["answer"] = answer
        return job_dict