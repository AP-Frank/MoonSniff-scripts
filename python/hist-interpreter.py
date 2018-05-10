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


def ask_yes_no(question):
    while True:
        print(question + " [y/n] ")
        choice = input().lower()
        if choice in ['true', '1', 't', 'y', 'yes']:
            return True
        elif choice in ['false', '0', 'f', 'n', 'no']:
            return False
        else:
            print("Please write yes or no.")


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


def compute_ccdf(compressed_hist, index):
    x = compressed_hist[index][0].copy()
    y = compressed_hist[index][1].copy()

    # convert to [us]
    x = np.divide(x, 1000)

    # normalize to 1
    y = np.divide(y, sum(y))
    print(y)

    cummulative_y = np.cumsum(y)

    inverse = np.repeat(1, len(y))
    inverse = np.subtract(inverse, cummulative_y)

    return x, y, inverse


def plot_ccdf(compressed_hist, points, bucket_size):
    for i in range(0, len(compressed_hist)):
        x, y, inverse = compute_ccdf(compressed_hist, i)
        plt.semilogy(x, inverse)

    plt.title("Latency of MoonGen forwarder (" + str(bucket_size) + " ns buckets)")
    plt.xlabel("Latency [us]")
    plt.ylabel("Normalized prevalence")
    plt.legend([str(int(point)) + " Mbit/s" for point in points])
    axes = plt.gca()
    axes.set_xlim([0, 0.5])

    plt.tight_layout()
    save_figure(plt, 'ccdf-' + str(bucket_size) + 'b')
    # plt.show()

    plt.close()


def plot_cdf_df(compressed_hist, points, bucket_size):
    print(compressed_hist)
    print(compressed_hist[0])

    x = compressed_hist[0][0]
    y = compressed_hist[0][1]

    # convert to [us]
    x = np.divide(x, 1000)

    # normalize to 1
    y = np.divide(y, sum(y))
    print(y)

    cummulative_y = np.cumsum(y)

    plt.plot(x, y)
    plt.plot(x, cummulative_y, 'r--')
    axes = plt.gca()
    axes.set_xlim([3, 9])
    # axes.set_ylim([0, 1])

    plt.title("Latency of MoonGen forwarder (" + str(bucket_size) + " ns buckets, " + str(int(points[0])) + " Mbit/s)")
    plt.xlabel("Latency [us]")
    plt.ylabel("Normalized prevalence")
    plt.legend(['df', 'cdf'])

    print('saving figure')
    plt.tight_layout()
    save_figure(plt, 'compare-' + str(bucket_size) + 'b-cdf')

    print('finished saving figure, now plotting')
    # plt.show()

    plt.close()


def plot_ccdf_df(compressed_hist, points, bucket_size):
    x, y, inverse = compute_ccdf(compressed_hist, 0)

    plt.semilogy(x, y)
    plt.semilogy(x, inverse, 'r--')
    axes = plt.gca()
    axes.set_xlim([3, 9])
    # axes.set_ylim([0, 1])

    plt.title("Latency of MoonGen forwarder (" + str(bucket_size) + " ns buckets, " + str(int(points[0])) + " Mbit/s)")
    plt.xlabel("Latency [us]")
    plt.ylabel("Normalized prevalence")
    plt.legend(['df', 'ccdf'])

    print('saving figure')
    plt.tight_layout()
    save_figure(plt, 'compare-' + str(bucket_size) + 'b-ccdf')

    print('finished saving figure, now plotting')
    # plt.show()

    plt.close()


def box_graph(histograms, xpoints, bucket_size):
    print("now plotting .. ")
    xpoints = [int(value) for value in xpoints]
    ticks = np.arange(1, len(xpoints) + 1, 1)
    # plt.figure(num=None, figsize=(14, 6), dpi=80, facecolor='w', edgecolor='k')

    # data set is pretty big, so fliers just cluster up the plot
    # instead draw only the min and max
    plt.boxplot(histograms, showmeans=False, widths=0.7, whis=[5, 95], showfliers=False)

    plt.title("Latency of MoonGen forwarder (" + str(bucket_size) + " ns buckets)")
    plt.xlabel("Average line-rate [Mbit/s]")
    plt.ylabel("Latency [ns]")
    plt.xticks(ticks, xpoints, rotation='vertical')

    # compute mins and maxes
    maxes = [hist[len(hist) - 1] for hist in histograms]
    mins = [hist[0] for hist in histograms]

    plt.plot(ticks, maxes, color='black', marker='o', linestyle='None', fillstyle='none')
    plt.plot(ticks, mins, color='black', marker='o', linestyle='None', fillstyle='none')

    # plt.legend(handles=[violin_parts['cmeans'], violin_parts['cmedians']])
    # ax = plt.gca()
    # ax.set_xticks(ticks)
    # ax.set_xticklabels(xpoints)
    plt.tight_layout()
    save_figure(plt, 'box-' + str(bucket_size) + 'b')
    # plt.show()

    plt.close()


