import re
import networkx as nx
import matplotlib.pyplot as plt

with open("IR.txt", "r") as f:
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

for i in range(len(Blocks)):
    print("Block " + str(i+1) + ":")
    print(Blocks[i]['flow'])
    print()


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
        # elif Blocks[i]['block'][j].startswith("goto"):
        #     Use[i].add(re.search(r'\((.*?)\)', Blocks[i]['block'][j]).group(1))
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

print("Use: ", Use)
print("Def: ", Def)            

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

print("Use: ", Use)
print("Def: ", Def)
print("In: ", In)
print("Out: ", Out)

Graph = nx.Graph()

Adj = {} 

for block_number in range(no_of_blocks):
    for node in In[block_number]:    
        if node not in Adj:
            Adj[node] = set()
        Adj[node] = Adj[node] | (In[block_number] - set(node))

print("Adj: ", Adj)


edges = []
nodes = []

for node in Adj:
    nodes.append(node)
    for neighbour in Adj[node]:
        edges.append((node, neighbour))

Graph.add_nodes_from(nodes)
Graph.add_edges_from(edges)

options = {"edgecolors": "tab:gray", "node_size": 800, "alpha": 0.9}

nx.draw_networkx(Graph, with_labels=True, **options)

plt.show()