"""
Test module for bap.noeval_parser
"""
# pylint: disable=import-error
import sys
import logging
import bap
from bap.noeval_parser import parser, EVALFREE_ADT_PARSER, ParserInputError, ParserError

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def lparser(input_str):
    """
    wrapper for lparser under test so we can pass a logger in just one
    spot
    """
    return parser(input_str, logger=logger)


EVALFREE_ADT_PARSER["load"] = lparser  # override with wrapper so we have logging


def test_parser_1():
    # pylint: disable=missing-docstring,invalid-name
    s = "()"
    tok = lparser(s)
    assert tok == ()


def test_parser_2():
    # pylint: disable=missing-docstring,invalid-name
    s = "(())"
    tok = lparser(s)
    assert tok == ((),)


def test_parser_3():
    # pylint: disable=missing-docstring,invalid-name
    s = "((),)"
    tok = lparser(s)
    assert tok == ((),)


def test_parser_4():
    # pylint: disable=missing-docstring,invalid-name
    s = "([],)"
    tok = lparser(s)
    assert tok == ([],)


def test_parser_5():
    # pylint: disable=missing-docstring,invalid-name
    s = "([1],)"
    tok = lparser(s)
    assert tok == ([1],)


def test_parser_6():
    # pylint: disable=missing-docstring,invalid-name
    def hello(x):
        assert x == [1]
        return "hi"

    bap.bir.hello = hello  # hack to test function applications
    try:
        s = "hello([1],)"
        tok = lparser(s)
        assert tok == "hi"
    finally:
        del bap.bir.hello


def test_parser_7():
    # pylint: disable=missing-docstring,invalid-name
    s = '("abc")'
    tok = lparser(s)
    assert tok == ("abc",)


def test_parser_8():
    # pylint: disable=missing-docstring,invalid-name
    def hello(x):
        assert x == [1]
        return "hi"

    bap.bir.hello = hello
    s = '( "abc")'
    tok = lparser(s)
    assert tok == ("abc",)


def test_parser_9():
    # pylint: disable=missing-docstring,invalid-name
    s = r'"\""'
    tok = lparser(s)
    assert tok == '"'


def test_parser_10():
    # pylint: disable=missing-docstring,invalid-name
    s = '"\\\\"'
    assert eval(s) == "\\"  # pylint: disable=eval-used
    tok = lparser(s)
    assert tok == "\\"


def test_parser_12():
    # pylint: disable=missing-docstring,invalid-name
    s = r'"\\\""'
    assert eval(s) == '\\"'  # pylint: disable=eval-used
    tok = lparser(s)
    assert tok == '\\"'


def test_parser_11():
    # pylint: disable=missing-docstring,invalid-name
    s = r'"\'"'
    tok = lparser(s)
    assert tok == "'"


def test_compare_to_old_escapes_1(tmpdir):
    # pylint: disable=missing-docstring,invalid-name
    import os

    tmpdir.join("test.c").write("int main() { return 0; }")
    with tmpdir.as_cwd():
        assert os.system("gcc -o test.out test.c") == 0
        comment = r"a slash: \\"
        main(
            [None, "test.out"],
            extras=(
                [
                    "--map-terms-with",
                    '((true) (comment "{}"))'.format(comment),
                    "--map-terms",
                ],
            ),
        )
        main(
            [None, "test.out", "skip"],
            extras=(
                [
                    "--map-terms-with",
                    '((true) (comment "{}"))'.format(comment),
                    "--map-terms",
                ],
            ),
        )


def test_compare_to_old_escapes_2(tmpdir):
    # pylint: disable=missing-docstring,invalid-name
    import os

    tmpdir.join("test.c").write("int main() { return 0; }")
    with tmpdir.as_cwd():
        assert os.system("gcc -o test.out test.c") == 0
        comment = r"an escaped quote: \""
        main(
            [None, "test.out"],
            extras=(
                [
                    "--map-terms-with",
                    '((true) (comment "{}"))'.format(comment),
                    "--map-terms",
                ],
            ),
        )
        main(
            [None, "test.out", "skip"],
            extras=(
                [
                    "--map-terms-with",
                    '((true) (comment "{}"))'.format(comment),
                    "--map-terms",
                ],
            ),
        )


