#! /bin/env python
# encoding=utf-8
# author: nickgu 
# 

import sys
import pydev

import torch
import torch.nn as nn
import tqdm
import traceback


def dump_embeddings(emb, fd):
    for emb in emb.weight:
        print >> fd, ','.join(map(lambda x:str(x), emb.tolist()))

def common_train(forward_and_backward_fn, optimizer, iteration_count, while_condition=None, loss_curve_output=None):
    try:
        acc_loss = 0.69

        def inner_proc(iter_num, acc_loss):
            optimizer.zero_grad()
            cur_loss = forward_and_backward_fn()
            optimizer.step()

            acc_loss = acc_loss * 0.99 + 0.01 * cur_loss
            if loss_curve_output:
                print >> loss_curve_output, '%d,%.3f,%.3f' % (iter_num, acc_loss, cur_loss)
            return cur_loss, acc_loss

        if while_condition:
            iter_num = 0
            while while_condition():
                acc_loss, cur_loss = inner_proc(iter_num, acc_loss)
                iter_num += 1
                sys.stderr.write('%cIter=%d acc_loss=%.3f cur_loss=%.3f lr:%.6f' % (13, 
                        iter_num, acc_loss, cur_loss, optimizer.param_groups[0]['lr']
                    ))
        else:
            process_bar = tqdm.tqdm(range(int(iteration_count)))
            for iter_num in process_bar:
                cur_loss, acc_loss = inner_proc(iter_num, acc_loss)
                process_bar.set_description("AccLoss:%0.3f, CurLoss:%.3f, lr: %0.6f" %
                                    (acc_loss, cur_loss, optimizer.param_groups[0]['lr']))


    except Exception, e:
        exstr = traceback.format_exc()
        pydev.err(exstr)
        pydev.err('Training Exception(may be interrupted by control.)')


def common_test(model, x, y):
    # easy test for multiclass output.
    # the net may design like this:
    #
    #   x_ = ...
    #   x_ = ...
    #   y_ = self.fc(x_)
    #   loss = torch.nn.CrossEntropy(y_, y)
    #
    #   max(1) : max dim at dim-1
    #   [1] : get dim.
    y_ = model.forward(x).max(1)[1]
    #   check the precision
    hit = y.eq(y_).sum()
    total = len(y)
    print >> sys.stderr, pydev.ColorString.red(' >>> EASY_TEST_RESULT: %.2f%% (%d/%d) <<<' % (hit*100./total, hit, total))

if __name__=='__main__':
    # test code.
    class LR(nn.Module):
        def __init__(self, in_size):
            nn.Module.__init__(self)
            self.fc = nn.Linear(in_size, 2)

        def forward(self, x):
            import torch.nn.functional as F
            return F.relu(self.fc(x))

    class TrainData():
        def __init__(self, batch_size=100):
            self.batch_size = batch_size
            self.batch_per_epoch = 1000

        def next_iter(self):
            from torch.autograd import Variable

            x = torch.randn(self.batch_size, 2) * 10.
            y = torch.empty(self.batch_size).random_(2).long()
            for idx, a in enumerate(x):
                if torch.cos(a[0]) > a[1]:
                    y[idx] = 0
                else:
                    y[idx] = 1
            
            X = Variable(torch.tensor(x).float())
            Y = Variable(torch.tensor(y).long())
            return X, Y


    import torch.optim as optim

    data = TrainData()
    data.set_batch_size(100)

    model = LR(2)
    optimizer = optim.SGD(model.parameters(), lr=0.01)
    loss_fn = nn.CrossEntropyLoss()

    def fwbp():
        x, y = data.next_iter()
        y_ = model.forward(x)
        loss = loss_fn(y_, y)
        loss.backward()
        return loss[0] / data.batch_size

    # test.
    x, y = data.next_iter()
    easy_test(model, x, y)

    easy_train(fwbp, optimizer, 1000)

    # test.
    x, y = data.next_iter()
    easy_test(model, x, y)

    
