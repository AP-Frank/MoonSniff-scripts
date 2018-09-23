import argparse
import os
import timeit

import numpy as np
import matplotlib.pyplot as plt

start = timeit.default_timer()

parser = argparse.ArgumentParser()
parser.add_argument('-b', '--begin', help="Start value", required=True)
parser.add_argument('-e', '--end', help="End value", required=True)
parser.add_argument('-s', '--stepsize', help="The size ot the steps", required=True)
parser.add_argument('-n', '--name', help="The common part of all file names (without <rate>.csv", required=True)
parser.add_argument('-i', '--image_title', help="Title displayed on all created images", default="Measurement")
parser.add_argument('-c', '--bucket_size', help="Bucket/Container size of the histogram", required=True)
parser.add_argument('-t', '--tex', help="Use TeX for typesetting", action='store_true')
parser.add_argument('-x', '--image_extension', help="Select the image type. Default is png", default="png")
args = parser.parse_args()

#########################################
# additional values which can be modified

# format strings for ccdf_df and cdf_df
FORMAT_PRIMARY = 'b-'  # format for df
FORMAT_SECONDARY = 'r--'  # format for cdf/ccdf


# colors taken from:
# https://stackoverflow.com/a/287944
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def ask_yes_no(question):
    """
    Ask the user a yes or no question via commandline

    :param question: The question to be displayed
    :return: True if the user answered with yes, False otherwise
    """
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
    """
    If --tex flag is set, use TeX fonts for texts
    """
    if args.tex:
        plt.rc('text', usetex=True)
        plt.rc('font', family='serif')


def save_figure(plt, filename):
    """
    Saves the given figure in a subfolder called image under the given name

    Old files are never overwritten, if the name is not unique, a number will be incremented

    :param plt: The plot to save
    :param filename: The name of the file
    """
    directory = 'images'
    if not os.path.exists(directory):
        os.makedirs(directory)

    ctr = 0

    # check if a picture with this name exists
    # to never overwrite old images
    while os.path.exists(directory + '/{}{:d}.{}'.format(filename, ctr, args.image_extension)):
        ctr += 1

    print('Saving to ' + directory + '/{}{:d}.{}'.format(filename, ctr, args.image_extension))
    plt.savefig(directory + '/{}{:d}.{}'.format(filename, ctr, args.image_extension), dpi=200)
    print('Done saving')


def compute_ccdf(compressed_hist, index):
    """
    Computes the CCDF directly form MoonSniffs histogram representation

    :param compressed_hist: Array of  MoonSniff histograms (compressed)
    :param index: Index within the compressed_hist
    :return:
        x: values (latencies) in [us]<br>
        y: values (amount of data-points) normalized to 1<br>
        inverse: 1-y element-wise
    """
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


def plot_ccdf(compressed_hist, points, bucket_size, xlim, name):
    """
    Plots the cumulative distribution function for all histograms

    :param compressed_hist: Array of MoonSniff histograms (compressed)
    :param points: Values for the x axis
    :param bucket_size: Size of the buckets
    :param xlim: If used limits the shown area (x-axis) to this array, e.g. [0, 1] will only show
    the graph between 0 and 1
    :param name: The name of the image
    """

    for i in range(0, len(compressed_hist)):
        x, y, inverse = compute_ccdf(compressed_hist, i)
        plt.semilogy(x, inverse)

    axes = plt.gca()
    percent_line = axes.axhline(0.01, linestyle='dashed', color='grey', linewidth=0.8)

    plt.title(name + " (" + str(bucket_size) + " ns buckets)")
    plt.xlabel("Latency [us]")
    plt.ylabel("Normalized prevalence")
    plt.legend([str(point) + " Mbit/s" for point in points] + ['99th percentile'])

    if len(xlim) == 2:
        axes = plt.gca()
        axes.set_xlim(xlim)
        # axes.set_ylim([0, 1])

    plt.tight_layout()
    save_figure(plt, 'ccdf-' + str(bucket_size) + 'b')
    # plt.show()

    plt.close()


