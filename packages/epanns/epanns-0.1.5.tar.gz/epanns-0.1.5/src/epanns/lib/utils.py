#!/usr/bin python
# -*- coding:utf-8 -*-

import torch
import csv

def load_csv_labels(labels_csv_path):
    """
    """
    with open(labels_csv_path, "r") as f:
        reader = csv.reader(f, delimiter=",")
        lines = list(reader)
    idxs, ids, labels = zip(*lines[1:])
    num_classes = len(labels)
    return num_classes, ids, labels

def move_data_to_device(x, device):
    if 'float' in str(x.dtype):
        x = torch.Tensor(x)
    elif 'int' in str(x.dtype):
        x = torch.LongTensor(x)
    else:
        return x

    return x.to(device)

def do_mixup(x, mixup_lambda):
    out = x[0::2].transpose(0, -1) * mixup_lambda[0::2] + \
        x[1::2].transpose(0, -1) * mixup_lambda[1::2]
    return out.transpose(0, -1)
