import re
import networkx as nx
import matplotlib.pyplot as plt
import copy

with open("IR.ir", "r") as f:
    IR = f.read()
    IR = IR.strip().split("\n")
    # print(IR)

leader = [i for i in range(1, len(IR)+1)]

# for i in range(len(IR)):
#     IR[i].strip()
#     if IR[i].startswith("if") or IR[i].startswith("goto"):
#         if (i+2 < len(IR)):
#             leader.append(i+2)
#         # Get the number between the brackets of goto()
#         goto_number = re.search(r'\((.*?)\)', IR[i]).group(1)
#         goto_number = int(goto_number)
#         leader.append(goto_number)


leader = list(set(leader))

# print(leader)

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

# # beautifully print the blocks
# for i in range(len(Blocks)):
#     print("Block " + str(i+1) + ":")
#     print(Blocks[i]['block'])
#     print()


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



# for i in range(len(Blocks)):
#     print("Block " + str(i+1) + ":")
#     print(Blocks[i]['flow'])
#     print()


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
        # elif Blocks[i]['block'][j].startswith("call"):
        #     Use[i].add(re.search(r'\((.*?)\)', Blocks[i]['block'][j]).group(1))
        # elif Blocks[i]['block'][j].startswith("return"):
        #     Use[i].add(re.search(r'\((.*?)\)', Blocks[i]['block'][j]).group(1))
        elif Blocks[i]['block'][j].startswith("print"):
            Use[i].add(re.search(r'\((.*?)\)', Blocks[i]['block'][j]).group(1))
        # elif Blocks[i]['block'][j].startswith("read"):
        #     Use[i].add(re.search(r'\((.*?)\)', Blocks[i]['block'][j]).group(1))
        # elif Blocks[i]['block'][j].startswith("param"):
        #     Use[i].add(re.search(r'\((.*?)\)', Blocks[i]['block'][j]).group(1))
        # elif Blocks[i]['block'][j].startswith("func"):
        #     Use[i].add(re.search(r'\((.*?)\)', Blocks[i]['block'][j]).group(1))
        # elif Blocks[i]['block'][j].startswith("label"):
        #     Use[i].add(re.search(r'\((.*?)\)', Blocks[i]['block'][j]).group(1))
        # elif Blocks[i]['block'][j].startswith("return"):
        #     Use[i].add(re.search(r'\((.*?)\)', Blocks[i]['block'][j]).group(1))
        # elif Blocks[i]['block'][j].startswith("end"):
        #     Use[i].add(re.search(r'\((.*?)\)', Blocks[i]['block'][j]).group(1))
        else:
            if "=" in Blocks[i]['block'][j]:
                tmp_def = Blocks[i]['block'][j].split("=")[0].strip()
                # Def[i].add(Blocks[i]['block'][j].split("=")[0].strip())
                rhs = Blocks[i]['block'][j].split("=")[1].strip().split()
                rhs_copy = []
                # remove all the operators from the rhs
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

                # print(rhs_copy)
                if j == 0 :
                    Use[i] = Use[i] | set(rhs_copy)
                else :
                    Use[i] = Use[i] | (set(rhs_copy) - Def[i])
                Def[i].add(tmp_def)
            else:
                Use[i].add(Blocks[i]['block'][j].strip())

# print("Use: ", Use)
# print("Def: ", Def)            

# IN = USE union (OUT - DEF)
# OUT = union (IN) for successive INs

# # find the number of blocks
no_of_blocks = len(leader)

for i in range(no_of_blocks):
    for j in range(no_of_blocks):
        In[j] = Use[j] | (Out[j] - Def[j])
        for k in (Blocks[j]['flow']):
            if k == 'exit' :
                continue
            else:
                Out[j] = Out[j] | In[k-1]

# print("Use: ", Use)
# print("Def: ", Def)
# print("In: ", In)
# print("Out: ", Out)

Graph = nx.Graph()

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


edges = []
nodes = []

for node in Adj:
    nodes.append(node)
    for neighbour in Adj[node]:
        edges.append((node, neighbour))