def test_compare_to_old_escapes_3(tmpdir):
    # pylint: disable=missing-docstring,invalid-name
    import os

    tmpdir.join("test.c").write("int main() { return 0; }")
    with tmpdir.as_cwd():
        assert os.system("gcc -o test.out test.c") == 0
        comment = r"an escaped slash and then escaped quote: \\\""
        main(
            [None, "test.out"],
            extras=(
                [
                    "--map-terms-with",
                    '((true) (comment "{}"))'.format(comment),
                    "--map-terms",
                ],
            ),
        )
        main(
            [None, "test.out", "skip"],
            extras=(
                [
                    "--map-terms-with",
                    '((true) (comment "{}"))'.format(comment),
                    "--map-terms",
                ],
            ),
        )


def test_compare_to_old_escapes_4(tmpdir):
    # pylint: disable=missing-docstring,invalid-name
    comment = r"an escaped slash and then escaped quote: \\\""
    import os

    tmpdir.join("test.c").write("int main() { return 0; }")
    comment_file = tmpdir.join("comment.scm")
    comment_file.write('((true) (comment "{}"))'.format(comment))
    with tmpdir.as_cwd():
        assert os.system("gcc -o test.out test.c") == 0
        main(
            [None, "test.out"],
            extras=(["--map-terms-using=%s" % comment_file, "--map-terms"],),
        )
        main(
            [None, "test.out", "skip"],
            extras=(["--map-terms-using=%s" % comment_file, "--map-terms"],),
        )


def test_parser_badinput_1():
    # pylint: disable=missing-docstring,invalid-name
    with pytest.raises(ParserInputError):
        lparser("a")


def test_parser_badinput_2():
    # pylint: disable=missing-docstring,invalid-name
    with pytest.raises(ParserInputError):
        lparser("(")


def test_parser_badinput_3():
    # pylint: disable=missing-docstring,invalid-name
    with pytest.raises(ParserInputError):
        lparser(")")


def test_parser_badinput_4():
    # pylint: disable=missing-docstring,invalid-name
    with pytest.raises(ParserInputError):
        lparser("")


def test_parser_badinput_5():
    # pylint: disable=missing-docstring,invalid-name
    with pytest.raises(ParserInputError):
        lparser(",")


def test_parser_badinput_6():
    # pylint: disable=missing-docstring,invalid-name
    with pytest.raises(ParserInputError):
        lparser("1a2")


def test_parser_badinput_7():
    # pylint: disable=missing-docstring,invalid-name
    with pytest.raises(ParserInputError):
        lparser("(]")


def test_parser_badinput_8():
    # pylint: disable=missing-docstring,invalid-name
    with pytest.raises(ParserInputError):
        lparser("[)")


def test_big_1():
    # pylint: disable=missing-docstring,invalid-name
    n = 1000
    hard_to_eval = "(" * n + "0," + ")" * n
    try:
        eval(hard_to_eval)  # pylint: disable=eval-used
        assert False, "expected MemoryError"
    except MemoryError:
        pass  # expected
    result = lparser(hard_to_eval)
    # try to verify structure
    i = 0
    while i < n - 1:
        i += 1
        assert isinstance(result, tuple)
        #        assert len(list(result)) == 0 # this hits same MemoryError
        assert result[0] is result[-1]  # this test is equivalent I think
        result = result[0]
    assert isinstance(result, tuple)
    assert len(result) == 1
    assert result == (0,)


def test_compare_to_old_1(tmpdir):
    # pylint: disable=missing-docstring,invalid-name
    import os

    tmpdir.join("test.c").write("int main() { return 0; }")
    with tmpdir.as_cwd():
        assert os.system("gcc -o test.out test.c") == 0
        main([None, "test.out"])


