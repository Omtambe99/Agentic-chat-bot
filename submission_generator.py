import json
import subprocess
import sys
from pathlib import Path
from bot import compose


def ensure_expanded_dataset(project_dir: Path) -> Path:
    expanded_dir = project_dir / "expanded"
    if (expanded_dir / "categories").exists() and (expanded_dir / "merchants").exists() and (expanded_dir / "triggers").exists():
        return expanded_dir

    generator = project_dir / "dataset" / "generate_dataset.py"
    if not generator.exists():
        raise FileNotFoundError(f"Missing dataset generator: {generator}")

    subprocess.run(
        [sys.executable, str(generator), "--seed-dir", str(project_dir / "dataset"), "--out", str(expanded_dir)],
        check=True,
        cwd=str(project_dir),
    )
    return expanded_dir


def build_submission(dataset_dir: Path, output_path: Path, test_pairs: int = 30):
    categories = list((dataset_dir / "categories").glob("*.json"))
    merchants = list((dataset_dir / "merchants").glob("*.json"))
    customers = list((dataset_dir / "customers").glob("*.json"))
    triggers = list((dataset_dir / "triggers").glob("*.json"))

    # Simple deterministic selection: pick first N triggers that reference a merchant
    selected = []
    for tpath in triggers:
        if len(selected) >= test_pairs:
            break
        t = json.loads(tpath.read_text())
        mid = t.get("merchant_id") or t.get("payload", {}).get("merchant_id")
        if not mid:
            continue
        # find merchant file for this id
        mpath = next((m for m in merchants if mid == m.stem), None)
        if not mpath:
            # fallback: pick first merchant
            mpath = merchants[0]
        m = json.loads(mpath.read_text())
        customer = None
        customer_id = t.get("customer_id") or t.get("payload", {}).get("customer_id")
        if customer_id:
            cpath = next((c for c in customers if customer_id == c.stem), None)
            if cpath:
                customer = json.loads(cpath.read_text())
        # find category for merchant
        cat_slug = m.get("category_slug") or m.get("identity", {}).get("category") or ""
        cpath = next((c for c in categories if c.stem == cat_slug), None) or categories[0]
        c = json.loads(cpath.read_text())

        out = compose(c, m, t, customer)
        selected.append({
            "test_id": t.get("id") or tpath.stem,
            **out
        })

    # Write JSONL
    with output_path.open("w", encoding="utf-8") as f:
        for item in selected:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"Wrote {len(selected)} lines to {output_path}")


if __name__ == "__main__":
    project_dir = Path(__file__).parent
    ds = ensure_expanded_dataset(project_dir)
    out = Path(__file__).parent / "submission.jsonl"
    build_submission(ds, out, test_pairs=30)
