import random as ran
import time
import os


def main():
    terminal = os.get_terminal_size()
    lenn = terminal.columns//2
    increase_times = 1
    numbers = [-1 for _ in range(lenn)]
    while (1):
        for _ in range(increase_times):
            rand_idx = ran.randint(0, lenn-1)
            numbers[rand_idx] = 0
        for i in range(len(numbers)):
            if numbers[i] != -1:
                numbers[i] += 1
            if numbers[i] == 9:
                numbers[i] = -1
        for j in range(len(numbers)):
            if (numbers[j] != -1):
                print(f"\033[32m{numbers[j]}\033[0m", end=" ")
            else:
                print(end="  ")
        print()
        time.sleep(0.025)       
if __name__ == "__main__":
    main()
