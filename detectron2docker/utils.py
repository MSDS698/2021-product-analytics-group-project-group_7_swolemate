import numpy as np
import os


def split_num(s):
    head = s.rstrip('0123456789')
    tail = s[len(head):]
    return head, tail


def files_in_order(folderpath):
    '''
    Args:
        Folder with compressed npy save files of good and bad exercises

    Returns:
        npy_files (numpy.array): ordered array of good then bad exercises
    '''
    npy_files = os.listdir(folderpath)
    no_extensions = [os.path.splitext(npy_file)[0] for npy_file in npy_files]
    splitted = [split_num(s) for s in no_extensions]
    splitted = np.array(splitted)
    indices = np.lexsort((splitted[:, 1].astype(int), splitted[:, 0]))
    npy_files = np.array(npy_files)
    return npy_files[indices]