def test_compare_to_old_2(tmpdir):
    # pylint: disable=missing-docstring,invalid-name
    import os

    tmpdir.join("test.c").write("int main() { return 0; }")
    with tmpdir.as_cwd():
        assert os.system("gcc -o test.out test.c") == 0
        main([None, "test.out", "skipeval"])


# NOTE: this should be the last test to avoid memory usage affecting other tests
def test_compare_to_old_verybig(tmpdir):
    # pylint: disable=missing-docstring,invalid-name
    import os

    tmpdir.join("test.c").write("int main() { return 0; }")
    with tmpdir.as_cwd():
        assert os.system("gcc -static -o test.out test.c") == 0
        main([None, "test.out", "skipeval"])


# Fixed ADT.__repr__ to match bap output to support testing
# Should consider merging this, but breaks compatabilty if anybody relied on
# the str() or repr() results on an ADT object
# Also bap seems to be inconsistent with trailing commas in tuples, so not sure
# which one is strictly better

integer_types = (
    (int, long) if sys.version_info < (3,) else (int,)
)  # pylint: disable=invalid-name

# this version always has trailing commas in tuples
def ADT_repr1(self):  # copied from bap.adt with tweaks. pylint: disable=invalid-name
    # pylint: disable=missing-docstring, invalid-name
    def qstr(x):
        if isinstance(x, integer_types):
            return "0x{0:x}".format(x)
        elif isinstance(x, bap.adt.ADT):
            return repr(x)
        elif isinstance(x, tuple):
            return "(" + ",".join(qstr(i) for i in x) + ",)"  # always trailing commas
        elif isinstance(x, list):
            return "[" + ",".join(qstr(i) for i in x) + "]"
        else:
            return '"' + repr(x)[1:-1] + '"'

    def args():
        if isinstance(self.arg, tuple):
            return ",".join(qstr(x) for x in self.arg)
        else:
            return qstr(self.arg)

    return "{0}({1})".format(self.constr, args())


# this version never has trailing commas in tuples
def ADT_repr2(self):  # copied from bap.adt with tweaks. pylint: disable=invalid-name
    # pylint: disable=missing-docstring, invalid-name
    def qstr(x):
        if isinstance(x, integer_types):
            return "0x{0:x}".format(x)
        elif isinstance(x, bap.adt.ADT):
            return repr(x)
        elif isinstance(x, tuple):
            return "(" + ",".join(qstr(i) for i in x) + ")"
        elif isinstance(x, list):
            return "[" + ",".join(qstr(i) for i in x) + "]"
        else:
            return '"' + repr(x)[1:-1] + '"'

    def args():
        if isinstance(self.arg, tuple):
            return ",".join(qstr(x) for x in self.arg)
        else:
            return qstr(self.arg)

    return "{0}({1})".format(self.constr, args())


def conv(s, i, mayint=True):  # pylint: disable=invalid-name
    """helper function for comparing bap string output and the __repr__ of
    ADT objects
    """
    if s[i] == " " and s[i - 1] == ",":  # skip whitespace after comma
        j = i + 1
        while s[j] == " ":
            j += 1
        return conv(s, j)
    elif s[i] == "\\":  # handle escaped values
        if s[i + 1] == "x":
            assert s[i + 2] in "0123456789abcdef"
            assert s[i + 3] in "0123456789abcdef"
            return chr(int(s[i + 2 : i + 4], 16)), i + 4
        else:
            return eval('"' + s[i : i + 2] + '"'), i + 2  # pylint: disable=eval-used
    elif (
        mayint and s[i : i + 2] == "0x"
    ):  # try to normalize integers in hex representation
        j = i + 2
        while s[j] in "0123456789abcdef":
            j += 1
        if j == (i + 2):  # not really a hex integer expression
            return s[i], i + 1
        return int(s[i + 2 : j], 16), j  # NOTE: returning int not char
    else:
        return s[i], i + 1


