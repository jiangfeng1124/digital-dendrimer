from anytree import Node, RenderTree
from copy import deepcopy
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def read_data(path):
    nodes = []
    for l in open(path):
        layer = l.strip().split()
        nodes.append(layer)
    nodes.reverse()
    return nodes

def build_tree(nodes):
    depth = len(nodes)
    assert (len(nodes[0]) == 1)
    tree = []
    leaves = []
    for i in range(depth):
        if i == 0:
            root = Node(nodes[0][0])
            tree.append([root])
        else:
            n_pre = len(nodes[i-1])
            n_cur = len(nodes[i])
            assert (n_cur == n_pre or n_cur == 2 * n_pre)
            layer = []
            if n_cur == n_pre:
                for j in range(n_cur):
                    layer.append(Node(nodes[i][j], parent=tree[i-1][j]))
                    if i == depth - 1:
                        leaves.append((i, j))
                tree.append(layer)
            elif n_cur == 2 * n_pre:
                for j in range(n_cur):
                    layer.append(Node(nodes[i][j], parent=tree[i-1][j/2]))
                    if i == depth - 1:
                        leaves.append((i, j))
                tree.append(layer)
            else:
                raise ValueError("Incorrect number of nodes in layer: %d" % (i))

    return tree, leaves

def update_tree(tree, i, j):
    dup_tree = deepcopy(tree)
    layer = dup_tree[i]
    node = layer[j]
    node.parent = None
    # layer.remove(node)
    # if len(layer) == 0:
    #     dup_tree.remove(layer)
    return dup_tree

# def traverse(tree, path):
#     for i, layer in enumerate(tree):
#         for j, node in enumerate(layer):
#             if node.is_leaf:
#                 if node.is_root:
#                     paths.add(path + node.name)
#                 else:
#                     traverse(update_tree(tree, i, j), path + node.name)

def traverse(tree, leaves, path):
    # for i, layer in enumerate(tree):
    #     for j, node in enumerate(layer):
    for i, j in leaves:
        node = tree[i][j]
        if node.is_leaf:
            if node.is_root:
                # print("add: {}".format(path + node.name))
                paths.add(path + node.name)
                # fw.write("{}\n".format(path + node.name))
                if len(paths) % 100 == 0:
                    print(len(paths))
                    sys.stdout.flush()
                if len(paths) % 800 == 0:
                    for path in paths:
                        # fw.write("{}\n".format(path + node.name))
                        fw.write("{}\n".format(path))
                    fw.flush()
                    sys.exit(-1)
            else:
                mod_leaves = deepcopy(leaves)
                if len(node.parent.children) == 1:
                    if len(tree[i]) == len(tree[i-1]):
                        mod_leaves.append((i-1, j))
                    else:
                        mod_leaves.append((i-1, j/2))
                mod_leaves.remove((i,j))
                traverse(update_tree(tree, i, j), mod_leaves, path + node.name)

def display_tree(root):
    for pre, fill, node in RenderTree(root):
        print("%s%s" % (pre, node.name))

if len(sys.argv) != 4:
    print >> sys.stderr, "Usage: python generate.py [input_file] [output_file] [image_file]"
    sys.exit(-1)

nodes = read_data(sys.argv[1])
tree, leaves = build_tree(nodes)
paths = set()

fw = open(sys.argv[2], "w")
traverse(tree, leaves, "")

print("Input tree:")
display_tree(tree[0][0]) # tree[0][0] is the root node

paths = sorted(list(paths), reverse=True)
paths = [ path[::-1] for path in paths ]

print("\nPossible paths written to {}\n".format(sys.argv[2]))
with open(sys.argv[2], "w") as fw:
    for path in paths:
        fw.write("{}\n".format(path))
fw.close()

def save_image(data, filename):
    sizes = np.shape(data)
    fig = plt.figure()
    # fig.set_size_inches(1. * sizes[0] / sizes[1], 1, forward = False)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)
    img = ax.imshow(data, interpolation='nearest')
    img.set_cmap('gray')
    plt.savefig(filename, cmap='hot')
    plt.close()

matrix = np.asarray([map(int, list(e)) for e in paths])
matrix = 1 - matrix # 0->1, 1->0
# save_image(matrix, sys.argv[3])
plt.imshow(matrix, cmap='gray', interpolation='none')
# plt.axis('off')
plt.savefig(sys.argv[3], bbox_inches='tight')

