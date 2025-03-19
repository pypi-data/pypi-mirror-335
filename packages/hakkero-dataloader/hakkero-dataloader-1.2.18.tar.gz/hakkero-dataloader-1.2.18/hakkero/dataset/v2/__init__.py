#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright @2025 AI. Inspur Inc.
#
# @author: sunxian <sunxian@inspur.com>
# @date: 2025/01/21
#
import torch.utils.data


def get_dummy_dataloader(max_len, batch_size, vocab_size, rank, world_size):
    class SteadyCounter(torch.utils.data.IterableDataset):
        def __init__(self, max_len, vocab_size):
            self.i = 0

            self.max_len = max_len
            self.vocab_size = vocab_size

        def __iter__(self):
            while True:
                out = torch.Tensor([x % self.vocab_size for x in range(self.i, self.i + self.max_len)]).long()
                yield out, out

                self.i += self.max_len

    data = SteadyCounter(max_len, vocab_size)
    return torch.utils.data.DataLoader(data, batch_size=batch_size)

def get_dataloader(cfg, rank, world_size):
    pass