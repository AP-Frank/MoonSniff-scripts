import argparse
import os
import timeit

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import collections


start = timeit.default_timer()

parser = argparse.ArgumentParser()
parser.add_argument('-b', '--begin', help="Start value")
parser.add_argument('-e', '--end', help="End value")
parser.add_argument('-s', '--stepsize', help="The size ot the steps")
parser.add_argument('-n', '--name', help="The common part of all file names (without <rate>.csv")
parser.add_argument('-t', '--tex', help="Use TeX for typesetting", action='store_true')
args = parser.parse_args()

########################
# computed information #
########################
info_avg = list()
info_stdDev = list()
info_max = list()
info_min = list()
info_percentile = list()
info_median = list()


########################


def get_percentile(percentile):
    # compute percentiles
    if percentile > 100 or percentile < 0:
        print('cannot compute percentiles')
        exit(-1)

    targetSamples = samples * percentile / 100
    sumsamples = 0

    for k, v in histo.items():
        sumsamples = sumsamples + v
        if sumsamples > targetSamples:
            return k


def configure_plt_font():
    if args.tex:
        plt.rc('text', usetex=True)
        plt.rc('font', family='serif')


def plot_graph():
    baseline_val = 5
    baseline = np.full((len(bins),), baseline_val)

    plt.plot(rate, bins, rate, baseline)

    plt.xlabel('Average data-rate in [Mbit/s]')
    plt.ylabel('Average latency in [ns]')
    ax = plt.gca()
    # ax.xaxis.set_major_locator(plt.MaxNLocator(2))
    ax.xaxis.set_major_locator(plt.MultipleLocator(stepsize))
    plt.title('Latency measurement for 1m optical fiber cable')
    plt.legend(['measured', 'expected'])
    plt.grid(True)
    plt.savefig('figure')
    plt.show()


def violin_graph(histograms, xpoints):
    print("now plotting .. ")
    xpoints = [int(value) for value in xpoints]
    ticks = np.arange(1, len(xpoints) + 1, 1)
    violin_parts = plt.violinplot(histograms, showmeans=True, showextrema=True, showmedians=True, widths=0.7)
    plt.setp(violin_parts['bodies'], facecolor='red', edgecolor='black')
    plt.setp(violin_parts['cmedians'], color='black')
    plt.setp(violin_parts['cmeans'], color='blue')
    plt.setp(violin_parts['cmaxes'], color='black')
    plt.setp(violin_parts['cmins'], color='black')
    plt.setp(violin_parts['cbars'], color='black')
    plt.title("Latency measurement for 20m fiber cable")
    plt.xlabel("Average line-rate in mbit/s")
    plt.ylabel("Latency in ns")
    plt.xticks(ticks, xpoints, rotation='vertical')
    #ax = plt.gca()
    #ax.set_xticks(ticks)
    #ax.set_xticklabels(xpoints)
    plt.savefig('figure.svg')
    plt.show()


def read_samples():
    stepsize = int(args.stepsize)
    begin = int(args.begin)
    end = int(args.end) + stepsize

    hists = list()
    points = list()

    for rate in range(begin, end, stepsize):
        value_lst = list()
        amount_lst = list()

        print(rate)

        file = open(args.name + "-" + str(rate) + ".csv")

        for line in file:
            vals = line.split(",")
            number = int(vals[0])
            amount = int(vals[1])
            value_lst.append(number)
            amount_lst.append(amount)

        # new stuff
        hist = np.repeat(value_lst, amount_lst)

        nth = int(sum(amount_lst) / 1000000)
        print("nth " + str(nth))

        print("size before: " + str(hist.size))
        hist = hist[::nth].copy()

        print("size after: " + str(hist.size))

        # print(hist)
        hists.append(hist)
        # print(hists)

        with open("measurement-rate-" + str(rate) + "-stats.csv") as file:
            next(file)

            mbit_framing = list()
            for line in file:
                vals = line.split(",")
                mbit_framing.append(float(vals[5]))

            points.append(np.average(mbit_framing))

    return hists, points


# bins = list()
#
# hists = list()
#
# stepsize = int(args.stepsize)
# begin = int(args.begin)
# end = int(args.end) + stepsize
#
# for rate in range(begin, end, stepsize):
#     value_lst = list()
#     amount_lst = list()
#
#     print(rate)
#     averages = list()
#
#     file = open("rate-" + str(rate) + "-run-" + str(1) + ".csv")
#
#     # make sure the order within the dict is not changed
#     histo = collections.OrderedDict()
#
#     samples = 0
#     sum = 0
#
#     for line in file:
#         vals = line.split(",")
#         number = int(vals[0])
#         amount = int(vals[1])
#         value_lst.append(number)
#         amount_lst.append(amount)
#
#         sum += number * amount
#         samples += amount
#
#         histo[number] = amount
#
#     average = (sum / samples)
#
#     # print(average)
#     bins.append(average)
#     print(histo)
#
#     # compute standard deviation
#     stdDevSum = 0
#     for k, v in histo.items():
#         stdDevSum = stdDevSum + v * ((k - average) ** 2)
#
#     info_avg.append(average)
#     info_stdDev.append((stdDevSum / (samples - 1)) ** 0.5)
#     info_min.append(next(iter(histo)))
#     info_max.append(next(iter(reversed(histo))))
#
#     # the .5 percentile is the median
#     info_median.append(get_percentile(50))
#
#     # new stuff
#     hist = np.repeat(value_lst, amount_lst)
#     print(hist)
#     hists.append(hist)
#     print(hists)
#
# rate = np.arange(begin, end, stepsize)

# print(bins)
# print(rate)

configure_plt_font()
hists, points = read_samples()

# plot_graph()
violin_graph(hists, points)

stop = timeit.default_timer()

print((stop - start)/60)