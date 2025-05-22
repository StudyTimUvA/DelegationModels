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

def load_performance_additional_parties(report_path):
    with open(report_path, "r") as f:
        report = json.load(f)["performance_additional_parties"]

    keys = list(map(int, report.keys()))
    values = list(map(float, report.values()))
    return keys, values

def load_performance_related_additional_parties(report_path):
    with open(report_path, "r") as f:
        report = json.load(f)["performance_related_additional_parties"]

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
    scores_additional_parties = []
    scores_related_additional_parties = []
    for rep in reports:
        report_path = os.path.join("reports", rep)

        performance = load_performance(report_path)
        scores.append(performance)

        performance_additional_parties = load_performance_additional_parties(report_path)
        scores_additional_parties.append(performance_additional_parties)

        performance_related_additional_parties = load_performance_related_additional_parties(report_path)
        scores_related_additional_parties.append(performance_related_additional_parties)

    # Create a plot for plain performance
    fig, ax = plt.subplots(figsize=(10, 6))
    for i, (keys, values) in enumerate(scores):
        ax.plot(keys, values, label=reports[i].replace(".json", ""))
    ax.set_xlabel("Number of Delegations")
    ax.set_ylabel("Time (s)")
    ax.set_title("Performance of Delegation Models")
    ax.legend()
    plt.savefig("reports/performance_plot.png")

    # Create a plot for performance with additional parties
    fig, ax = plt.subplots(figsize=(10, 6))
    for i, (keys, values) in enumerate(scores_additional_parties):
        ax.plot(keys, values, label=reports[i].replace(".json", ""))
    ax.set_xlabel("Number of additional Delegations")
    ax.set_ylabel("Time (s)")
    ax.set_title("Performance of Delegation Models with Additional Parties")
    ax.legend()
    plt.savefig("reports/performance_plot_additional_parties.png")

    # Create a plot for performance with related additional parties
    fig, ax = plt.subplots(figsize=(10, 6))
    for i, (keys, values) in enumerate(scores_related_additional_parties):
        ax.plot(keys, values, label=reports[i].replace(".json", ""))
    ax.set_xlabel("Number of related additional Delegations")
    ax.set_ylabel("Time (s)")
    ax.set_title("Performance of Delegation Models with Related Additional Parties")
    ax.legend()
    plt.savefig("reports/performance_plot_related_additional_parties.png")
