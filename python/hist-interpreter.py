import numpy as np
import matplotlib.pyplot as plt

bins = list()

for rate in range(1000, 10000, 1000):
    print(rate)
    averages = list()

    for experiment in range(1, 5, 1):
        file = open("rate-" + str(rate) + "-run-" + str(experiment) + ".csv")

        samples = 0
        sum = 0

        for line in file:
            vals = line.split(",")
            number = int(vals[0])
            amount = int(vals[1])

            sum += number * amount
            samples += amount

        averages.append(sum / samples)

    average = np.mean(averages)
    print(averages)
    print(average)
    bins.append(average)

rate = np.arange(1000, 10000, 1000)

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
