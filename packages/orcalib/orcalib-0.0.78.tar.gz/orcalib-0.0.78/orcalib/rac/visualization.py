from collections import defaultdict
from statistics import mean
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator
from plotly.subplots import make_subplots
from prettytable import PrettyTable

from .old_return_types import AnalyzeResult


def visualize_explain(data: AnalyzeResult):
    """Visualizes the model's predictions and memories"""
    label_df = pd.DataFrame(data.label_stats)
    memory_df = pd.DataFrame(data.memory_stats)

    _, axis = plt.subplots(4, 1, figsize=(12, 20))

    # Label distribution pie chart
    sizes = data.label_counts.values()
    labels = [
        f"label: {label['label']}, {'name: ' + label['label_name'] + ',' if label['label_name'] is not None else ''} count: {label['count']}"
        for label in data.label_stats
    ]

    axis[0].set(title="Accessed Memories Label Distribution")
    axis[0].pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
    )

    # scatter plot of mean memory lookup scores per label
    if all(label["label_name"] for label in data.label_stats):
        # if all labels have a name show them
        axis[1].scatter(label_df["mean"], label_df["label_name"], color="green", label="Mean Lookup scores per label")
    else:
        axis[1].scatter(label_df["mean"], label_df["label"], color="green", label="Mean Lookup scores per label")
    axis[1].set(
        title="Mean Fragment Lookup Scores per Label",
        xlabel="Mean Fragment Lookup Score",
        ylabel="Label",
    )

    # scatter plot of Memory score distribution per label
    if all(label["label_name"] for label in data.memory_stats):
        # if all memories have a label_name; show the names
        axis[2].scatter(
            memory_df["lookup_score"], memory_df["label_name"], color="green", label="Lookup scores per label"
        )
    else:
        axis[2].scatter(memory_df["lookup_score"], memory_df["label"], color="green", label="Lookup scores per label")

    axis[2].set(title="Fragment Lookup Score Distribution Per Label", xlabel="Lookup Score", ylabel="Label")

    # Show the mean and variance of scores per label
    x = [label["label"] for label in label_df.to_dict(orient="records")]
    y = [label["mean"] for label in label_df.to_dict(orient="records")]
    yerr = [label["variance"] for label in label_df.to_dict(orient="records")]

    axis[3].errorbar(x, y, yerr, fmt="o", linewidth=2, capsize=6)

    axis[3].set(
        xlim=(0, len(data.label_counts.keys())),
        xticks=np.arange(0, max(data.label_counts.keys())),
        ylim=(0, 1),
        yticks=np.arange(0, 2),
        title="Mean and Variance of Scores per Label",
        xlabel="Label",
        ylabel="Score",
    )

    plt.show()
    return None


def visualize_memory_stats(memory_stats: dict):
    """Visualizes the memory stats"""
    # Initialize lists to store memory IDs and correct/incorrect counts
    memory_ids = []
    correct_counts = []
    incorrect_counts = []
    ratios = []

    # Extract memory IDs and counts from memory stats
    for memory_id, stats in memory_stats.items():
        memory_ids.append(memory_id)
        correct_counts.append(stats.correct)
        incorrect_counts.append(stats.incorrect)
        ratios.append(1 - stats.ratio)

    # Create a plot of correct and incorrect counts
    _, axis = plt.subplots(1, 1, figsize=(12, 5))
    axis.bar(memory_ids, correct_counts, color="blue", label="Correct")
    axis.bar(memory_ids, incorrect_counts, bottom=correct_counts, color="red", label="Incorrect")
    axis.set_xlabel("Memory ID")
    axis.set_ylabel("Count")
    axis.set_title("Lookups per Fragment")
    axis.xaxis.set_major_locator(MaxNLocator(integer=True))  # Ensure x-axis shows only integers
    axis.legend()

    # Create a plot of ratio incorrect
    _, axis2 = plt.subplots(1, 1, figsize=(12, 5))
    axis2.bar(memory_ids, ratios, color="red", label="Incorrect Ratio")
    axis2.set_xlabel("Memory ID")
    axis2.set_ylabel("Ratio")
    axis2.set_title("High-error Fragments")
    axis2.xaxis.set_major_locator(MaxNLocator(integer=True))  # Ensure x-axis shows only integers
    axis2.legend()

    # Create a scatter plot of ratio by label
    label_ratios = defaultdict(list)
    for memory_id, stats in memory_stats.items():
        label = stats.label
        label_ratios[label].append(stats.ratio)

    _, axis3 = plt.subplots(1, 1, figsize=(12, 5))
    for label, ratios in label_ratios.items():
        axis3.scatter([label], mean(ratios), len(ratios), label=f"Label {label}")
    axis3.set_xlabel("Label")
    axis3.set_ylabel("Ratio")
    axis3.xaxis.set_major_locator(MaxNLocator(integer=True))  # Ensure x-axis shows only integers
    axis3.set_title("Accuracy by memory label")