def violin_graph(histograms, xpoints, bucket_size):
    print("now plotting .. ")
    xpoints = [int(value) for value in xpoints]
    ticks = np.arange(1, len(xpoints) + 1, 1)
    # plt.figure(num=None, figsize=(14, 6), dpi=80, facecolor='w', edgecolor='k')
    violin_parts = plt.violinplot(histograms, showmeans=True, showextrema=True, showmedians=True, widths=0.7)
    plt.setp(violin_parts['bodies'], facecolor='red', edgecolor='black')
    plt.setp(violin_parts['cmedians'], color='black', linestyle='dotted', label='median')
    plt.setp(violin_parts['cmeans'], color='blue', label='mean')
    plt.setp(violin_parts['cmaxes'], color='black')
    plt.setp(violin_parts['cmins'], color='black')
    plt.setp(violin_parts['cbars'], color='black')

    plt.title("Latency of MoonGen forwarder (" + str(bucket_size) + " ns buckets)")
    plt.xlabel("Average line-rate [Mbit/s]")
    plt.ylabel("Latency [ns]")
    plt.xticks(ticks, xpoints, rotation='vertical')

    plt.legend(handles=[violin_parts['cmeans'], violin_parts['cmedians']])
    # ax = plt.gca()
    # ax.set_xticks(ticks)
    # ax.set_xticklabels(xpoints)
    plt.tight_layout()
    save_figure(plt, 'violin-' + str(bucket_size) + 'b')
    # plt.show()

    plt.close()


def read_samples():
    skip_rates = False
    stepsize = int(args.stepsize)
    begin = int(args.begin)
    end = int(args.end) + stepsize

    hists = list()
    points = list()

    # list is not expanded as hists
    compressed_hist = list()

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

        compressed_hist.append((value_lst, amount_lst))
        # new stuff
        hist = np.repeat(value_lst, amount_lst)

        nth = max(1, int(sum(amount_lst) / 1000000))
        print("nth " + str(nth))

        print("size before: " + str(hist.size))

        # downsampling: we do not want to loose the maximum or the minimum,
        # so they are added manually
        reduced = np.insert(hist[nth:len(hist) - 1:nth].copy(), 0, hist[0])
        reduced = np.append(reduced, hist[len(hist) - 1])
        print(reduced)

        hist = reduced
        # hist = hist[nth:len(hist) - 1:nth].copy()

        print(hist)

        print("size after: " + str(hist.size))

        # print(hist)
        hists.append(hist)
        # print(hists)

        if not skip_rates:
            ratefile = "measurement-rate-" + str(rate) + "-stats.csv"

            try:
                with open(ratefile) as file:
                    # as the NIC first has to initialize, usually full
                    # receiving capacity is only reached after a few seconds
                    next(file)
                    next(file)

                    Mbit_framing = list()
                    for line in file:
                        vals = line.split(",")
                        Mbit_framing.append(float(vals[5]))

                    # the last values can also be influenced by the teardown
                    del Mbit_framing[-1]
                    del Mbit_framing[-1]
                    points.append(np.average(Mbit_framing))

            except FileNotFoundError as e:
                print("File " + ratefile + " not found. Actual line-rate cannot be displayed.")
                if ask_yes_no("Fall back to base-rate?"):
                    skip_rates = True
                    points = range(begin, end, stepsize)
                else:
                    exit(0)

    return hists, points, compressed_hist


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
hists, points, compressed_hist = read_samples()

# plot_graph()
# violin_graph(hists, points, 1)
box_graph(hists, points, 1)
# plot_cdf_df(compressed_hist, points, 1)
# plot_ccdf_df(compressed_hist, points, 50)
# plot_ccdf(compressed_hist, points, 1)

stop = timeit.default_timer()

print()
print('Estimated time [min]')
print((stop - start) / 60)
