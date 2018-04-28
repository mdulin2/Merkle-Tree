"""
Understanding the merkle trees is very vital. So, here's a good explanation on how they work.
https://hackernoon.com/merkle-trees-181cb4bc30b4
"""

import random as rand
import datetime
import hashlib


class Block:

    """
    Representation of a transaction of a node
    """
    def __init__(self,ID,value = 0, header =""):
        self.ID = ID #the incremental ID of the transaction
        self.date_created = datetime.datetime.now() #the physical time
        self.value = value #the value the node holds
        self.header = header #more information about the node
        self.random_bytes = self.random_vals(5)
        self.previous = None # need to work on this piece...

    """
    Creates a lot of random bytes
    Args:
        amount(int): the amount of random numbers to return
    Returns:
        value(string): a large amount of random values
    """
    def random_vals(self,amount):
        value = ""
        for i in range(amount):
            value += str(rand.randint(1,1000000))

        return value

    def get_ID(self):
        return self.ID

    def get_value(self):
        return self.value

    def get_header(self):
        return self.header

    def set_header(self,header):
        self.header = header

    def set_value(self, value):
        self.value = value

    """
    Calculates the sha512 hash of the Transaction
    Returns:
        hexdigest(string): returns the hexidecimal representation of the node
    """
    def get_hash(self):
        #str(self.date_created)
        val = str(self.ID)  +str(self.value) + str(self.header)
        m = hashlib.sha512(val)
        return m.hexdigest()

class Tree:

    def __init__(self):
        self.history = list()
        self.root = ""
        self.amount = 0
        self.tree_child = dict()
        self.tree_parent = dict()

    """
    Returns the amount of pairs in the bottom row.
    """
    def make_pairs_init(self):
        return (len(self.history))//2, (len(self.history))%2

    """
    Gets the hash of two hashes
    Args:
        val1(string): the hash of block 1
        val2(string): the hash of block 2
    Returns:
        hash(string): the hash of val1+val2
    """
    def get_hash(self, val1, val2):
        #str(self.date_created)
        val = str(val1) + str(val2)
        m = hashlib.sha512(val)
        return m.hexdigest()

    """
    Returns the amount of layers that should be in the tree.
    This is essentially the discrete log problem that's being solved.
    """
    def get_layer_count(self):
        count = len(self.history)
        iteration = 0
        if(count == 0):
            return 1
        while(True):
            if((2 ** iteration) <= count and (2** (iteration +1)) >= count):
                return iteration + 1
            iteration+=1

    """
    Adds a transaction to the history.
    Args:
        value(int): the integer value that the tree is holding
    """
    def add_transaction(self,value):
        block = Block(self.amount,value = value)
        self.amount +=1
        self.history.append(block)
        self.root = self.create_tree()

    """
    Returns the top hash of the merkle tree. Which is known as the merkle root.
    """
    def get_root(self):
        return self.root

    """
    Recreates the Merkle Tree
    Returns:
        hash(string): The Merkle root
    """
    def create_tree(self):
        self.tree_child = dict()
        self.tree_parent = dict()
        layers = self.get_layer_count()
        init_pair,remainder = self.make_pairs_init()
        new_line = self.init_layer(self.history,init_pair,remainder)
        for i in range(layers):
            if(i % 2 == 1):
                new_line = self.one_layer_left(new_line,len(new_line)//2,len(new_line) %2)
            else:
                new_line = self.one_layer_right(new_line,len(new_line)//2,len(new_line) %2)
        return new_line

    """
    Creates the initial layer of the hashed merkle layer.
    This edits the child and parent dictionaries.
    Args:
        keys(list of Blocks): the full history of the chain
        init_pair(int): amount of pairs being used
        remainder(int): if the amount in the history is even or odd.
    Returns:
        new_line(list): A list of hashes created by the layer.
    """
    def init_layer(self, keys, init_pair,remainder):
        new_line = list()
        #does a single layter of hashing
        for pair in range(0,init_pair*2,2):
            # creating the hash of the blocks
            node1 = keys[pair].get_hash()
            node2 = keys[pair+1].get_hash()
            hashed = self.get_hash(node1,node2)

            #keeps track of what the layer looks like
            new_line.append(hashed)

            #updates the tree
            self.tree_child[hashed] = [node1,node2]
            self.tree_parent[node1] = hashed
            self.tree_parent[node2] = hashed

        if(remainder == 1):
            new_line.append(keys[-1].get_hash())
        return new_line

    """
    Creates a layer of the Merkle tree, starting on the leftside.
    This edits the child and parent dictionaries.
    Args:
        keys(list of strings): The hashes associated with the layer
        init_pair(int): amount of pairs being used
        remainder(int): if the amount in the history is even or odd.
    Returns:
        new_line(list): A list of hashes created by the layer.
    """
    def one_layer_left(self, keys, init_pair,remainder):
        new_line = list()
        #does a single layer of hashing
        for pair in range(0,init_pair*2,2):
            node1 = keys[pair]
            node2 = keys[pair+1]
            hashed = self.get_hash(node1,node2)

            #keeps track of the keys going up the tree
            new_line.append(hashed)

            #updates the tree
            self.tree_child[hashed] = [node1,node2]
            self.tree_parent[node1] = hashed
            self.tree_parent[node2] = hashed

        # at the root hash
        if(len(keys) == 1):
            return keys[0]

        # leftover from the pairs
        if(remainder == 1):
            new_line.append(keys[-1])

        return new_line
    """
    Creates a layer of the Merkle tree, starting on the rightside
    This edits the child and parent dictionaries.
    Args:
        keys(list of strings): The hashes associated with the layer
        init_pair(int): amount of pairs being used
        remainder(int): if the amount in the history is even or odd.
    Returns:
        new_line(list): A list of hashes created by the layer.
    """
    def one_layer_right(self, keys, init_pair,remainder):
        new_line = list()
        maximum = len(keys) - 1
        #does a single layter of hashing
        for pair in range(0,init_pair*2,2):
            node1 = keys[maximum -pair ]
            node2 = keys[maximum -(pair +1)]
            hashed = self.get_hash(node1,node2)
            #keeps track of the keys going up the tree
            new_line.append(hashed)
            self.tree_child[hashed] = [node1,node2]
            self.tree_parent[node1] = hashed
            self.tree_parent[node2] = hashed

        if(len(keys) == 1):
            return keys[0]

        if(remainder == 1):
            new_line.append(keys[0])

        return new_line
"""
creates a tree, then adds 10 blocks to it.
"""
T = Tree()
for i in range(10):
    T.add_transaction("")
    print T.get_root()