def print_memories_table(data: AnalyzeResult):
    """Prints the memories and labels tables in a pretty format"""
    memory_keys = list(data.memory_stats[0].keys())
    memory_values = [list(item.values()) for item in data.memory_stats]
    label_keys = list(data.label_stats[0].keys())
    label_values = [list(item.values()) for item in data.label_stats]

    memory_table = [memory_keys, *memory_values]
    mem_tab = PrettyTable(memory_table[0])
    mem_tab.add_rows(memory_table[1:])

    labels_table = [label_keys, *label_values]
    lab_tab = PrettyTable(labels_table[0])
    lab_tab.add_rows(labels_table[1:])

    return f"Memories Table,\n{mem_tab}\nLabels Table\n{lab_tab}"


def plot_model_performance_comparison(results, labels, metrics, config):
    # Create figure for the bar chart
    fig = go.Figure()

    colors = ["#72d972", "#2ca02c", "#6fa2df", "#0a69da"]
    colorCounter = 0
    # Add bars for each scenario
    for label_key, label_name in labels.items():
        fig.add_trace(
            go.Bar(
                x=metrics,
                y=[results[label_key][metric] for metric in metrics],
                marker=dict(color=colors[colorCounter]),
                name=label_name,
            )
        )
        colorCounter += 1

    # Update layout
    fig.update_layout(
        title=config["title"],
        xaxis_title=config["xaxis"],
        yaxis_title=config["yaxis"],
        barmode="group",
        template="plotly",
    )

    # Show the figure
    fig.show()


class FinetunePlot:
    def __init__(self, show_running_mean: bool = False):
        self.fig = make_subplots(specs=[[{"secondary_y": False}]])

        # Add traces
        self.fig.add_trace(
            go.Scatter(
                name="Loss",
                mode="markers",
                marker={
                    "size": 5,
                    "color": "rgba(0,0,255,0.5)",
                },
            ),
        )
        self.fig.add_trace(
            go.Scatter(
                mode="lines",
                name="Mean Loss" if show_running_mean else "Trailing Mean Loss",
                line=dict(
                    color="blue",
                    width=2,
                ),
            ),
        )
        self.fig.add_trace(
            go.Scatter(
                mode="lines",
                name="Validation Loss",
                line=dict(
                    color="green",
                    width=2,
                ),
            ),
        )

        # Update layout
        self.fig.update_layout(
            height=600,
            xaxis=dict(title="Epoch"),
            yaxis=dict(title="Loss"),
            title="Training Loss per Epoch",
            legend=dict(x=0.01, y=0.99),
        )

        self.fig_widget = go.FigureWidget(self.fig)

    def update(
        self,
        fractional_epochs: list[float],
        loss_values: list[float],
        mean_loss_values: list[float],
        validation_scores: list[float],
        batch_count: int,
        num_batches: int,
        epoch: int,
        total_epochs: int,
    ):
        # Add vertical line to indicate the start of a new epoch
        if (batch_count + 1) % num_batches == 0 and batch_count != 0:
            self.fig_widget.add_vline(
                x=int((batch_count + 1) / num_batches),
                line_color="rgba(0,0,0,0.25)",
            )

        with self.fig_widget.batch_update():
            d: Any = self.fig_widget.data
            d[0].x = fractional_epochs
            d[0].y = loss_values
            d[1].x = fractional_epochs
            d[1].y = mean_loss_values
            d[2].x = list(range(0, len(validation_scores)))
            d[2].y = validation_scores
            self.fig_widget.update_layout(xaxis=dict(title=f"Epoch: {epoch + 1}/{total_epochs}"))

    def get_widget(self):
        return self.fig_widget
