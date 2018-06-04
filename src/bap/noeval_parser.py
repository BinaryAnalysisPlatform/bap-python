#! /usr/bin/env python3
'''
Parser for ADT string from bap that does not use eval

The naive eval-based version runs into out-of-memory conditions on large files
'''
import gc
import sys
import time

from subprocess import check_output

# bap.1.3 breaks the format of the following types.  it prints hexes
# without prefixing them with the `0x` escape. To fix it without
# fixing bap, we will treat integers inside this parents as
# hexadecimals if there is no prefix.
BROKEN_TYPES = [
    'Section',
    'Region'
]

# NOTE: uses bap.bir, but cannot import at module level (circular references)

def toint(string, start, end, base=10):
    '''
    Convert substring string[start:end] to integer/long without eval

    Note: may contain leading whitespace
    '''
    istr = string[start:end].lstrip()
    if sys.version_info > (3,): # then longs don't exist
        if istr.endswith('L'):
            istr = istr.rstrip('L')
        of_str = int
    else:
        if istr.endswith('L'):
            of_str = long
        else:
            of_str = int
    if istr.startswith('0x'):
        return of_str(istr, 16)
    else:
        return of_str(istr, base)

def setup_progress(totalitems):
    '''
    Generate functions to help track execution progress
    '''
    last_itemsdone = [0]
    last_timedone = [time.time()]
    def s_to_hms(remain_s):
        '''
        Convert seconds to (hours, minutes, seconds)
        '''
        remain_m = remain_s / 60
        remain_h = remain_m / 60
        remain_m -= remain_h*60
        remain_s = remain_s%60
        return remain_h, remain_m, remain_s
    def progress(itemsdone):
        '''
        Convert itemsdone of totalitems into tuple with elements:
        1. tuple describing progress in units: (done/total, done, total)
        2. remaining time from s_to_hms()
        '''
        itemprogress = (100.0*itemsdone/totalitems, itemsdone, totalitems)
        itemsleft = totalitems - itemsdone
        idelta = itemsdone - last_itemsdone[0]
        last_itemsdone[0] = itemsdone
        timedone = time.time()
        tdelta = timedone - last_timedone[0]
        last_timedone[0] = timedone
        if idelta > 0:
            s_per = tdelta / idelta
            i_remain = itemsleft
            remain_s = int(i_remain * s_per)
            return itemprogress, s_to_hms(remain_s)
        return itemprogress, (-1, -1, -1)
    def interval():
        '''
        Return time since last progress() call
        '''
        return time.time() - last_timedone[0]
    return interval, progress

def _try_update_parent(parent, objs, stk):
    k = stk.pop() # pop the just evaluated item
    del objs[k] # preemtively remove since this is the most likely case
    if stk:
        pparent = objs[stk[-1]]
        assert isinstance(pparent, dict)
        assert pparent, 'parent is empty'
        assert pparent['typ'] != 'int', 'parent wrong type: %r' % (pparent['typ'])
        assert 'children' in pparent
        pparent['children'].append(parent)
    else: # put things back (unlikely)
        stk.append(k)
        objs[k] = parent

def _parse_str(in_c, in_s, i, objs, stk):
    del in_c # unused
    endpos = i
    while True: # find non-escaped double quote
        endpos = in_s.find('"', endpos+1)
        if endpos < 0:
            raise ParserInputError("mismatched double-quote")
        if in_s[endpos-1] == '\\': # may be escaped double quote...
            # or could be a real quote after escaped slash
            # count slashes going back
            k = endpos - 2
            while k >= 0 and in_s[k] == '\\':
                k -= 1
            slashes = (endpos - 1) - k
            if slashes % 2 == 0: # this is really an ending double quote
                break
            # otherwise it's not
            continue
        break
    k = stk[-1]
    assert all((in_s[_k] in (' ', '\t', '\n') for _k in range(k, i))), \
            'pre quote is not whitespace at [%d..%d)' % (k, i)
    if sys.version_info > (3,):
        # need to use unicode_escape of a bytes, but have a str
        parent = objs[k] = (in_s[i+1:endpos]).encode('utf-8').decode('unicode_escape')
    else:
        parent = objs[k] = in_s[i+1:endpos].decode('string_escape')
    ## try added new item to parent
    _try_update_parent(parent, objs, stk)
    # next obj
    i = endpos+1
    stk.append(i)
    objs[i] = {}
    return i

def _parse_finished(in_c, in_s, i, objs, stk):
    del in_c # unused
    # close an int, or make sure top object is empty and pop/return
    k = stk.pop()
    top = objs[k]
    del objs[k] # remove from hash
    if top: # must be an int
        assert isinstance(top, dict)
        if top.get('typ', None) != 'd':
            raise ParserInputError('Incomplete input stream')
        try:
            objs[k] = toint(in_s, k, i)
        except ValueError:
            raise ParserInputError("Integer expected between [%d..%d)" % (k, i))
        # push it back
        stk.append(k) # this is unlikely so put the extra work here
    return

def _parse_end(in_c, in_s, i, objs, stk):
    if 'typedb' not in globals(): # first time through this function
        # Need access to bap.bir namespace, but avoid circular import
        global bir # pylint: disable=global-variable-not-assigned,invalid-name
        from .bap import bir
        # potential optimization
        # define the typedb to optimize
