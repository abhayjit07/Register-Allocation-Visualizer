def expireOldIntervals(interval, active, registers):
    for i in active.copy():
        if i[1] <= interval[0]:
            active.remove(i)
            for j, reg in enumerate(registers):
                if reg == i:
                    registers[j] = (-1, -1)

def displayRegisters(registers):
    for i, reg in enumerate(registers):
        print(f"Register {i+1} contains {reg[0]} {reg[1]}")
    print()

def linearScanRegisterAllocation(LiveIntervals, registers):
    active = set()

    for interval in LiveIntervals:
        expireOldIntervals(interval, active, registers)

        if len(active) == R:
            spillAtInterval(interval, active, registers)
        else:
            for i, reg in enumerate(registers):
                if reg == (-1, -1):
                    registers[i] = interval
                    active.add(interval)
                    break

        displayRegisters(registers)

def spillAtInterval(interval, active, registers):
    max_end = interval[1]
    flag = False
    spill_interval = interval

    for i in active:
        if i[1] > max_end:
            max_end = i[1]
            spill_interval = i
            flag = True

    if flag:
        active.remove(spill_interval)
        print(f"Spilled {spill_interval[0]} {spill_interval[1]} to memory")
        index = -1
        for j, reg in enumerate(registers):
            if reg == spill_interval:
                registers[j] = (-1, -1)
                index = j
                break
        active.add(interval)
        registers[index] = interval
    else:
        print(f"Spilled {interval[0]} {interval[1]} to memory")

if __name__ == "__main__":
    LiveIntervals = {(1, 3), (2, 5), (3, 10), (4, 8), (5, 7)}
    R = 2
    registers = [(-1, -1)] * R

    for interval in LiveIntervals:
        print(interval[0], interval[1])

    linearScanRegisterAllocation(LiveIntervals, registers)
