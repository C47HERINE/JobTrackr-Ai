import os
import requests


class Evaluator:
    """LLM-based job classifier."""
    def __init__(self, llm):

        # Define which job fields are used to build the LLM input.
        self.sections = ['title', 'job_type', 'skills', 'description']
        self.ollama_endpoint = "http://10.10.10.5:11434/api/chat"

        # Load and concatenate all user context files once at init.
        self.user_data = "".join(open(os.path.join('user/data/', f)).read() for f in os.listdir('user/data'))
        self.llm = llm


    def load_job_string(self, data: dict):
        """Flatten selected job fields into a single prompt string"""
        string = ''
        for section in self.sections:
            value = data.get(section)
            if value:
                string += data[section]
                string += '\n'
        return string


    def send_chat(self, prompt: str) -> str:
        """Send a single prompt to Ollama and return the model response."""
        payload = {"model": self.llm, "messages": [{"role": "user", "content": prompt}], "stream": False}
        response = requests.post(self.ollama_endpoint, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        content = data["message"]["content"]
        return content.strip()


    def get_advice(self, job_dict: dict) -> dict:

        # Skip if already classified.
        if job_dict.get("should_apply") in ("apply", "pass"):
            return job_dict

        # Build prompt input from job data.
        job_information = self.load_job_string(job_dict)
        prompt = (
            "You are a hiring-screening classifier. Decide whether the candidate is a match for this job.\n\n"
            "Rules:\n"
            "- The FIRST word of your reply MUST be exactly either: apply or pass.\n"
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

        # Retry until a valid decision token is extracted or attempts exhausted.
        while attempt < max_attempts:
            answer = self.send_chat(prompt)
            decision = None
            words = answer.lower().split()

            # Extract first word and normalize punctuation.
            if words:
                first_word = words[0].strip(".,:;!?()[]\"'")
                if first_word in ("apply", "pass"):
                    decision = first_word
            if decision:
                print(job_dict["title"], decision)
                break
            attempt += 1

        # Fallback when the model fails to follow the format.
        if decision not in ("apply", "pass"):
            decision = "error"

        # Persist decision and explanation into the job object.
        job_dict["should_apply"] = decision
        job_dict["answer"] = answer
        return job_dict