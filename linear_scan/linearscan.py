import sys
import matplotlib.pyplot as plt
import re
import networkx as nx

Graph = nx.Graph()
initial_nodes = []
fixed_positions = {}
nodes = []
edges = []
position = None
img_count = 1

def extract_liveranges(nodes, In, Out, Blocks):
    live_ranges = {}
    first_update = {}
    for node in nodes:
        live_ranges[node] = [0, 0]
        first_update[node] = False
    for block in Blocks:
        for node in In[block['leader']-1]:
            if block['leader'] > live_ranges[node][1] or first_update[node] == False:
                live_ranges[node][1] = block['leader']
                first_update[node] = True
        for node in Out[block['leader']-1]:
            if block['leader'] < live_ranges[node][0] or first_update[node] == False:
                live_ranges[node][0] = block['leader']
                first_update[node] = True
    return live_ranges

def liveness(irfilename):
    global Graph, nodes, edges, position, img_count, initial_nodes, fixed_positions
    f =  open(irfilename, "r")
    IR = f.read()
    IR = IR.strip().split("\n")
    f.close()

    leader = [i for i in range(1, len(IR)+1)]
    leader = list(set(leader))
    Blocks = []

    for i in range(len(leader)):
        if i+1 < len(leader):
            block = {}
            block['leader'] = leader[i]
            block['block'] = (IR[leader[i]-1:leader[i+1]-1])
            Blocks.append(block)
        else:
            block = {}
            block['leader'] = leader[i]
            block['block'] = (IR[leader[i]-1:])
            Blocks.append(block)

    for i in range(len(Blocks)):
        if i+1 < len(Blocks):
            Blocks[i]['flow'] = []
            Blocks[i]['flow'].append(i+2)
            if Blocks[i]['block'][-1].startswith("goto") or Blocks[i]['block'][-1].startswith("if"):
                goto_number = re.search(r'\((.*?)\)', Blocks[i]['block'][-1]).group(1)
                goto_number = int(goto_number)
                # find the block with the goto_number as the leader
                for j in range(len(Blocks)):
                    if Blocks[j]['leader'] == goto_number:
                        Blocks[i]['flow'].append(j+1)         
        else:
            Blocks[i]['flow'] = []
            if Blocks[i]['block'][-1].startswith("goto") or Blocks[i]['block'][-1].startswith("if"):
                goto_number = re.search(r'\((.*?)\)', Blocks[i]['block'][-1]).group(1)
                goto_number = int(goto_number)
                # find the block with the goto_number as the leader
                for j in range(len(Blocks)):
                    if Blocks[j]['leader'] == goto_number:
                        Blocks[i]['flow'].append(j+1)
            Blocks[i]['flow'].append("exit")


    Use = []
    Def = []
    In = []
    Out = []

    operators = ['+', '-', '*', '/', '%', '==', '!=', '>', '<', '>=', '<=', '!']

    for i in range(len(Blocks)):
        Use.append(set())
        Def.append(set())
        In.append(set())
        Out.append(set())
        for j in range(len(Blocks[i]['block'])):
            if Blocks[i]['block'][j].startswith("if"):
                continue
            elif Blocks[i]['block'][j].startswith("goto"):
                continue
            elif Blocks[i]['block'][j].startswith("print"):
                Use[i].add(re.search(r'\((.*?)\)', Blocks[i]['block'][j]).group(1))
            elif Blocks[i]['block'][j].startswith("load"):
                Def[i].add(re.search(r'\((.*?)\)', Blocks[i]['block'][j]).group(1))
            elif Blocks[i]['block'][j].startswith("store"):
                Use[i].add(re.search(r'\((.*?)\)', Blocks[i]['block'][j]).group(1))
                continue
            else:
                if "=" in Blocks[i]['block'][j]:
                    tmp_def = Blocks[i]['block'][j].split("=")[0].strip()
                    # Def[i].add(Blocks[i]['block'][j].split("=")[0].strip())
                    rhs = Blocks[i]['block'][j].split("=")[1].strip().split()
                    rhs_copy = []
                    size = len(rhs)
                    for k in range(size):
                        if rhs[k] in operators or rhs[k].isnumeric():
                            continue
                        else:
                            try:
                                float(rhs[k])
                                continue
                            except:
                                rhs_copy.append(rhs[k])
                    if j == 0 :
                        Use[i] = Use[i] | set(rhs_copy)
                    else :
                        Use[i] = Use[i] | (set(rhs_copy) - Def[i])
                    Def[i].add(tmp_def)
                else:
                    Use[i].add(Blocks[i]['block'][j].strip())

    no_of_blocks = len(leader)

    for i in range(no_of_blocks):
        for j in range(no_of_blocks):
            In[j] = Use[j] | (Out[j] - Def[j])
            for k in (Blocks[j]['flow']):
                if k == 'exit' :
                    continue
                else:
                    Out[j] = Out[j] | In[k-1]

    
    Adj = {} 

    for block_number in range(no_of_blocks):
        for node in In[block_number]:    
            if node not in Adj:
                Adj[node] = set()
            Adj[node] = Adj[node] | (In[block_number] - set(node))

    # remove self loops
    for node in Adj:
        if node in Adj[node]:
            Adj[node].remove(node)

    for node in Adj:
        if node not in nodes:
            nodes.append(node)
        for neighbour in Adj[node]:
            if (node, neighbour) not in edges and (neighbour, node) not in edges:
                edges.append((node, neighbour))

    if not initial_nodes:
        initial_nodes = nodes.copy()

    Graph = nx.Graph()
    Graph.add_nodes_from(nodes)
    Graph.add_edges_from(edges)
    fixed_nodes = initial_nodes.copy()
    position = nx.circular_layout(Graph)
    fixed_positions = {}
    for node in fixed_nodes:
        fixed_positions[node] = position[node]
    options = {"edgecolors": "tab:gray", "node_size": 1000, "alpha": 1, "pos": position}
    
    # Draw graph with title 
    plt.figure(figsize=(7, 7))
    plt.title("Interference Graph")
    nx.draw(Graph, with_labels=True, **options)
    plt.savefig("interference_graph.png")

    live_ranges = extract_liveranges(nodes, In, Out, Blocks)
    return live_ranges

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

    live_ranges = liveness(sys.argv[1])
    print(live_ranges)

    LiveIntervals = []

    for node in live_ranges:
        #convert live_ranges[node] to a tuple
        range = (live_ranges[node][0], live_ranges[node][1])
        LiveIntervals.append(range)

    #sort live intervals by start time
    LiveIntervals.sort(key=lambda x: x[0])

    #read number of registers from arguments
    R = int(sys.argv[2])

    registers = [(-1, -1)] * R

    for interval in LiveIntervals:
        print(interval[0], interval[1])

    linearScanRegisterAllocation(LiveIntervals, registers, dick)
