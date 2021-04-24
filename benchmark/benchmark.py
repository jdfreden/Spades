import time

from Game import *
import csv


def run_Normal(state, itermax, reps):
    times = []
    for i in range(reps):
        st = time.time()
        ISMCTS(state, itermax, verbose=0)
        times.append(time.time() - st)

    return times


def run_Para(state, itermax, reps):
    times = []
    for i in range(reps):
        st = time.time()
        ParaISMCTS_driver(state, itermax, verbose=0, numWorkers=5)
        times.append(time.time() - st)

    return times


def main():
    N = 100
    # iterations = [5, 10, 50, 100, 500, 1000, 5000, 10000]
    iterations = [1100, 1300, 1700, 1900, 2100, 2200, 2300, 2400]

    normal = []
    para = []
    for it in iterations:
        print(it)
        random.seed(123)
        ss = SpadesGameState(Player.north)
        ts = run_Normal(ss, it, N)
        ts.append(it)
        normal.append(ts)

    for it in iterations:
        print(it)
        random.seed(123)
        ss = SpadesGameState(Player.north)
        ts = run_Para(ss, it, N)
        ts.append(it)
        para.append(ts)

    with open('benchmark/normal.csv', mode='w', newline='') as of:
        writer = csv.writer(of, delimiter = ',')
        for l in normal:
            writer.writerow(l)

    with open('benchmark/para.csv', mode='w', newline='') as of:
        writer = csv.writer(of, delimiter=',')
        for l in para:
            writer.writerow(l)


if __name__ == "__main__":
    main()
