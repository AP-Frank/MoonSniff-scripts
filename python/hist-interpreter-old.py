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


def save_figure(plt, filename):
    directory = 'images'
    if not os.path.exists(directory):
        os.makedirs(directory)

    ctr = 0

    while os.path.exists(directory + '/{}{:d}.png'.format(filename, ctr)):
        ctr += 1

    plt.savefig(directory + '/{}{:d}.png'.format(filename, ctr), dpi=200)
    print('Done saving')


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
    save_figure(plt, 'figure')
    plt.show()


bins = list()

hists = list()

stepsize = int(args.stepsize)
begin = int(args.begin)
end = int(args.end) + stepsize

for rate in range(begin, end, stepsize):
    value_lst = list()
    amount_lst = list()

    print(rate)
    averages = list()

    file = open("rate-" + str(rate) + "-run-" + str(1) + ".csv")

    # make sure the order within the dict is not changed
    histo = collections.OrderedDict()

    samples = 0
    sum = 0

    for line in file:
        vals = line.split(",")
        number = int(vals[0])
        amount = int(vals[1])
        value_lst.append(number)
        amount_lst.append(amount)

        sum += number * amount
        samples += amount

        histo[number] = amount

    average = (sum / samples)

    # print(average)
    bins.append(average)
    print(histo)

    # compute standard deviation
    stdDevSum = 0
    for k, v in histo.items():
        stdDevSum = stdDevSum + v * ((k - average) ** 2)

    info_avg.append(average)
    info_stdDev.append((stdDevSum / (samples - 1)) ** 0.5)
    info_min.append(next(iter(histo)))
    info_max.append(next(iter(reversed(histo))))

    # the .5 percentile is the median
    info_median.append(get_percentile(50))

    # new stuff
    hist = np.repeat(value_lst, amount_lst)
    print(hist)
    hists.append(hist)
    print(hists)

rate = np.arange(begin, end, stepsize)

print(bins)
print(rate)

configure_plt_font()

plot_graph()


stop = timeit.default_timer()

print()
print('Estimated time [min]')
print((stop - start) / 60)
