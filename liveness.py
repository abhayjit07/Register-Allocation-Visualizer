import re
import networkx as nx
import matplotlib.pyplot as plt
import copy

def liveness(irfilename):
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
    # nx.draw(Graph, with_labels=True, font_weight='bold', **options, pos=position)

    plt.savefig("interference_graph.png")

    return Graph, Adj, Def, Use, In, Out, Blocks, nodes

def correctIR_help(line_of_insert, lines):
    for line_no in range(len(lines)):
        if "goto" in lines[line_no]:
            goto_number = re.search(r'\((.*?)\)', lines[line_no]).group(1)
            goto_number = int(goto_number)
            if goto_number > line_of_insert + 1:
                goto_number += 1
                lines[line_no] = lines[line_no].replace(re.search(r'\((.*?)\)', lines[line_no]).group(1), str(goto_number))

def correctIR(irfilename, inserts):
    f = open(irfilename, "r+")
    lines = f.readlines()
    for line_no in inserts:
        correctIR_help(line_no, lines)
    f.seek(0)
    f.writelines(lines)
    f.truncate()
    f.close()

def regalloc(irfilename, number_of_registers):
    Graph, Adj, Def, Use, In, Out, Blocks, nodes = liveness(irfilename)

    # TODO: live_intervals = {}

    # CHAITIN'S ALGORITHM: 

    stack = []
    Adj_copy = copy.deepcopy(Adj)

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
        for color in colors:
            if color in [node_colors[new_node] for new_node in Adj[node] if new_node in New_Adj]:
                continue
            else:
                node_colors[node] = color
                break
        
        if node not in node_colors:
            print("Spilled")
            success = False
            failed_node = node
            break
        
        New_Adj[node] = set()
        
        for new_node in New_Adj:
            if node in Adj[new_node]:
                New_Adj[node].add(new_node)
                New_Adj[new_node].add(node)

    count = 0
    lineskip = 0
    if not success:
        f = open(irfilename, "r+")
        lines = f.readlines()

        inserts = []

        flag = False
        for inst in Blocks:
            flag = False

            if failed_node in Use[inst['leader']-1] : 
                line_number = inst['leader'] - 1
                load_string = "load &" + failed_node + " (" + failed_node + str(count) + ")\n"
                lines.insert(line_number + lineskip, load_string)
                inserts.append(line_number + lineskip)
                lines[line_number + lineskip + 1] = lines[line_number + lineskip + 1].replace(failed_node, failed_node + str(count))
                lineskip += 1
                flag = True

            if failed_node in Def[inst['leader']-1] : 
                line_number = inst['leader'] - 1
                store_string = "store &" + failed_node + " (" + failed_node + str(count) + ")\n"
                lines.insert(line_number + lineskip + 1, store_string)
                inserts.append(line_number + lineskip + 1)
                lines[line_number + lineskip] = lines[line_number + lineskip].replace(failed_node, failed_node + str(count))
                lineskip += 1
                flag = True
            
            if flag:
                count += 1
        
        f.seek(0)
        f.writelines(lines)
        f.truncate()
        f.close()

        correctIR(irfilename, inserts)
        return regalloc(irfilename, number_of_registers)

    for node in Adj:
        if node not in node_colors:
            node_colors[node] = 'r0'
    
    allocation = {}
    for node in node_colors:
        allocation[node] = node_colors[node]
    
    return allocation

def rewriteIR(irfilename, allocation):
    new_irfilename = irfilename.split(".")[0] + "_regalloc.ir"
    f_new = open(new_irfilename, "w")
    f = open(irfilename, "r")
    lines = f.readlines()
    allocation = dict(sorted(allocation.items(), key=lambda item: len(item[0]), reverse = True))
    for line_no in range(len(lines)):
        for node in allocation:
            if node in lines[line_no]:
                if "load" in lines[line_no] or "store" in lines[line_no]:
                    lines[line_no] = lines[line_no].split(" ")
                    lines[line_no][2] = lines[line_no][2].replace(node, allocation[node])
                    lines[line_no] = " ".join(lines[line_no])
                    continue
                if "print" in lines[line_no]:
                    lines[line_no] = lines[line_no].split(" ")
                    lines[line_no][1] = "(" + allocation[node] + ")\n"
                    lines[line_no] = " ".join(lines[line_no])
                    continue
                lines[line_no] = lines[line_no].replace(node, allocation[node])
    f_new.seek(0)
    f_new.writelines(lines)
    f_new.truncate()
    f_new.close()

import sys

def main():
    print(sys.argv)
    if len(sys.argv) < 2:
        print("Please provide the IR file as an argument")
        return
    irfilename = sys.argv[1]
    allocation = regalloc(irfilename, 3)
    print("Register allocation done")
    print(allocation)
    rewriteIR(irfilename, allocation)


if __name__ == "__main__":
    main()