def plot_cdf_df(compressed_hist, points, bucket_size, xlim, name):
    """
    Plots the cumulative distribution function and the plain distribution function of a single histogram

    :param compressed_hist: Array of MoonSniff histograms (compressed)
    :param points: Values for the x axis
    :param bucket_size: Size of the buckets
    :param xlim: If used limits the shown area (x-axis) to this array, e.g. [0, 1] will only show
    the graph between 0 and 1
    :param name: The name of the image
    """

    print(compressed_hist)
    print(compressed_hist[0])

    x = compressed_hist[0][0].copy()
    y = compressed_hist[0][1].copy()

    # convert to [us]
    x = np.divide(x, 1000)

    # normalize to 1
    y = np.divide(y, sum(y))
    print(y)

    cummulative_y = np.cumsum(y)

    plt.plot(x, y, FORMAT_PRIMARY)
    plt.plot(x, cummulative_y, FORMAT_SECONDARY)

    if len(xlim) == 2:
        axes = plt.gca()
        axes.set_xlim(xlim)
        # axes.set_ylim([0, 1])

    plt.title(name + " (" + str(bucket_size) + " ns buckets, " + str(points[0]) + " Mbit/s)")
    plt.xlabel("Latency [us]")
    plt.ylabel("Normalized prevalence")
    plt.legend(['df', 'cdf'])

    print('saving figure')
    plt.tight_layout()
    save_figure(plt, 'compare-' + str(bucket_size) + 'b-cdf')

    print('finished saving figure, now plotting')
    # plt.show()

    plt.close()


def plot_ccdf_df(compressed_hist, points, bucket_size, xlim, name):
    """
    Plots the complementary cumulative distribution function and the plain distribution function

    :param compressed_hist: Array of MoonSniff histograms (compressed)
    :param points: Values for the x axis
    :param bucket_size: Size of the buckets
    :param xlim: If used limits the shown area (x-axis) to this array, e.g. [0, 1] will only show
    :param name: The name of the image
    """

    x, y, inverse = compute_ccdf(compressed_hist, 0)

    plt.semilogy(x, y, FORMAT_PRIMARY)
    plt.semilogy(x, inverse, FORMAT_SECONDARY)

    if len(xlim) == 2:
        axes = plt.gca()
        axes.set_xlim(xlim)
        # axes.set_ylim([0, 1])

    plt.title(name + " (" + str(bucket_size) + " ns buckets, " + str(points[0]) + " Mbit/s)")
    plt.xlabel("Latency [us]")
    plt.ylabel("Normalized prevalence")
    plt.legend(['df', 'ccdf'])

    print('saving figure')
    plt.tight_layout()
    save_figure(plt, 'compare-' + str(bucket_size) + 'b-ccdf')

    print('finished saving figure, now plotting')
    # plt.show()

    plt.close()


def box_graph(histograms, xpoints, bucket_size, name):
    """
    Plot a box graph representing all histograms

    :param histograms: The input histograms (expanded)
    :param xpoints: Values for the x axis
    :param bucket_size: Size of the buckets
    :param name: The name of the image
    """

    print("now plotting .. ")
    ticks = np.arange(1, len(xpoints) + 1, 1)
    # plt.figure(num=None, figsize=(14, 6), dpi=80, facecolor='w', edgecolor='k')

    # data set is pretty big, so fliers just cluster up the plot
    # instead draw only the min and max
    box_parts = plt.boxplot(histograms, showmeans=False, widths=0.7, whis=[5, 95], showfliers=False)
    plt.setp(box_parts['boxes'], label='boxes')
    plt.setp(box_parts['medians'], label='median')
    plt.setp(box_parts['fliers'], label='max/min')

    plt.title(name + " (" + str(bucket_size) + " ns buckets)")
    plt.xlabel("Average line-rate [Mbit/s]")
    plt.ylabel("Latency [ns]")
    plt.xticks(ticks, xpoints, rotation='vertical')

    # compute mins and maxes
    maxes = [hist[len(hist) - 1] for hist in histograms]
    mins = [hist[0] for hist in histograms]

    max_line = plt.plot(ticks, maxes, color='black', marker='o', linestyle='None', fillstyle='none', label='max/min')
    plt.plot(ticks, mins, color='black', marker='o', linestyle='None', fillstyle='none')

    plt.legend(handles=[box_parts['medians'][0], max_line[0]])
    # ax = plt.gca()
    # ax.set_xticks(ticks)
    # ax.set_xticklabels(xpoints)
    plt.tight_layout()
    save_figure(plt, 'box-' + str(bucket_size) + 'b')
    # plt.show()

    plt.close()