#        global typedb # pylint: disable=global-variable-undefined,invalid-name
#        typedb = {}
    # pop last object
    k = stk.pop()
    top = objs[k]
    del objs[k] # remove from hash
    # look at parent
    if not stk:
        raise ParserInputError('Mismatched input stream')
    j = stk[-1]
    parent = objs[j]
    ptyp = parent['typ']
    assert isinstance(parent, dict)
    assert parent, 'parent is empty'
    assert ptyp != 'int', 'parent wrong type: %r' % (parent['typ'])
    assert 'children' in parent
    if top: # add to parent if non empty
        # make real int before appending
        if top['typ'] == 'd': # int
            try:
                base = 16 if ptyp in BROKEN_TYPES else 10
                top = toint(in_s, k, i, base)
            except ValueError:
                raise ParserInputError("Integer expected between [%d..%d)" % (k, i))
        parent['children'].append(top)
    if in_c == ',': # add blank object and move on
        # next obj
        i = i+1
        stk.append(i)
        objs[i] = {}
        return i
    else: # we are ending a tuple/list/app do it
        # maybe handle apply (num and seq are earlier)
        if ptyp == '[':
            if in_c != ']':
                raise ParserInputError('close %r and open %r mismatch' % (in_c, ptyp))
            parent = objs[j] = parent.get('children', []) # pylint: disable=redefined-variable-type
        elif ptyp == '(':
            if in_c != ')':
                raise ParserInputError('close %r and open %r mismatch' % (in_c, ptyp))
            parent = objs[j] = tuple(parent.get('children', ())) # pylint: disable=redefined-variable-type
        else:
            name = ptyp
            # potential optimization
#            if name not in typedb:
#                typedb[name] = getattr(bir, name)
#            parent = objs[j] = typedb[name](*parent.get('children', ())) # pylint: disable=redefined-variable-type
            parent = objs[j] = getattr(bir, name)(*parent.get('children', ())) # pylint: disable=redefined-variable-type
        # now add to parent if exists
        _try_update_parent(parent, objs, stk)
        # next obj
        i = i+1
        stk.append(i)
        objs[i] = {}
        return i

def _parse_start(in_c, in_s, i, objs, stk):
    k = stk[-1]
    top = objs[k]
    if top: # not empty means app
        name_start = top['start'] # avoids whitespace issue
        name = in_s[name_start:i] # could just strip?
        top['typ'] = name
    else:
        top['typ'] = in_c # list or tuple
    top['children'] = []
    # next obj
    i = i+1
    stk.append(i)
    objs[i] = {}
    return i

def _parse_any(in_c, in_s, i, objs, stk):
    del in_s # unused
    # look at top to determine type
    top = objs[stk[-1]]
    if not top: # empty, so need to make type choice between int and app
        if in_c.isdigit():
            top['typ'] = 'd'
        elif in_c in (' ', "\t", "\n"): # ignore whitespace
            pass # no setting, skipping whitespace
        else:
            top['typ'] = 'a'
            top['start'] = i # needed since whitespace might make the stack index off
    else:
        pass # type choice is already made and this char is not interesting
    i = i + 1 # keep going!
    return i

_parse_functions = { # pylint: disable=invalid-name
    '"': _parse_str,
    ')': _parse_end,
    ']': _parse_end,
    ',': _parse_end,
    '(': _parse_start,
    '[': _parse_start,
}

def _parser(in_s, logger=None):
    '''
    Main no-eval parser implementation
    '''
    i = 0
    s_len = len(in_s)
    stk = [0] # start with 'top' position in stack
    objs = {0:{}} # start with blank object
    # upon reading a character it always belong to the top object
    # if the char ends the top object, then a new empty top is created
    # top object uninitialized going into loop first time
    interval_check, get_progress = setup_progress(s_len)
    while i <= s_len:
        if logger is not None and interval_check() > 5:
            progress, remaining = get_progress(i)
            logger.info("progress: %0.2f%% : %10d of %d" % progress)
            logger.info("remaining: %02d:%02d:%02d" % remaining)
        if i < s_len:
            in_c = in_s[i]
        else:
            assert i == s_len
            _parse_finished(in_c, in_s, i, objs, stk)
            break
        parse_func = _parse_functions.get(in_c, _parse_any)
        i = parse_func(in_c, in_s, i, objs, stk)
#        if c == '"':
#            i = _parse_str(c, s, i, objs, stk)
#        elif c in (',', ')', ']'): # ending item, tricky because tuple/list can end in comma
#            i = _parse_end(c, s, i, objs, stk)
#        elif c in ('(', '['):
#            i = _parse_start(c, s, i, objs, stk)
#        else:
#            i = _parse_any(c, s, i, objs, stk)
    assert len(stk) == 1
    assert stk[0] == 0
    assert 0 in objs
    result = objs[0]
    if isinstance(result, dict):
        raise ParserInputError('Incomplete input string')
    return objs[0]

class ParserInputError(Exception):
    '''Class of exceptions for bad input to the parser'''
    pass
class ParserError(Exception):
    '''Class of exceptions for errors in the parser, not the input'''
    pass

def parser(input_str, disable_gc=False, logger=None):
    '''
    Entrypoint to optimized adt parser.
    Input: string (non-empty)
    Output: Python object equivalent to eval(input_str) in the context bap.bir

    Options: disable_gc: if true, no garbage collection is done while parsing

    Notes: Expects a well formatted (ie. balanced) string with caveats:
        Only contains string representations of tuples, lists, integers, and
        function calls with name such that bap.bir.hasattr(name) is true.
        Integers may start with '0x' for base 16, otherwise base 10 is assumed.
        Strings must start and end with double-quote and not contain a
        double-quote, not even an escaped one
    '''
    # _parser expects a str
    if not isinstance(input_str, str):
        input_str = input_str.decode('utf-8')
    if input_str == '':
        raise ParserInputError("ADT Parser called on empty string")
    if disable_gc:
        gc.disable() # disable for better timing consistency during testing
    result = _parser(input_str, logger=logger)
    if disable_gc:
        gc.enable()
    gc.collect() # force garbage collection to reclaim memory before we leave
    return result

EVALFREE_ADT_PARSER = {
    'format': 'adt',
    'load': parser
}
