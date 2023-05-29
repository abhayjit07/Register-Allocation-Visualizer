import matplotlib.pyplot as plt

def expireOldIntervals(interval, active, registers):
    for i in active.copy():
        if i[1] <= interval[0]:
            active.remove(i)
            for j, reg in enumerate(registers):
                if reg == i:
                    registers[j] = (-1, -1)

def displayRegisters(registers, dick):
    for i, reg in enumerate(registers):
        variable = next((key for key, value in dick.items() if value == (reg[0], reg[1])), 'NONE')
        print(f"Register {i+1} contains variable {variable} (live interval: {dick[variable][0]}-{dick[variable][1]})")
    print()

def linearScanRegisterAllocation(LiveIntervals, registers, dick):
    active = set()

    for interval in LiveIntervals:
        expireOldIntervals(interval, active, registers)

        if len(active) == R:
            spillAtInterval(interval, active, registers, dick)
        else:
            for i, reg in enumerate(registers):
                if reg == (-1, -1):
                    registers[i] = interval
                    active.add(interval)
                    break

        displayRegisters(registers, dick)

def spillAtInterval(interval, active, registers, dick):
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
        variable = next((key for key, value in dick.items() if value == (spill_interval[0], spill_interval[1])), 'NONE')
        print(f"Spilled variable {variable} to memory")
        index = -1
        for j, reg in enumerate(registers):
            if reg == spill_interval:
                registers[j] = (-1, -1)
                index = j
                break
        active.add(interval)
        registers[index] = interval
    else:
        variable = next((key for key, value in dick.items() if value == (spill_interval[0], spill_interval[1])), 'NONE')
        print(f"Spilled variable {variable} to memory")

if __name__ == "__main__":
    LiveIntervals = {(1, 3), (2, 5), (3, 10), (4, 8), (5, 7)}
    #make a dictionary of intervals mapping them to variables
    dick={'a':(1, 3), 'b':(2, 5), 'c':(3, 10), 'd':(4, 8), 'e':(5, 7),'NONE':(-1,-1)}
    R = 2
    registers = [(-1, -1)] * R

    for interval in LiveIntervals:
        print(interval[0], interval[1])

    linearScanRegisterAllocation(LiveIntervals, registers, dick)
