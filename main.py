import json
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Groups smaller than this are suppressed in every output
MIN_CELL = 10

NUMERIC = [
    "demographics.age",
    "anthropometry.bmi",
    "labs.glucose",
    "vitals.systolic_bp",
    "vitals.diastolic_bp",
]

GROUP_BY = ["demographics.gender", "outcome.diabetic"]


def main():
    out_dir = os.environ.get("EPSILON_OUTPUT_DIR", "outputs")
    for sub in ("tables", "plots", "model"):
        os.makedirs(os.path.join(out_dir, sub), exist_ok=True)

    df = pd.read_csv("generated/data.csv")
    print(f"Loaded {len(df)} records, columns: {sorted(df.columns)}")

    # The real dataset may not have every column the dummy data has
    numeric = [c for c in NUMERIC if c in df.columns]
    missing = [c for c in NUMERIC + GROUP_BY if c not in df.columns]
    if missing:
        print(f"Skipping missing columns: {missing}")
    group_by = [c for c in GROUP_BY if c in df.columns]
    if not group_by or not numeric:
        raise SystemExit("No grouping or numeric columns available")
    for col in numeric:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Mean of the numeric measures per gender and diabetic outcome
    groups = df.groupby(group_by)
    summary = groups[numeric].mean().round(2)
    summary.insert(0, "n", groups.size())
    summary = summary[summary["n"] >= MIN_CELL]
    summary.to_csv(os.path.join(out_dir, "tables", "summary_by_group.csv"))

    # Counts per gender and outcome
    counts = groups.size()
    counts = counts[counts >= MIN_CELL]
    with open(os.path.join(out_dir, "counts.json"), "w") as f:
        json.dump(
            {
                "total": int(len(df)),
                "min_cell": MIN_CELL,
                "group_by": group_by,
                "counts": {" / ".join(map(str, k if isinstance(k, tuple) else (k,))): int(n) for k, n in counts.items()},
            },
            f,
            indent=2,
        )

    # Mean of the first available measure (BMI when present) per group
    measure = "anthropometry.bmi" if "anthropometry.bmi" in numeric else numeric[0]
    series = summary[measure]
    data = series.unstack(group_by[-1]) if len(group_by) > 1 else series
    ax = data.plot(kind="bar", rot=0, title=f"Mean {measure} by group (n >= {MIN_CELL})")
    ax.set_ylabel(f"Mean {measure}")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "plots", "bmi_by_group.png"), dpi=100)

    # Group means as a numpy array (a file type with no preview)
    np.save(os.path.join(out_dir, "model", "group_means.npy"), summary[numeric].to_numpy())

    # Short markdown report (no preview either; download only)
    with open(os.path.join(out_dir, "report.md"), "w") as f:
        f.write("# Diabetes risk summary\n\n")
        f.write(f"Records: {len(df)}. Groups with fewer than {MIN_CELL} people are suppressed.\n\n")
        f.write(f"Measures: {', '.join(numeric)}\n")

    print(summary.to_string())
    written = sorted(
        os.path.relpath(os.path.join(root, name), out_dir)
        for root, _, names in os.walk(out_dir)
        for name in names
    )
    print(f"Wrote {written}")
    return {"result": "Analysis complete", "groups": int(len(summary))}


if __name__ == "__main__":
    result = main()
    print(result)
