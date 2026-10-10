
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_api_key = os.getenv("GROQ_API_KEY")
_client = Groq(api_key=_api_key) if _api_key else None

# Use a model available to your Groq account.
MODEL = "openai/gpt-oss-20b"


def generate_hr_answer(message: str, candidate_context: str = "") -> str:
    """Generate a natural HR answer using the LLM."""

    if _client is None:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Check the backend .env file."
        )

    response = _client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are FairHire AI, a helpful HR recruiting assistant. "
                    "Answer clearly and naturally. Use only the supplied "
                    "candidate information for candidate-specific claims. "
                    "Never invent candidate skills, experience, qualifications, "
                    "or scores. If information is missing, say so. "
                    "Support fair, job-related evaluation and do not infer "
                    "protected characteristics."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Candidate information:\n{candidate_context or 'No candidate selected.'}"
                    f"\n\nHR question:\n{message}"
                ),
            },
        ],
        temperature=0.3,
        max_tokens=500,
    )

    answer = response.choices[0].message.content
    return answer.strip() if answer else "I couldn't generate an answer. Please try again."