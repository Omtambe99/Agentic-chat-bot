import json
from pathlib import Path


REQUIRED_KEYS = {"test_id", "body", "cta", "send_as", "suppression_key", "rationale"}


def evaluate(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    problems = []
    seen_ids = set()

    for index, line in enumerate(lines, start=1):
        if not line.strip():
            problems.append(f"Line {index}: empty line")
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            problems.append(f"Line {index}: invalid JSON ({exc})")
            continue

        missing = REQUIRED_KEYS - item.keys()
        if missing:
            problems.append(f"Line {index}: missing keys {sorted(missing)}")

        test_id = item.get("test_id")
        if not test_id:
            problems.append(f"Line {index}: missing test_id")
        elif test_id in seen_ids:
            problems.append(f"Line {index}: duplicate test_id {test_id}")
        else:
            seen_ids.add(test_id)

        cta = item.get("cta")
        if cta not in {"YES/STOP", "open_ended", "none"}:
            problems.append(f"Line {index}: invalid cta {cta}")

        send_as = item.get("send_as")
        if send_as not in {"vera", "merchant_on_behalf"}:
            problems.append(f"Line {index}: invalid send_as {send_as}")

        body = item.get("body", "")
        if not body or len(body) < 10:
            problems.append(f"Line {index}: body too short")

    return {"count": len(lines), "valid": not problems, "problems": problems}


if __name__ == "__main__":
    import sys

    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "submission.jsonl"
    result = evaluate(target)
    print(json.dumps(result, indent=2, ensure_ascii=False))