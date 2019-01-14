from io import open
from os import path
from multiprocessing import cpu_count
import random
from concurrent.futures import ProcessPoolExecutor
from collections import Counter
from deepwalk import DeepWalk_graph as graph


def count_sizes(file):

    c = Counter()
    with open(file, 'r') as f:
        for l in f:
            size = l.split()
            c.update(size)

    return c

def count_textfiles(files, workers=1)

    c = Counter()
    with ProcessPoolExecutor(max_workers=workers) as executor:
        for c_ in executor.map(count_sizes, files):
            c.update(c_)

    return c

def count_lines(f):
    if path.isfile(f):
        num_lines = sum(1 for line in open(f))
        return num_lines
    else:
        return 0

class WalksCorpus(object):

    def __init__(self, file_list):
        self.file_list = file_list

    def __iter__(self):
        for file in self.file_list:
            with open(file, 'r') as f:
                for line in f:
                    yield  line.split()

def _write_walks_to_disk(args):
    num_walks, walk_length, alpha, rand, f = args
    G = __current_graph

    with open(f, 'w') as fout:
    for walk in graph.build_deepwalk_corpus_iter(G=G, num_walks=num_walks, walk_length=walk_length,
                                                 alpha=alpha, rand=rand):
        fout.write(u"{}\n".format(u" ".join(v for v in walk)))

    return f

def write_walks_to_disk(G, filebase, num_walks, walk_length, alpha=0, rand=random.Random, num_workers=cpu_count(),
                        always_rebuild=True):

    global __current_graph
    __current_graph = G

    files_list = ["{}.{}".format(filebase, str(x)) for x in list(range(num_walks))]
    expected_size = len(G)
    args_list = []
    files = []

    if num_walks <= num_workers:
        walks_per_worker = [1 for x in range(num_walks)]
    else:
        walks_per_worker = [len(list(filter(lambda z: z!= None, [y for y in x])))
                            for x in graph.grouper(int(num_walks / num_workers)+1, range(1, num_walks+1))]

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        for size, file_, ppw in zip(executor.map(count_lines, files_list), files_list, walks_per_worker):
            if always_rebuild or size != (ppw*expected_size):
                args_list.append((ppw, walk_length, alpha, random.Random(rand.randint(0, 2**31)), file_))
            else:
                files.append(file_)

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        for file_ in executor.map(_write_walks_to_disk, args_list):
            files.append(file_)

    return files

def combine_files_iter(file_list):

    for file in file_list:
        with open(file, 'r') as f:
            for line in f:
                yield line.split()