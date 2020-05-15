import matplotlib.pyplot as plt
from statistics import mean, median, stdev
import scipy.stats
import numpy as np
import urllib
import io
import base64


def get_score_dist(scores):
    if not scores:
        return
    x_min = min(scores)
    x_max = max(scores)
    avg = mean(scores)
    std = stdev(scores)
    x = np.linspace(x_min, x_max)
    y = scipy.stats.norm.pdf(x, avg, std)

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax2.hist(scores, alpha=0.5, edgecolor='None', color='orange')
    ax1.plot(x, y, color='red', zorder=2)
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
    fig, ax = plt.subplots()
    ax.boxplot(scores, vert=False)
    ax.height = 200
    ax.set_xlabel('Score')
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