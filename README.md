# Queue breakdown plotter

Plots logs of what accounts are getting allocations on a cluster over time.

## Generating data

The script expects whitespace-separated files with columns:

- Project/account
- Number of allocated nodes
- Number of jobs in queue
- Time of observation

To generate this on a Slurm cluster,
the following command could be used in a Cron job:

``` bash
squeue -O Account,NumNodes,State | awk 'BEGIN {ts=strftime("%Y-%m-%dT%H:%M:%S");} {totaljobcounts[$1] += 1; if($3=="RUNNING") {nodecounts[$1] += $2}} END {for(project in nodecounts) {print project, nodecounts[project], totaljobcounts[project], ts}}' >> qbreakdown_log
```

(Please think about the load that
repeatedly interrogating `squeue`
may cause on your cluster.
Granularity of one hour is likely sufficient.)

## Installation

``` shellsession
pip install git+https://github.com/edbennett/qbreakdown_plot
```

## Usage

The simplest usage:

``` shellsession
qbreakdown_plot qbreakdown_log
```

By default,
this will display the plot on screen,
and plot the number of allocated nodes.

Options:

- To instead plot the number of queued jobs,
  use `--plot_type jobs_queued`.
- To highlight a specific project,
  use `--highlight_project` followed by the project name.
  This can be repeated to highlight multiple projects.
- To output the plot to a file rather than to the screen,
  use `--plot_filename` followed by the filename to use.
- To customise the plotting format,
  use `--plot_style` followed by a stylesheet.
  This may be the name of one of Matplotlib's builtin stylesheets,
  or the path of any stylesheet.
- To add a dashed horizontal line,
  e.g. for the mean usage required to utilise a project's resources,
  use `--hline` followed by a `project,value` pair.

Full example:

``` shellsession
qbreakdown_plot qbreakdown_log \
    --plot_type jobs_queued \
    --highlight_project p001 \
    --highlight_project p003 \
    --hline p001,50 \
    --hline p003,100 \
    --plot_filename queued.pdf \
    --plot_style ggplot
```
