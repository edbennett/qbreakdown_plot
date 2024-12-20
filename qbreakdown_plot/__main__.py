#!/usr/bin/env python

"""Plot the time history of qbreakdown data."""

from argparse import ArgumentParser, FileType
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd


def twotuple(arg):
    split_arg = arg.split(",")
    return split_arg[0], float(split_arg[1])


def get_args():
    """
    Define and parse arguments to the code.
    """
    parser = ArgumentParser(
        prog="qbreakdown_plot",
        description="Plot a breakdown of cluster usage over time",
    )
    parser.add_argument(
        "qbreakdown_file",
        type=FileType("r"),
        help="File containing qbreakdown output",
    )
    parser.add_argument(
        "--plot_type",
        choices=["alloc_nodes", "jobs_queued", "waiting_jobs", "waiting_job_nodes"],
        default="alloc_nodes",
        help=(
            "What to plot:"
            "    alloc_nodes: the number of nodes allocated to each project."
            "    jobs_queued: the number of jobs in the queue (including running jobs) "
            "    for each project"
        ),
    )
    parser.add_argument(
        "--highlight_project",
        dest="highlight_projects",
        action="append",
        metavar="project",
        default=[],
        help="Project to highlight on the plot",
    )
    parser.add_argument(
        "--hline",
        dest="hlines",
        action="append",
        metavar="number",
        type=twotuple,
        default=[],
        help="Horizontal line to draw in the form `associated project,limit`",
    )
    parser.add_argument(
        "--plot_filename",
        default=None,
        help="File in which to place the resulting plot. By default, shows on the screen.",
    )
    parser.add_argument(
        "--plot_style",
        default=Path(__file__).parent.absolute() / "styles.mplstyle",
        help="Style sheet to use for plotting",
    )
    return parser.parse_args()


def read_data(f):
    """
    Given a qbreakdown output `f`, read it into a Pandas DataFrame,
    with a row for each date,
    and columns for each project and for each plot type.
    """
    df = pd.read_csv(
        f,
        sep=r"\s+",
        names=[
            "time",
            "project",
            "alloc_nodes",
            "jobs_queued",
            "waiting_jobs",
            "waiting_job_nodes",
        ],
        parse_dates=["time"],
        infer_datetime_format=True,
    )
    # This turns integers into floats, but that shouldn't hurt us on these data
    return df.pivot_table(
        columns=["project"], index=["time"], fill_value=0
    ).reset_index()


def plot(data, plot_type, highlight_projects, hlines):
    """
    Given a dataframe `data`,
    plot the time history of the specified `plot_type`.
    """
    fig, ax = plt.subplots(layout="constrained")
    descriptions = {
        "alloc_nodes": "Number of nodes allocated by project",
        "jobs_queued": "Number of jobs in queue by project",
        "waiting_jobs": "Number of jobs waiting in the queue by project",
        "waiting_job_nodes": (
            "Number of nodes that waiting jobs in the queue could use by project"
        ),
    }
    ax.set_title(descriptions[plot_type])
    lines = {}

    for project in sorted(data.columns.levels[1]):
        if not project:
            continue
        linewidth = (
            3 * plt.rcParams["lines.linewidth"]
            if project in highlight_projects
            else None
        )
        lines[project] = ax.plot(
            data["time"], data[plot_type][project], label=project, lw=linewidth
        )

    for project, limit in hlines:
        if project in lines:
            colour = lines[project][0].get_color()
        else:
            colour = "black"
        ax.axhline(limit, dashes=(3, 3), color=colour)

    ax.set_xlabel("Time")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    ylabels = {
        "alloc_nodes": "Node count",
        "jobs_queued": "Job count",
        "waiting_jobs": "Job count",
        "waiting_job_nodes": "Node count",
    }
    ax.set_ylabel(ylabels[plot_type])
    fig.legend(loc="outside right", title="Project")

    return fig


def save_or_show(fig, filename=None):
    """
    For a given `fig`, save it to `filename` if specified, otherwise show it on screen.
    In either case, flush it from the buffer.
    """
    if filename:
        fig.savefig(filename)
        plt.close(fig)
    else:
        plt.show()


def main():
    """
    Read and plot the data.
    """
    args = get_args()
    plt.style.use(args.plot_style)
    data = read_data(args.qbreakdown_file)
    fig = plot(data, args.plot_type, args.highlight_projects, args.hlines)
    save_or_show(fig, args.plot_filename)


if __name__ == "__main__":
    main()
