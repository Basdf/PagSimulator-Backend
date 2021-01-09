from __future__ import print_function
import sys
from optparse import OptionParser
import random
import math


# to make Python2 and Python3 act the same -- how dumb
def random_seed(seed):
    try:
        random.seed(seed, version=1)
    except:
        random.seed(seed)
    return


def convert(size):
    length = len(size)
    lastchar = size[length - 1]
    if (lastchar == 'k') or (lastchar == 'K'):
        m = 1024
        nsize = int(size[0:length - 1]) * m
    elif (lastchar == 'm') or (lastchar == 'M'):
        m = 1024 * 1024
        nsize = int(size[0:length - 1]) * m
    elif (lastchar == 'g') or (lastchar == 'G'):
        m = 1024 * 1024 * 1024
        nsize = int(size[0:length - 1]) * m
    else:
        nsize = int(size)
    return nsize


def hfunc(index):
    if index == -1:
        return 'MISS'
    else:
        return 'HIT '


def vfunc(victim):
    if victim == -1:
        return '-'
    else:
        return str(victim)


# ADDRESSES a set of comma-separated pages to access; -1 means randomly generate
# NUMADDRS if addresses is -1, this is the number of addrs to generate
# POLICY replacement policy: FIFO, LRU, MRU, OPT, UNOPT, RAND, CLOCK
# CLOCKBITS for CLOCK policy, how many clock bits to use
# CACHESIZE size of the page cache, in pages
# MAXPAGE if randomly generating page accesses, this is the max page number
# SEED  random number seed


def pagingPolicy(
    addresses='-1',
    numaddrs=10,
    policy='FIFO',
    clockbits=2,
    cachesize=3,
    maxpage=10,
    seed=0,
):
    random_seed(seed)
    addrList = []
    if addresses == '-1':
        for i in range(0, numaddrs):
            n = int(maxpage * random.random())
            addrList.append(n)
    else:
        addrList = addresses.split(',')
    solve = {}
    solve["options"] = {
        "addresses": addrList,
        "numaddrs": numaddrs,
        "policy": policy,
        "clockbits": clockbits,
        "cachesize": cachesize,
        "maxpage": maxpage,
        "seed": seed,
    }
    solve["stats"] = {}
    solve["steps"] = []
    # init memory structure
    count = 0
    memory = []
    hits = 0
    miss = 0

    if policy == 'FIFO':
        leftStr = 'FirstIn'
        riteStr = 'Lastin '
    elif policy == 'LRU':
        leftStr = 'LRU'
        riteStr = 'MRU'
    elif policy == 'MRU':
        leftStr = 'LRU'
        riteStr = 'MRU'
    elif policy == 'OPT' or policy == 'RAND' or policy == 'UNOPT' or policy == 'CLOCK':
        leftStr = 'Left '
        riteStr = 'Right'
    else:
        ##enviar mensaje de error
        print('Policy %s is not yet implemented' % policy)
        exit(1)

    # track reference bits for clock
    ref = {}

    cdebug = False

    # need to generate addresses
    addrIndex = 0
    for nStr in addrList:
        # first, lookup
        n = int(nStr)
        try:
            idx = memory.index(n)
            hits = hits + 1
            if policy == 'LRU' or policy == 'MRU':
                update = memory.remove(n)
                memory.append(n)  # puts it on MRU side
        except:
            idx = -1
            miss = miss + 1

        victim = -1
        if idx == -1:
            # miss, replace?
            # print('BUG count, cachesize:', count, cachesize)
            if count == cachesize:
                # must replace
                if policy == 'FIFO' or policy == 'LRU':
                    victim = memory.pop(0)
                elif policy == 'MRU':
                    victim = memory.pop(count - 1)
                elif policy == 'RAND':
                    victim = memory.pop(int(random.random() * count))
                elif policy == 'CLOCK':
                    # hack: for now, do random
                    # victim = memory.pop(int(random.random() * count))
                    victim = -1
                    while victim == -1:
                        page = memory[int(random.random() * count)]
                        if ref[page] >= 1:
                            ref[page] -= 1
                        else:
                            # this is our victim
                            victim = page
                            memory.remove(page)
                            break

                    # remove old page's ref count
                    if page in memory:
                        assert ('BROKEN')
                    del ref[victim]

                elif policy == 'OPT':
                    maxReplace = -1
                    replaceIdx = -1
                    replacePage = -1
                    # print('OPT: access %d, memory %s' % (n, memory) )
                    # print('OPT: replace from FUTURE (%s)' % addrList[addrIndex+1:])
                    for pageIndex in range(0, count):
                        page = memory[pageIndex]
                        # now, have page 'page' at index 'pageIndex' in memory
                        whenReferenced = len(addrList)
                        # whenReferenced tells us when, in the future, this was referenced
                        for futureIdx in range(addrIndex + 1, len(addrList)):
                            futurePage = int(addrList[futureIdx])
                            if page == futurePage:
                                whenReferenced = futureIdx
                                break
                        # print('OPT: page %d is referenced at %d' % (page, whenReferenced))
                        if whenReferenced >= maxReplace:
                            # print('OPT: ??? updating maxReplace (%d %d %d)' % (replaceIdx, replacePage, maxReplace))
                            replaceIdx = pageIndex
                            replacePage = page
                            maxReplace = whenReferenced
                            # print('OPT: --> updating maxReplace (%d %d %d)' % (replaceIdx, replacePage, maxReplace))
                    victim = memory.pop(replaceIdx)
                    # print('OPT: replacing page %d (idx:%d) because I saw it in future at %d' % (victim, replaceIdx, whenReferenced))
                elif policy == 'UNOPT':
                    minReplace = len(addrList) + 1
                    replaceIdx = -1
                    replacePage = -1
                    for pageIndex in range(0, count):
                        page = memory[pageIndex]
                        # now, have page 'page' at index 'pageIndex' in memory
                        whenReferenced = len(addrList)
                        # whenReferenced tells us when, in the future, this was referenced
                        for futureIdx in range(addrIndex + 1, len(addrList)):
                            futurePage = int(addrList[futureIdx])
                            if page == futurePage:
                                whenReferenced = futureIdx
                                break
                        if whenReferenced < minReplace:
                            replaceIdx = pageIndex
                            replacePage = page
                            minReplace = whenReferenced
                    victim = memory.pop(replaceIdx)
            else:
                # miss, but no replacement needed (cache not full)
                victim = -1
                count = count + 1

            # now add to memory
            memory.append(n)
            if victim != -1:
                assert (victim not in memory)

        # after miss processing, update reference bit
        if n not in ref:
            ref[n] = 1
        else:
            ref[n] += 1
            if ref[n] > clockbits:
                ref[n] = clockbits

        solve["steps"].append({
            "access": n,
            "response": hfunc(idx),
            "leftStr": leftStr,
            "memory": memory[0:],
            "riteStr": riteStr,
            "victim": vfunc(victim),
            "hits": hits,
            "miss": miss,
        })
        addrIndex = addrIndex + 1

    solve["stats"] = {
        "hits": hits,
        "misses": miss,
        "hitrate": (100.0 * float(hits)) / (float(hits) + float(miss))
    }
    return solve