def violin_graph(histograms, xpoints, bucket_size, name):
    """
    Plot a box graph representing all histograms

    :param histograms: The input histograms (expanded)
    :param xpoints: Values for the x axis
    :param bucket_size: Size of the buckets
    :param name: The name of the image
    """

    print("now plotting .. ")
    ticks = np.arange(1, len(xpoints) + 1, 1)
    # plt.figure(num=None, figsize=(14, 6), dpi=80, facecolor='w', edgecolor='k')
    violin_parts = plt.violinplot(histograms, showmeans=True, showextrema=True, showmedians=True, widths=0.7)
    plt.setp(violin_parts['bodies'], facecolor='red', edgecolor='black')
    plt.setp(violin_parts['cmedians'], color='black', linestyle='dotted', label='median')
    plt.setp(violin_parts['cmeans'], color='blue', label='mean')
    plt.setp(violin_parts['cmaxes'], color='black')
    plt.setp(violin_parts['cmins'], color='black')
    plt.setp(violin_parts['cbars'], color='black')

    plt.title(name + " (" + str(bucket_size) + " ns buckets)")
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
    """
    Reads the MoonSniff output and wraps it in python lists for later processing

    :return:
        hists: Uncompressed histogram, e.g. 10, 1; 14, 3 -> [10, 14, 14, 14]<br>
        points: X-axis values (average line-rate associated to each histogram)<br>
        compressed_hist: Compressed histogram, [[list of values], [list of amounts]]
    """
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

        # complete histogram without downsampling
        compressed_hist.append((value_lst, amount_lst))

        # TODO: instead of building a full sized list and reducing it later, build reduced one right away
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

                    # first row is the header
                    next(file)

                    # now retrieve devices
                    dev1 = int(next(file).split(",")[1].split("=")[1])
                    dev2 = dev1

                    while dev1 == dev2:
                        dev2 = int(next(file).split(",")[1].split("=")[1])

                    Mbit_framing_1 = list()
                    Mbit_framing_2 = list()

                    for line in file:
                        vals = line.split(",")
                        device = int(vals[1].split("=")[1])

                        if device == dev1:
                            Mbit_framing_1.append(float(vals[5]))
                        elif device == dev2:
                            Mbit_framing_2.append(float(vals[5]))
                        else:
                            print('ERR: The stats file lists more than 2 devices')
                            exit(-1)

                    # the last values can also be influenced by the teardown
                    del Mbit_framing_1[-1]
                    del Mbit_framing_2[-1]

                    avg_1 = np.average(Mbit_framing_1)
                    avg_2 = np.average(Mbit_framing_2)
                    difference = np.abs(avg_2 - avg_1)
                    if difference > 100:
                        print(bcolors.WARNING + 'WARN: Difference between incoming and outgoing transmit-rates of the '
                                                'test device is high: {}'.format(difference) + bcolors.ENDC)
                        print(bcolors.WARNING + 'The y-axis may be of. Printing both values.' + bcolors.ENDC)

                        points.append("{}; {}".format(int(avg_1), int(avg_2)))
                    else:
                        # select the rate to display
                        if avg_1 > avg_2:
                            points.append(int(avg_1))
                        else:
                            points.append(int(avg_2))

            except FileNotFoundError as e:
                print(bcolors.WARNING + "WARN: File " + ratefile + " not found. Actual line-rate cannot be displayed."
                      + bcolors.ENDC)
                if ask_yes_no("Fall back to base-rate?"):
                    skip_rates = True
                    points = range(begin, end, stepsize)
                else:
                    exit(0)

    return hists, points, compressed_hist


configure_plt_font()
hists, points, compressed_hist = read_samples()

bucket_size = int(args.bucket_size)

###################################
# Uncomment/comment below to      #
# create images                   #
#                                 #
# Plotting more than one at a time#
# should also work                #
###################################

violin_graph(hists, points, bucket_size, args.image_title)
box_graph(hists, points, bucket_size, args.image_title)
plot_cdf_df(compressed_hist, points, bucket_size, [], args.image_title)
plot_ccdf_df(compressed_hist, points, bucket_size, [], args.image_title)
plot_ccdf(compressed_hist, points, bucket_size, [], args.image_title)

stop = timeit.default_timer()

print()
print('Estimated time [min]')
print((stop - start) / 60)
