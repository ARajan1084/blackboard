import matplotlib.pyplot as plt
from statistics import mean, median, stdev
import scipy.stats
import numpy as np
import urllib
import io
import base64
import random


COLORS = ['darkred', 'orange', 'green', 'lightskyblue', 'lightslategrey']


def get_general_stats(scores, points):
    if not scores:
        return
    scores = [float(score) for score in scores]
    stats = {
        'mean': mean(scores),
        'mean_perc': (mean(scores)*100.0)/points,
        'median': median(scores),
        'stdev': stdev(scores),
        'min': min(scores),
        'max': max(scores)
    }
    return stats


def get_score_dist(scores):
    if not scores:
        return
    color = random.choice(COLORS)
    x_min = float(min(scores))
    x_max = float(max(scores))
    avg = float(mean(scores))
    std = float(stdev(scores))
    x = np.linspace(x_min, x_max)
    y = scipy.stats.norm.pdf(x, avg, std)

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax2.hist(scores, alpha=0.5, edgecolor='None', color=color)
    ax1.plot(x, y, color=color, zorder=2)
    ax1.grid()
    ax1.set_xlabel('Score')
    ax1.set_ylabel('Density')
    ax2.set_ylabel('Frequency')
    ax1.set_xlim(x_min, x_max)
    fig.tight_layout()
    return plt_to_uri(fig)


def get_score_hist(scores):
    if not scores:
        return
    fig, ax = plt.subplots()
    ax.hist(scores)
    ax.set_xlabel('Score')
    ax.set_ylabel('Frequency')
    ax.autoscale()
    fig.tight_layout()
    return plt_to_uri(fig)


def get_score_box(scores):
    if not scores:
        return
    scores = [float(score) for score in scores]
    fig, ax = plt.subplots()
    ax.boxplot(scores, vert=False, widths=0.6)
    ax.height = 200
    ax.set_xlabel('Score')
    ax.get_yaxis().set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.set_size_inches(6, 2, forward=True)
    ax.autoscale()
    fig.tight_layout()
    return plt_to_uri(fig)


def plt_to_uri(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    return uri
