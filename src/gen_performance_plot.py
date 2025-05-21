"""
Given the reports in the reports folder, this script will generate a single plot containing the performance scores of all models.
"""

import json
import matplotlib.pyplot as plt
import os

def load_performance(report_path):
    """
    Load the report from the given path.
    """
    with open(report_path, "r") as f:
        report = json.load(f)["performance"]

    keys = list(map(int, report.keys()))
    values = list(map(float, report.values()))
    return keys, values

def get_report_names():
    """
    Get the names of the reports in the reports folder.
    """
    report_names = []
    for file in os.listdir("reports"):
        if file.endswith(".json"):
            report_names.append(file)
    return report_names

if __name__ == "__main__":
    reports = get_report_names()

    scores = []
    for rep in reports:
        report_path = os.path.join("reports", rep)
        performance = load_performance(report_path)
        scores.append(performance)

    # Create a plot
    fig, ax = plt.subplots(figsize=(10, 6))
    for i, (keys, values) in enumerate(scores):
        ax.plot(keys, values, label=reports[i].replace(".json", ""))
    ax.set_xlabel("Number of Delegations")
    ax.set_ylabel("Time (s)")
    ax.set_title("Performance of Delegation Models")
    ax.legend()
    plt.savefig("reports/performance_plot.png")
