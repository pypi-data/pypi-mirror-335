#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright @2025 AI. Inspur Inc.
#
# @author: sunxian <sunxian@inspur.com>
# @date: 2025/01/21
#

def _shard_partition(items, rank, world_size):
    src = (rank * len(items)) // world_size
    dst = ((rank+1) * len(items)) // world_size
    return items[src:dst]

