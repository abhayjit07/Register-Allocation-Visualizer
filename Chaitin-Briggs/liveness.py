import random
import re
from matplotlib.table import Table
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.plotting import table 
import copy
from PIL import Image, ImageDraw, ImageFont, ImageFilter

Graph = nx.Graph()
initial_nodes = []
fixed_positions = {}
nodes = []
edges = []
position = None
img_count = 1


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
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    ax1.set_title("Chaitin-Briggs Algorithm")
    nx.draw(Graph, with_labels=True, **options, ax=ax1)
    ax2.set_title("Stack")
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.axis('off')

    table_data = [['Stack']]
    cell_colors = [['tab:gray']]
    table = ax2.table(cellText=table_data,cellColours=cell_colors, loc='center', cellLoc='center', colWidths=[0.2])
    
    stack_label_cell = table[0, 0]
    stack_label_cell.set_text_props(weight='bold')
    stack_label_cell.set_height(0.1)
    stack_label_cell.set_fontsize(12)
    stack_label_cell.set_text_props(color='w')
    stack_label_cell._set_text_position((0.5, 0.5))
    plt.savefig("images/" + str(img_count) + '.png')
    plt.close()
    img_count += 1

    return Adj, Def, Use, In, Out, Blocks

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
    global Graph, position, nodes, edges, initial_nodes, fixed_positions
    Adj, Def, Use, In, Out, Blocks = liveness(irfilename)

    Graph = nx.Graph()
    Graph.add_nodes_from(nodes)
    Graph.add_edges_from(edges)
    options = {"edgecolors": "tab:gray", "node_size": 1000, "alpha": 1, "pos": position}
    node_colors_array = ["tab:blue" for _ in range(len(nodes))]
    edge_colors = ["tab:red" for _ in range(len(Graph.edges()))]
    # Draw graph with title
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    ax1.set_title("Interference Graph")
    try:
        nx.draw(Graph, with_labels=True, node_color=node_colors_array, edge_color=edge_colors, **options, ax=ax1)
    except:
        # print the exact cause of the error
        print("Error in graph coloring")
        print("Adjacency list: ", Adj)
        print("Def: ", Def)
        print("Use: ", Use)
        print("In: ", In)
        print("Out: ", Out)
        print("Blocks: ", Blocks)
        print("Nodes: ", nodes)
        print("Graph: ", Graph)
        print("Position: ", position)

    ax2.set_title("Stack")
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.axis('off')

    plt.savefig("interference_graph_fade.png")
    
    # TODO: live_intervals = {}

    # CHAITIN'S ALGORITHM: 

    stack = []
    Adj_copy = copy.deepcopy(Adj)

    global img_count

    removed = False

    while len(Adj_copy) > 0:
        removed = False
        for node in nodes:
            if node in Adj_copy and len(Adj_copy[node]) < number_of_registers:
                if node in stack:
                    continue
                stack.append(node)
                # reduce alpha of the appended node and its edges
                color = 'tab:gray'
                node_colors_array[nodes.index(node)] = color
                for neighbour in Adj[node]:
                    try:
                        edge_colors[list(Graph.edges()).index((node, neighbour))] = color
                    except:
                        edge_colors[list(Graph.edges()).index((neighbour, node))] = color
                for neighbour in Adj[node]:
                    if neighbour in Adj_copy:
                        Adj_copy[neighbour].remove(node)
                Adj_copy.pop(node)

                Graph = nx.Graph()
                Graph.add_nodes_from(nodes)
                Graph.add_edges_from(edges)

                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
                ax1.set_title("Chaitin-Briggs Algorithm")
                ax2.set_title("Stack")
                ax2.set_xticks([])
                ax2.set_yticks([])
                ax2.axis('off')

                options = {"node_size": 1000, "alpha": 1, "pos": position}

                try:
                    nx.draw(Graph, with_labels=True, node_color=node_colors_array, edge_color=edge_colors, **options, ax=ax1)
                except:
                    # print the exact cause of the error
                    print("Error in graph coloring")
                    print("Adjacency list: ", Adj)
                    print("Def: ", Def)
                    print("Use: ", Use)
                    print("In: ", In)
                    print("Out: ", Out)
                    print("Blocks: ", Blocks)
                    print("Nodes: ", nodes)
                    print("Graph: ", Graph)
                    print("Position: ", position)
                

                # plot table in ax2 but upside down, with 'stack' at the bottom
                table_data = [[node] for node in stack]
                table_data.reverse()
                table_data.append(['Stack'])
                cell_colors = [['tab:blue'] for _ in range(len(stack))]
                cell_colors.append(['tab:gray'])
                # Plot table without column and row headers
                table = ax2.table(cellText=table_data, cellColours=cell_colors, loc='center', cellLoc='center', colWidths=[0.2])
                ax2.axis('off')
                table.scale(1, 2)

                stack_label_cell = table[(len(stack), 0)]
                stack_label_cell.set_text_props(weight='bold')
                stack_label_cell.set_height(0.1)
                stack_label_cell.set_fontsize(12)
                stack_label_cell.set_text_props(color='w')
                stack_label_cell._set_text_position((0.5, 0.5))
                                                             
                plt.savefig("images/" + str(img_count) + ".png")
                plt.close()
                print(img_count)
                img_count += 1
                removed = True

        if not removed and len(Adj_copy) > 0:
            spill_node = list(Adj_copy.keys())[0]
            stack.append(spill_node)
            tmp = Adj[spill_node].copy()
            for neighbour in tmp:
                if neighbour in Adj_copy:
                    Adj_copy[neighbour] = Adj_copy[neighbour] - set(spill_node)
            Adj_copy.pop(spill_node)



    New_Adj = {}
    node_colors = {}


    colors = [f'r{i}' for i in range(number_of_registers)]
    # A map that maps each r{i} to an actual color
    color_map = {'r0': 'tab:blue', 'r1': 'tab:orange', 'r2': 'tab:green', 'r3': 'tab:red', 'r4': 'tab:purple', 'r5': 'tab:brown', 'r6': 'tab:pink', 'r7': 'tab:gray', 'r8': 'tab:olive', 'r9': 'tab:cyan'}
    # populate node_colors_array with the numeric rgb values of the color gray
    node_colors_array = ['tab:gray' for _ in range(len(nodes))]
    success = True
    stack = list(reversed(stack))
    failed_node = 'none'

    tmp_stack = stack.copy()
    color_stack = []
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
            Graph = nx.Graph()
            Graph.add_nodes_from(nodes)
            Graph.add_edges_from(edges)
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            ax1.set_title("Chaitin-Briggs Algorithm")
            ax2.set_title("Stack")
            ax2.set_xticks([])
            ax2.set_yticks([])
            ax2.axis('off')

            options = {"node_size": 1000, "alpha": 1, "pos": position}

            nx.draw(Graph, with_labels=True, node_color=node_colors_array, edge_color=edge_colors, **options, ax=ax1)

            # plot table in ax2 but upside down, with 'stack' at the bottom
            table_data = [[node] for node in stack]
            table_data.reverse()
            table_data.append(['Stack'])
            cell_colors = [['tab:blue'] for _ in range(len(stack))]
            cell_colors.append(['tab:gray'])
            # Plot table without column and row headers
            table = ax2.table(cellText=table_data, cellColours=cell_colors, loc='center', cellLoc='center', colWidths=[0.2])
            ax2.axis('off')
            table.scale(1, 2)

            stack_label_cell = table[(len(stack), 0)]
            stack_label_cell.set_text_props(weight='bold')
            stack_label_cell.set_height(0.1)
            stack_label_cell.set_fontsize(12)
            stack_label_cell.set_text_props(color='w')
            stack_label_cell._set_text_position((0.5, 0.5))

            plt.savefig("images/" + str(img_count) + ".png")
            plt.close()
            img_count += 1

            image_to_blur = Image.open("images/" + str(img_count - 1) + ".png")
            
            blurred_image = image_to_blur.filter(ImageFilter.GaussianBlur(radius=5))

            draw = ImageDraw.Draw(blurred_image)

            font = ImageFont.truetype("Lexend-Bold.ttf", 64)
            text = f"Coloring Failed!\nSpilled Node: {failed_node}\n{failed_node} is spilled to the memory"
            text_width, text_height = draw.textbbox((0, 0), text, font=font)[:2]
            x = (blurred_image.width - text_width) // 2
            y = (blurred_image.height - text_height) // 2

            text_color = (0, 0, 0)

            draw.text((x, y), text, font=font, fill=text_color)

            blurred_image.save("images/" + str(img_count - 1) + ".png")


            nodes.remove(node)
            initial_nodes.remove(node)
            tmp_stack.remove(node)
            edge_copy = edges.copy()
            for edge in edges:
                if failed_node in edge:
                    edge_copy.remove(edge)
            edges = edge_copy
            break
        
        New_Adj[node] = set()
        
        for new_node in New_Adj:
            if node in Adj[new_node]:
                New_Adj[node].add(new_node)
                New_Adj[new_node].add(node)
        
        Graph = nx.Graph()
        Graph.add_nodes_from(nodes)
        new_edges = edges.copy()
        for edge in new_edges:
            if failed_node in edge:
                new_edges.remove(edge)
        Graph.add_edges_from(new_edges)
        
        color = node_colors[node]
        node_colors_array[nodes.index(node)] = color_map[color]
        for neighbour in Adj[node]:
            try:
                edge_colors[list(Graph.edges()).index((node, neighbour))] = 'tab:gray'
            except:
                edge_colors[list(Graph.edges()).index((neighbour, node))] = 'tab:gray'
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 6))
        fig.subplots_adjust(wspace=0)
        
        ax1.set_title("Chaitin-Briggs Algorithm")
        ax2.set_title("Stack")
        ax3.set_title("Popped Nodes")

        try:
            nx.draw(Graph, with_labels=True, node_color=node_colors_array, edge_color=edge_colors, **options, ax=ax1)
        except:
            # print the exact cause of the error
            print("Error in graph coloring")
            print("Adjacency list: ", Adj)
            print("Def: ", Def)
            print("Use: ", Use)
            print("In: ", In)
            print("Out: ", Out)
            print("Blocks: ", Blocks)
            print("Nodes: ", nodes)
            print("Graph: ", Graph)
            print("Position: ", position)

        fig.subplots_adjust(left=0, right=1)

        # Get the x and y limits of the graph plot
        x_limits = ax1.get_xlim()
        y_limits = ax1.get_ylim()

        # Increase the plot limits by a margin (adjust as needed)
        x_margin = 0.1
        y_margin = 0.1
        ax1.set_xlim(x_limits[0] - x_margin, x_limits[1] + x_margin)
        ax1.set_ylim(y_limits[0] - y_margin, y_limits[1] + y_margin)

        color_stack.append(tmp_stack.pop(0))


        # plot table in ax2 but upside down, with 'stack' at the bottom
        table_data = [[node] for node in tmp_stack]
        table_data.append(['Stack'])
        cell_colors = [['tab:blue'] for _ in range(len(tmp_stack))]
        cell_colors.append(['tab:gray'])
        # Plot table without column and row headers
        table = ax2.table(cellText=table_data, cellColours=cell_colors, loc='center', cellLoc='center', colWidths=[0.2])
        ax2.axis('off')
        table.scale(1, 2)

        stack_label_cell = table[(len(tmp_stack), 0)]
        stack_label_cell.set_text_props(weight='bold')
        stack_label_cell.set_height(0.1)
        stack_label_cell.set_fontsize(12)
        stack_label_cell.set_text_props(color='w')
        stack_label_cell._set_text_position((0.5, 0.5))

        popped_table_data = [[node] for node in color_stack]
        # Remove borders and spaces between columns
        ax3.axis('off')
        popped_colors = [[color_map[node_colors[node]]] for node in color_stack]
        table3 = ax3.table(cellText=popped_table_data, cellColours=popped_colors, loc='center', cellLoc='center', colWidths=[0.2])
        table3.scale(1, 2)

        plt.savefig("images/" + str(img_count) + ".png")
        plt.close()
        print(img_count)
        img_count += 1

    count = 0
    lineskip = 0
    if not success:
        newir = irfilename
        newir = newir + ".changed"
        f = open(irfilename, "r")
        f_new = open(newir, "w")
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
        
        f_new.seek(0)
        f_new.writelines(lines)
        f_new.truncate()
        f_new.close()

        correctIR(newir, inserts)
        return regalloc(newir, number_of_registers)

    for node in Adj:
        if node not in node_colors:
            node_colors[node] = 'r0'
    
    allocation = {}
    for node in node_colors:
        allocation[node] = node_colors[node]
    
    return allocation, irfilename

