import matplotlib.pyplot as plt
import numpy

colors = ["b", "r", "g"]

def barplot(filename, data):
    if data == []:
        return ""
    n = len(data)
    cols = len(data[0][1])
    ind = numpy.arange(n)
    fig,ax = plt.subplots()
    ax2 = ax.twinx()
    width = 1.0 / (cols+1)

    for i in range(cols):
        d = list(map(lambda r: r[1][i], data))
        r = ax.bar(ind + i*width, d, width, color=colors[i])

    labels = list(map(lambda r: r[0], data))
    ax.set_ylabel("Count")
    ax2.set_ylabel("Percent")
    ax.xaxis.set_ticks(numpy.arange(0, len(labels), 1) + 0.5)
    ax.set_xticklabels(labels, rotation=25, ha="right")

    plt.subplots_adjust(left=0.125, right=0.9, top=0.9, bottom=0.2)
    plt.savefig("out/" + filename)

    return filename
