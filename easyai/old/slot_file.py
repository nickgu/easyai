#! /bin/env python
# encoding=utf-8
# author: nickgu 
# 

import pydev

class SlotFileWriter:
    def __init__(self, filename):
        self.__fd = file(filename, 'w')
        self.__cur_slot_cnt = 0

        self.__ins_cnt = 0
        self.__slot_cnt = 0
        self.__fea_cnt = 0

    def begin_instance(self, label=0):
        self.__cur_slot_cnt = 0
        self.__fd.write('%s\t'%label)

    def write_slot(self, slot_id, slot_fea_id_list):
        if self.__cur_slot_cnt != 0:
            self.__fd.write('\t')

        self.__fd.write('%s:%s' % (slot_id, ','.join(map(lambda x:str(x), slot_fea_id_list))))

        self.__cur_slot_cnt += 1
        self.__slot_cnt += 1
        self.__fea_cnt += len(slot_fea_id_list)

    def end_instance(self):
        self.__fd.write('\n')
        self.__ins_cnt += 1

    def summary(self):
        pydev.info('Summary: ins=%d, slot=%d, fea=%d' % (self.__ins_cnt, self.__slot_cnt, self.__fea_cnt))


class SlotFileReader:
    def __init__(self, filename):
        self.__fd = file(filename)
        self.__epoch = 0

    def epoch(self): return self.__epoch

    def read_one(self):
        # endless reading
        line = self.__fd.readline()
        if line == '':
            # ending of file.
            self.__epoch += 1
            self.reopen()
            line = self.__fd.readline()

        arr = line.strip().split('\t')
        label = int(arr[0])
        slots = []
        for item in arr[1:]:
            key, id_list = self.__parse_slot(item)
            slots.append( (key, id_list) )

        return label, slots

    def next(self, n):
        labels = []
        slots = []
        for i in range(n):
            label, slot = self.read_one()
            labels.append(label)
            slots.append(slot)
        return labels, slots

    def reopen(self):
        self.__fd.seek(0)

    def __parse_slot(self, item):
        key, ids = item.split(':')
        # TODO: Temp default process. WRONG! but for nan.
        if ids == '':
            return key, [0]
        id_list = map(lambda x:int(x), ids.split(','))
        return key, id_list

class Unittest(pydev.App):
    def __init__(self):
        pydev.App.__init__(self)

    def test_SlotFileWriter(self):
        writer = SlotFileWriter('test.ins')
        for i in range(1000):
            writer.begin_instance( i % 2 )
            for j in range(10):
                slot_id = 'slot%s' % j
                writer.write_slot(slot_id, list(range(j)))
            writer.end_instance()
        writer.summary()
        pydev.info('passed')


if __name__=='__main__':
    ut = Unittest()
    ut.run()