def rewriteIR(irfilename, allocation):
    new_irfilename = irfilename
    new_irfilename = new_irfilename + ".regalloc"

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
                    lines[line_no][1] = lines[line_no][1].replace(node, allocation[node])
                    lines[line_no] = " ".join(lines[line_no])
                    continue
                if "goto" in lines[line_no]:
                    lines[line_no] = lines[line_no].split(" ")
                    lines[line_no][1] = lines[line_no][1].replace(node, allocation[node])
                    if len(lines[line_no]) > 2:
                        lines[line_no][3] = lines[line_no][3].replace(node, allocation[node])
                    lines[line_no] = " ".join(lines[line_no])
                    continue
                lines[line_no] = lines[line_no].replace(node, allocation[node])
    f_new.seek(0)
    f_new.writelines(lines)
    f_new.truncate()
    f_new.close()

import sys
import imageio.v2 as imageio
import os

def createGif():
    images_names = []
    images = []
    for image in os.listdir("images"):
        images_names.append(image)

    images_names.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
    for image in images_names:
        images.append(imageio.imread("images/" + image))
        
    imageio.mimsave('Chaitin-Briggs.gif', images, duration=40*len(images))

def main():
    global Graph

    # REmove all images in the images folder
    for image in os.listdir("images"):
        os.remove("images/" + image)
    print(sys.argv)
    if len(sys.argv) < 2:
        print("Please provide the IR file as an argument")
        return
    if len(sys.argv) < 3:
        print("Please provide the number of registers as an argument")
        return
    irfilename = sys.argv[1]
    number_of_registers = int(sys.argv[2])
    allocation, irfilename = regalloc(irfilename, number_of_registers)
    print("Register allocation done")
    print(allocation)
    rewriteIR(irfilename, allocation)
    createGif()
    print("Gif generation done")


if __name__ == "__main__":
    main()
