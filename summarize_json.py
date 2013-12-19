# Summarizes the contents of a JSON file
# Created by Philip Guo on 2013-07-18

import json
import sys
import operator
from collections import defaultdict

def spaces(level):
    return '  ' * level


# returns a dict with keys num_dicts, num_lists, num_strings, num_bools,
# num_numbers, num_nulls
def analyze_types(lst):
    ret = defaultdict(int)
    for e in lst:
        if type(e) is dict:
            ret['dict'] += 1
        elif type(e) is list:
            ret['list'] += 1
        elif type(e) in (str, unicode):
            ret['string'] += 1
        elif type(e) in (int, long, float):
            ret['number'] += 1
        elif type(e) is bool:
            ret['bool'] += 1
        else:
            assert e is None
            ret['null'] += 1
    return ret

# returns 'dict', 'list', 'string', 'number', 'bool', 'null'
# if type_dict is COMPLETELY HOMOGENEOUS, otherwise return None
def get_homogeneous_type(type_dict):
    names_and_counts = type_dict.items()
    non_zero = [e for e in names_and_counts if e[1] > 0]
    if len(non_zero) != 1:
        return None
    else:
        return non_zero[0][0]

def pp_type_dict(type_dict):
    names_and_counts = ['%d %ss' % (e[1], e[0]) for e in type_dict.items()]
    return ', '.join(names_and_counts)
    

def summarize_dict(d, indent):
    for k, v, in d.iteritems():
        print spaces(indent) + '> ' + repr(str(k)), ':'

        if type(v) is dict:
            print spaces(indent+1) + 'dict {'
            summarize_dict(v, indent+1)
            print spaces(indent+1) + '}'
        elif type(v) is list:
            print spaces(indent+1) + 'list ['
            summarize_list(v, indent+1)
            print spaces(indent+1) + ']'
        else:
            print spaces(indent+1) + repr(str(v))


def summarize_list(lst, indent, is_toplevel=False):
    type_dict = analyze_types(lst)

    ht = get_homogeneous_type(type_dict)
    prefix = spaces(indent+1)
    if len(lst) == 0:
        print prefix + 'empty'
    elif ht:
        if ht == 'dict':
            print prefix + 'dict {'
            summarize_list_of_dicts(lst, indent+1)
            print prefix + '}'
        elif ht == 'list':
            print prefix + 'list ['
            summarize_list_of_lists(lst, indent+1)
            print prefix + ']'
        elif ht == 'number':
            print prefix + ht,
            summarize_list_of_numbers(lst)
        elif ht == 'string':
            print prefix + ht
            summarize_list_of_strings(lst, indent+1)
        elif ht == 'bool':
            print prefix + ht
            summarize_list_of_bools(lst, indent+1)
        else:
            assert ht == 'null'
            print prefix + ht
            #summarize_list_of_nulls(lst, indent+1)
    else:
        # test on
        # python summarize_json.py opt-aliasing-golden.trace.json 
        print prefix + 'heterogeneous list:', pp_type_dict(type_dict)

    if is_toplevel:
        print prefix + 'list.length:', len(lst)


def summarize_list_of_dicts(lst, indent):
    field_counts = defaultdict(int)
    total = len(lst)

    for e in lst:
        assert type(e) is dict
        for k in e.keys():
            field_counts[k] += 1

    for f, c in field_counts.iteritems():
        print spaces(indent+1) + '> ' + repr(str(f)),
        if c < total:
            sublist = [e[f] for e in lst if f in e]
            print '(%d of %d records) :' % (c, total)
        else:
            sublist = [e[f] for e in lst]
            print ':'

        summarize_list(sublist, indent+1)


def summarize_list_of_numbers(lst):
    lst_min = min(lst)
    lst_max = max(lst)
    lst_mean = float(sum(lst)) / len(lst)

    # singleton
    if len(set(lst)) == 1:
        print str(lst[0])
        return

    print '[min: %.4g, mean: %.4g, max: %.4g]' % (lst_min, lst_mean, lst_max),

    # test sortedness or reverse sortedness
    if sorted(lst) == lst:
        print 'sorted'
    elif reversed(lst) == lst:
        print 'reverse sorted'
    else:
        print


def summarize_list_of_strings(lst, indent):
    hist = defaultdict(int)
    for e in lst:
        hist[e] += 1

    # if only singletons, don't do anything
    if len(set(hist.values())) == 1 and hist.values()[0] == 1:
        return

    # print N most common as 'enums' if they're NOT singletons
    i = 0
    N = 5
    display_leftovers = False
    printed_set = set()
    for k,v in sorted(hist.items(), key=lambda e:e[1], reverse=True):
        # by the time we reach a singleton, just break (since we're
        # reverse sorted, so everything else is a singleton by now)
        if v == 1:
            break

        print spaces(indent+1) + repr(str(k)), 'x', v
        display_leftovers = True
        printed_set.add(k)

        i += 1
        if i >= N:
            break

    num_others = len(set(hist.keys()) - printed_set)
    if num_others > 0 and display_leftovers:
        print spaces(indent+1) + '%d other elements' % num_others


def summarize_list_of_bools(lst, indent):
    num_true = num_false = 0
    for e in lst:
        if e is True:
            num_true += 1
        else:
            assert e is False
            num_false += 1
    print spaces(indent+1) + '[True: %d, False: %d]' % (num_true, num_false)


def summarize_list_of_lists(lst, indent):
    list_lengths = [len(e) for e in lst]

    # analyze types of each constituent sublist
    hts = set()
    for e in lst:
        type_dict = analyze_types(e)
        ht = get_homogeneous_type(type_dict)
        if ht:
            hts.add(ht)

    if not hts:
        print spaces(indent+1) + '[heterogeneous sub-lists]'
    elif len(hts) == 1:
        homogeneous_type = list(hts)[0]
        # flatten the list and recurse, tricky tricky!
        flattened_lst = reduce(operator.add, lst)
        if flattened_lst:
            summarize_list(flattened_lst, indent) # don't increase the indent level!
        else:
            print spaces(indent+1) + 'empty lists'
    else:
        print spaces(indent+1) + ', '.join(sorted(hts)) + ' (heterogeneous)'

    print spaces(indent+1) + 'sublist.lengths:',
    summarize_list_of_numbers(list_lengths)


if __name__ == "__main__":
    o = json.load(open(sys.argv[1]))
    if type(o) is dict:
        print 'dict {'
        summarize_dict(o, 0)
        print '}'
    elif type(o) is list:
        print 'list ['
        summarize_list(o, 0, True)
        print ']'
    else:
        print 'Primitive:', o