Graph.add_nodes_from(nodes)
Graph.add_edges_from(edges)

options = {"edgecolors": "tab:gray", "node_size": 800, "alpha": 0.9}



position = nx.spring_layout(Graph)
nx.draw(Graph, with_labels=True, font_weight='bold', **options, pos=position)

plt.savefig("interference_graph.png")


# TODO: live_intervals = {}



# CHAITIN'S ALGORITHM: 

def correctIR_help(line_of_insert):
    with open("IR.ir", "r") as f:
        lines = f.readlines()
    for line_no in range(line_of_insert, len(lines)):
        if "goto" in lines[line_no]:
            goto_number = re.search(r'\((.*?)\)', Blocks[i]['block'][-1]).group(1)
            if goto_number >= line_of_insert:
                goto_number += 1
                lines[line_no] = lines[line_no].replace(re.search(r'\((.*?)\)', Blocks[i]['block'][-1]).group(1), str(goto_number))

def correctIR():
    with open("IR.ir", "r") as f:
        lines = f.readlines()
    for line_no in range(len(lines)):
        if "load" in lines[line_no] or "store" in lines[line_no]:
            correctIR_help(line_no)


stack = []
Adj_copy = copy.deepcopy(Adj)
number_of_registers = 2

# print("Adj_copy: ", Adj_copy)
# print("nodes: ", nodes)

removed = False

while len(Adj_copy) > 0:
    removed = False
    for node in nodes:
        if node in Adj_copy and len(Adj_copy[node]) < number_of_registers:
            if node in stack:
                continue
            stack.append(node)
            for neighbour in Adj[node]:
                if neighbour in Adj_copy:
                    Adj_copy[neighbour].remove(node)
            Adj_copy.pop(node)
            removed = True
    if not removed and len(Adj_copy) > 0:
        # Spill (optimistic coloring)
        spill_node = list(Adj_copy.keys())[0]
        stack.append(spill_node)
        tmp = Adj[spill_node].copy()
        for neighbour in tmp:
            if neighbour in Adj_copy:
                Adj_copy[neighbour] = Adj_copy[neighbour] - set(spill_node)
        Adj_copy.pop(spill_node)



New_Graph = nx.Graph()

New_Adj = {}
node_colors = {}

colors = [f'r{i}' for i in range(number_of_registers)]

success = True

stack = reversed(stack)

failed_node = 'none'

for node in stack:
    # Check if node can be assigned a color
    for color in colors:
        if color in [node_colors[new_node] for new_node in Adj[node] if new_node in New_Adj]:
            continue
        else:
            node_colors[node] = color
            break
    
    # Check if color was assigned
    if node not in node_colors:
        # Spill
        print("Spilled")
        success = False
        failed_node = node
        break
    
    New_Adj[node] = set()
    
    for new_node in New_Adj:
        if node in Adj[new_node]:
            New_Adj[node].add(new_node)
            New_Adj[new_node].add(node)

# Spill

count = 0
lineskip = 0
if not success:
    #open file with read/write permissions
    f = open("IR.ir", "r+")
    lines = f.readlines()

    flag = False
    for inst in Blocks:
        flag = False

        if failed_node in Use[inst['leader']-1] : 
            print("line number: ", inst['leader'] - 1)
            line_number = inst['leader'] - 1
            load_string = "load &" + failed_node + " " + failed_node + str(count) + "\n"
            lines.insert(line_number - 1, load_string)
            lines[line_number + lineskip] = lines[line_number + lineskip].replace(failed_node, failed_node + str(count))
            lineskip += 1
            flag = True

        if failed_node in Def[inst['leader']-1] : 
            line_number = inst['leader'] - 1
            store_string = "store &" + failed_node + " " + failed_node + str(count) + "\n"
            lines.insert(line_number + lineskip + 1, store_string)
            lines[line_number + lineskip] = lines[line_number + lineskip].replace(failed_node, failed_node + str(count))
            lineskip += 1
            flag = True
        
        if flag:
            count += 1
    
    # update file with lines
    f.seek(0)
    f.writelines(lines)
    f.truncate()
    f.close()



            
            
    










