import json
import re
from pathlib import Path
from statistics import mean


NUM_RE = re.compile(r"\b\d+(?:\.\d+)?\b")
RUPEE_RE = re.compile(r"₹\s?\d+|Rs\.?\s?\d+", re.IGNORECASE)
DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}\s+[A-Za-z]{3,9}\b")


def score_output(output: dict) -> dict:
    body = output.get("body", "")
    cta = output.get("cta", "")

    specificity = 0
    if NUM_RE.search(body):
        specificity += 4
    if RUPEE_RE.search(body):
        specificity += 2
    if DATE_RE.search(body):
        specificity += 2
    if len(body) > 80:
        specificity += 1
    specificity = min(10, specificity)

    category_fit = 5
    if any(token in body.lower() for token in ["dental", "salon", "gym", "pharmacy", "restaurant"]):
        category_fit += 2
    if any(token in body.lower() for token in ["fluoride", "aligner", "whitening", "review", "offer", "post"]):
        category_fit += 2
    category_fit = min(10, category_fit)

    merchant_fit = 0
    if any(token in body.lower() for token in ["hi", "doc", "dr.", "owner", "manager"]):
        merchant_fit += 2
    if any(token in body.lower() for token in ["you", "your", "dashboard", "listing", "post", "renewal"]):
        merchant_fit += 3
    merchant_fit = min(10, merchant_fit)

    trigger_relevance = 0
    if any(token in body.lower() for token in ["why now", "heads-up", "due", "upcoming", "stale", "spike", "dip", "nearby"]):
        trigger_relevance += 4
    if cta in {"YES/STOP", "open_ended", "none"}:
        trigger_relevance += 2
    trigger_relevance = min(10, trigger_relevance)

    engagement = 0
    if cta == "YES/STOP":
        engagement += 4
    if any(token in body.lower() for token in ["want", "reply", "draft", "summary", "checklist", "help"]):
        engagement += 4
    if any(token in body.lower() for token in ["quick", "simple", "ready", "one-line"]):
        engagement += 2
    engagement = min(10, engagement)

    total = specificity + category_fit + merchant_fit + trigger_relevance + engagement
    return {
        "specificity": specificity,
        "category_fit": category_fit,
        "merchant_fit": merchant_fit,
        "trigger_relevance": trigger_relevance,
        "engagement": engagement,
        "total": total,
    }


def evaluate_file(submission_path: Path) -> dict:
    rows = [json.loads(line) for line in submission_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    scores = [score_output(row) for row in rows]
    return {
        "count": len(scores),
        "average_total": round(mean(score["total"] for score in scores), 2) if scores else 0,
        "average_specificity": round(mean(score["specificity"] for score in scores), 2) if scores else 0,
        "average_category_fit": round(mean(score["category_fit"] for score in scores), 2) if scores else 0,
        "average_merchant_fit": round(mean(score["merchant_fit"] for score in scores), 2) if scores else 0,
        "average_trigger_relevance": round(mean(score["trigger_relevance"] for score in scores), 2) if scores else 0,
        "average_engagement": round(mean(score["engagement"] for score in scores), 2) if scores else 0,
        "scores": scores,
    }


if __name__ == "__main__":
    target = Path(__file__).parent / "submission.jsonl"
    print(json.dumps(evaluate_file(target), indent=2, ensure_ascii=False))