def get_proj_strs(proj):
    """
    Returns results of repr(proj) with various bap.adt.ADT.__repr__
    implementations

    Uses ADT_repr1 and ADT_repr2 as neccessary based on Python version
    """
    astr0 = repr(proj)  # get string represtation
    orig_ADT_repr = bap.adt.ADT.__repr__  # pylint: disable=invalid-name
    try:
        if True:
            #        if sys.version_info < (3,):
            bap.adt.ADT.__repr__ = ADT_repr1  # Monkey patch in ADT_repr1
        astr1 = repr(proj)  # get string represtation
        if True:
            #            if sys.version_info < (3,):
            bap.adt.ADT.__repr__ = ADT_repr2  # Monkey patch in ADT_repr2
        astr2 = repr(proj)  # get string represtation
    finally:
        bap.adt.ADT.__repr__ = orig_ADT_repr  # fix before leaving

    return astr0, astr1, astr2


def _compare_proj_str(estr, possible_actual_strs):
    """
    Compare string output from bap with (normalized) repr() of the project
    created with the eval-free parser

    Comparison is unfortunately complex.  We need to compare varying
    representations without resorting to eval otherwise we hit the same bug
    the eval-free parser is trying to fix.
    """
    exceptions = []
    for aidx, astr in enumerate(
        possible_actual_strs
    ):  # so we can try both ADT_repr implementations
        try:
            i = 0
            j = 0
            a_len = len(astr)
            e_len = len(estr)

            while i < a_len and j < e_len:
                achar, i_new = conv(astr, i)
                echar, j_new = conv(estr, j)
                if achar == echar:
                    i = i_new
                    j = j_new
                    continue
                else:
                    if estr[j] == "\\":  # try the simple version of achar
                        achar_new, i_new_new = astr[i], i + 1
                        if achar_new == echar:
                            i = i_new_new
                            j = j_new
                            continue
                    if isinstance(achar, integer_types) and not isinstance(
                        echar, integer_types
                    ):
                        # convert echar and compare
                        k = j + 1
                        while estr[k] in "0123456789":
                            k += 1
                        try:
                            eint = int(estr[j:k])
                            info = "int mismatch at i=%d j=%d %d!=%d" % (
                                i,
                                j,
                                achar,
                                eint,
                            )
                            assert achar == eint, info
                            j = k
                            i = i_new
                            continue
                        except (ValueError, AssertionError):
                            # couldnt convert to int, or they dont match
                            # try non-integer version
                            achar, i_new = conv(astr, i, mayint=False)
                            if achar == echar:
                                i = i_new
                                j = j_new
                                continue
                    if astr[i] == ",":  # try again but "no-comma"  ADT_repr
                        break  # while and go on to next astr option
                    info = ""
                    info += "proj failed at index i=%d j=%d\n" % (i, j)
                    if i >= 20:
                        info += "astr = %s\n%s\n" % (
                            astr[i - 20 : i + 10],
                            "-" * (7 + 20) + "^",
                        )
                    else:
                        info += "astr = %s\n%s\n" % (
                            astr[0 : i + 10],
                            "-" * (i + 7) + "^",
                        )
                    if j >= 20:
                        info += "estr = %s\n%s\n" % (
                            estr[j - 20 : j + 10],
                            "-" * (7 + 20) + "^",
                        )
                    else:
                        info += "estr = %s\n%s\n" % (
                            estr[0 : j + 10],
                            "-" * (j + 7) + "^",
                        )
                    assert False, info
            break  # done ok!
        except Exception as exc:  # pylint: disable=broad-except
            exceptions.append((exc, sys.exc_info()))
            if (aidx + 1) == len(
                possible_actual_strs
            ):  # then we're on last one so raise all
                # if all the exceptions were the same, just reraise this one
                set_of = set((str(e) for (e, _) in exceptions))
                if len(set_of) == 1:
                    #                    raise
                    assert False, exceptions
                # otherwise assert False with all of them
                assert False, exceptions


