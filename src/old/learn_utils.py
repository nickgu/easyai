#! /bin/env python
# encoding=utf-8
# author: nickgu 
# 

import sys
import pydev
import tqdm

class IndexCoder:
    def __init__(self):
        self.tags = []
        self.index = {}

    def get(self, key):
        # get the index of key,
        # if not exists, return None
        return self.index.get(key, None)

    def alloc(self, key):
        # get or alloc and index for a key.
        # if not exists, alloc one.
        if key not in self.index:
            idx = len(self.tags)
            self.index[key] = idx
            self.tags.append(key)
            return idx
        return self.index[key]

    def get_code(self, idx):
        return self.tags[idx]

    def save(self, fd):
        for value in self.tags:
            fd.write('%s\n' % value)

    def load(self, fd):
        self.tags = []
        self.index = {}
        for tag in fd.readlines():
            tag = tag.strip()
            self.index[tag] = len(self.index)
            self.tags.append(tag)

'''
    Usage:
        # pre-scan:
        for ins:
            for feature in ins:
                slot_index_coder.alloc(slot_id, key)
        # trainning.
        for ins:
            for feature in ins:
                input.append(slot_index_coder.get(slot_id, key))
'''
class SlotIndexCoder:
    def __init__(self):
        self.__slot_index = {}

    def slot_dict(self): return self.__slot_index

    def get(self, slot, key):
        if slot not in self.__slot_index:
            return None
        slot_coder = self.__slot_index[slot]
        return slot_coder.get(key)

    def alloc(self, slot, key):
        if slot not in self.__slot_index:
            self.__slot_index[slot] = IndexCoder()
        return self.__slot_index[slot].alloc(key)

    def save(self, fd):
        fd.write('%s\n' % '\t'.join(self.__slot_index.keys()))
        for slot, index_coder in self.__slot_index.iteritems():
            for idx, value in enumerate(index_coder.tags):
                fd.write('%s\t%s\t%d\n' % (slot, value, idx))

    def load(self, fd):
        self.__slot_index = {}
        slot_info = fd.readline().strip().split('\t')
        for slot in slot_info:
            self.__slot_index[slot] = IndexCoder()
        pydev.info('%d slot info loaded' % len(self.__slot_index))
        
        for slot, key, idx in pydev.foreach_row(fd):
            slot_index = self.__slot_index.get(slot, None)
            if slot_index is None:
                raise Exception('Cannot get slot : %s' % slot)

            if int(idx) != len(slot_index.tags):
                raise Exception('Index not match : %s:%s:%s' % (slot, idx, key))

            slot_index.index[key] = len(slot_index.tags)
            slot_index.tags.append(key)

    def __eq__(self, peer):
        if self.__slot_index.keys() != peer.__slot_index.keys():
            return False

        for slot, index in self.__slot_index.iteritems():
            peer_index = peer.__slot_index[slot]
            if peer_index.tags != index.tags:
                return False
            if peer_index.index != index.index:
                return False

        return True

def auc(pred, y, reorder=True):
    import sklearn.metrics as M
    tpr, fpr, threshold = M.roc_curve(y, pred, reorder)
    auc = M.auc(tpr, fpr)
    print >> sys.stderr, pydev.ColorString.yellow(' >>> EASY_AUC_TEST: %.4f (%d items) <<<' % (auc, len(pred)))
    return auc


