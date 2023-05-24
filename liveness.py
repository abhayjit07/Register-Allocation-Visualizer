import re

with open("IR.txt", "r") as f:
    IR = f.read()
    IR = IR.strip().split("\n")
    # print(IR)

leader = [1]

for i in range(len(IR)):
    IR[i].strip()
    if IR[i].startswith("if") or IR[i].startswith("goto"):
        if (i+2 < len(IR)):
            leader.append(i+2)
        # Get the number between the brackets of goto()
        goto_number = re.search(r'\((.*?)\)', IR[i]).group(1)
        goto_number = int(goto_number)
        leader.append(goto_number)


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

# print(Blocks)


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
        Blocks[i]['flow'].append("exit")

print(Blocks)   