def main(argv=None, debugging=False, extras=()):
    """
    Main entry point, allows quick comparison of eval-based adt parser with this
    eval-free adt parser.

    Done by parsing, then comparing objects with ==.

    Also converts objects to strings for char-by-char comparison if the objects
    don't match, or the eval version can/should not be used.
    """
    import os  # this is one of the few test functions needing this module

    # setup parser struct that uses eval.  Do this explicitly so tests always
    # compare against an eval version, even after the code is (hopefully) merged
    witheval_adt_parser = {
        "format": "adt",
        "load": lambda s: eval(s, bap.bir.__dict__),  # pylint: disable=eval-used
    }

    if argv is None:
        argv = sys.argv
    toparse = argv[1]
    if not debugging:
        debugging = len(argv) > 3
        logger.debug("debugging = %s", debugging)

    if debugging and os.path.exists("estr.txt"):  # optional optimize
        logger.debug("loading estr.txt")
        with open("estr.txt") as fobj:
            estr = fobj.read()
    else:
        skipeval = len(argv) > 2
        if skipeval:
            logger.info("Calling bap.run(%r, parser=PASSTHRU)", toparse)
            projtxt = bap.run(
                toparse, *extras, parser={"format": "adt", "load": lambda s: s}
            )
            if not isinstance(projtxt, str):  # on python3 projtxt is bytes not str
                estr = projtxt.decode("utf-8")
            else:
                estr = str(projtxt)  # pylint: disable=redefined-variable-type
            # normalize white space in input
            estr = estr.replace("\n", "")
            # normalize strings in input
        else:
            logger.info("Calling bap.run(%r, parser=WITHEVAL)", toparse)
            origproj = bap.run(toparse, *extras, parser=witheval_adt_parser)

        # make sure to do this here not before calling bap the first time
        # Once this runs, if a lot of memory is used, Python can't create
        # child processes in all cases because os.fork() will fail under heavy
        # memory load
        logger.info("Calling bap.run(%r, parser=EVALFREE)", toparse)
        new_proj = bap.run(toparse, *extras, parser=EVALFREE_ADT_PARSER)

        if not skipeval:
            if origproj == new_proj:  # done!
                return
            estr = str(origproj)

    if debugging and all(
        (  # optionally optimize to test faster
            os.path.exists("/tmp/astr0.txt"),
            os.path.exists("/tmp/astr1.txt"),
            os.path.exists("/tmp/astr2.txt"),
        )
    ):
        logger.debug("loading astr0.txt")
        with open("/tmp/astr0.txt") as fobj:
            astr0 = fobj.read()
        logger.debug("loading astr1.txt")
        with open("/tmp/astr1.txt") as fobj:
            astr1 = fobj.read()
        logger.debug("loading astr2.txt")
        with open("/tmp/astr2.txt") as fobj:
            astr2 = fobj.read()
    else:  # normal test path
        if "new_proj" not in locals():  # since we may have optimized it out
            logger.info("Calling bap.run(%r, parser=EVALFREE)", toparse)
            new_proj = bap.run(toparse, parser=EVALFREE_ADT_PARSER)

        astr0, astr1, astr2 = get_proj_strs(new_proj)

    if debugging:  # save for manual inspection
        with open("/tmp/astr0.txt", "w") as fobj:
            fobj.write(astr1)
        with open("/tmp/astr1.txt", "w") as fobj:
            fobj.write(astr1)
        with open("/tmp/astr2.txt", "w") as fobj:
            fobj.write(astr2)
        with open("/tmp/estr.txt", "w") as fobj:
            fobj.write(estr)

    _compare_proj_str(estr, (astr0, astr1, astr2))


try:
    import pytest  # pylint: disable=wrong-import-position

    HAVE_PYTEST = True
except ImportError:
    HAVE_PYTEST = False

if HAVE_PYTEST:
    # mark the slow ones as 'slow'
    # Run pytest with '--slow' to also run the slow tests
    test_compare_to_old_verybig = pytest.mark.slow(
        test_compare_to_old_verybig
    )  # pylint: disable=invalid-name

if __name__ == "__main__":
    main()
