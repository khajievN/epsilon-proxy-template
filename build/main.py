import json
import os

import matplotlib.pyplot as plt
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


def main():
    out_dir = os.environ.get("EPSILON_OUTPUT_DIR", "outputs")
    os.makedirs(out_dir, exist_ok=True)

    df = pd.read_csv("generated/data.csv")
    for col in NUMERIC:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    print(f"Loaded {len(df)} records")

    # Mean of the numeric measures per gender and diabetic outcome
    groups = df.groupby(["demographics.gender", "outcome.diabetic"])
    summary = groups[NUMERIC].mean().round(2)
    summary.insert(0, "n", groups.size())
    summary = summary[summary["n"] >= MIN_CELL]
    summary.to_csv(os.path.join(out_dir, "summary_by_group.csv"))

    # Counts per gender and outcome
    counts = df.groupby(["demographics.gender", "outcome.diabetic"]).size()
    counts = counts[counts >= MIN_CELL]
    with open(os.path.join(out_dir, "counts.json"), "w") as f:
        json.dump(
            {
                "total": int(len(df)),
                "min_cell": MIN_CELL,
                "counts": {f"{g} / {o}": int(n) for (g, o), n in counts.items()},
            },
            f,
            indent=2,
        )

    # Mean BMI by gender and diabetic outcome
    bmi = summary["anthropometry.bmi"].unstack("outcome.diabetic")
    ax = bmi.plot(kind="bar", rot=0, title=f"Mean BMI by gender and diabetic outcome (n >= {MIN_CELL})")
    ax.set_xlabel("Gender")
    ax.set_ylabel("Mean BMI")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "bmi_by_group.png"), dpi=100)

    print(summary.to_string())
    print(f"Wrote {sorted(os.listdir(out_dir))}")
    return {"result": "Analysis complete", "groups": int(len(summary))}


if __name__ == "__main__":
    result = main()
    print(result)
