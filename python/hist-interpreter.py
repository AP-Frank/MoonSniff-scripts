import argparse
import numpy as np
import matplotlib.pyplot as plt
import collections

parser = argparse.ArgumentParser()
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

bins = list()

for rate in range(1000, 10000, 1000):
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

        sum += number * amount
        samples += amount

        histo[number] = amount

    average = (sum / samples)

    print(average)
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

rate = np.arange(1000, 10000, 1000)

if args.tex:
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')

plt.plot(rate, bins, rate, np.full((9,), 5))

plt.xlabel('Average data-rate in [Mbit/s]')
plt.ylabel('Average latency in [ns]')
plt.title('Latency measurement for 1m optical fiber cable')
plt.legend(['measured', 'expected'])
plt.grid(True)
plt.savefig('figure')
plt.show()
