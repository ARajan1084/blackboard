import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import scipy.stats
import numpy as np
import urllib
import io
import base64

months = mdates.MonthLocator()  # every month
day_fmt = mdates.DateFormatter('%D')


def get_grade_trend(grade_history):
    data = []
    for entry in grade_history:
        data.append((entry.date_updated, entry.grade))
    data.sort(key=lambda item: item[0])
    x = [item[0] for item in data]
    y = [item[1] for item in data]

    fig, ax = plt.subplots()
    ax.plot(x, y, marker='o')
    ax.autoscale()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(day_fmt)
    fig.tight_layout()

    return plt_to_uri(fig)


def plt_to_uri(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    return uri
