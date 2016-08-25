from subprocess import Popen,PIPE
import bir


class BapError(Exception):
    "Base class for BAP runtime errors"
    def __init__(self, cmd, out, err):
        self.cmd = cmd
        self.out = out
        self.err = err

    def info(self):
        return """
        Standard output:\n{0}\n
        Standard error: \n{1}\n
        Invoked as: {2}
        """.format(self.out, self.err, ' '.join(self.cmd))

class MalformedOutput(BapError):
    """Raised if we were unable to parse the output of bap. """
    def __init__(self, exn, *args):
        super(MalformedOutput, self).__init__(*args)
        self.exn = exn

    def __str__(self):
        return '\n'.join([
            "expected a valid Python expression, but got",
            str(self.exn),
            self.info()
        ])

class Failed(BapError):
    "Raised when bap subprocess returns a non-zero code"
    def __init__(self, code, *args):
        super(Failed, self).__init__(*args)
        self.code = code

    def __str__(self):
        return '\n'.join([
            "exited with return code {0}".format(self.code),
            self.info()
        ])

class Killed(BapError):
    "Raised when bap subprocess is killed by a signal"
    def __init__(self, signal, *args):
        super(Killed, self).__init__(*args)
        self.signal = signal

    def __str__(self):
        return '\n'.join([
            "received signal {0}".format(self.signal),
            self.info()
        ])


adt_project_parser = {
    'format' : 'adt',
    'load' : bir.loads
}


def run(path, args=[], bap='bap', parser=adt_project_parser):
    r"""run(file[, args] [, bap=PATH] [,parser=PARSER]) -> project

    Run bap on a specified `file`, wait until it finishes, parse
    and return the result, using project data structure as default.

    Example:

    >>> proj = run('/bin/true')

    To specify extra command line arguments, pass them as a list:

    >>> proj = run('/bin/true', ['--no-cache', '--symbolizer=ida'])

    To specify an explicit path to `bap` executable use `bap` keyword
    argument:

    >>> proj = run('/bin/true', bap='/usr/bin/bap')


    By default a project data structure is dumped in ADT format and
    loaded into `bir.Project` data structure. To parse other formats,
    a parser argument can be specified. It must be a dictionary, that
    may contain the following two fields:

      - `format` - a format name as accepted by bap's `--dump` option,
                   it will passed to bap.
      - `load` - a function that parses the output.


    In case of errors, the `load` function must raise `SyntaxError`
    exception. Example:

    >>> version = run('/bin/true', parser={'load' : str.strip})

    If `parser` is `None` or if it doesn't provide `load` function,
    then the program output is returned as is.


    Exceptions
    ----------

    Will pass through exceptions from the underlying subprocess module,
    with OSError being the most common one. If everything went fine on
    the system level, then may raise SyntaxError at the parsing step.
    Also may raise Failed or Killed exceptions in case if the return code
    wasn't zero.


    """
    opts = [bap, path] + args

    if parser and 'format' in parser:
        opts += ['-d{format}'.format(**parser)]

    bap = Popen(opts, stdout=PIPE, stderr=PIPE)
    out,err = bap.communicate()

    if bap.returncode == 0:
        try:
            if parser and 'load' in parser:
                return parser['load'](out)
            else:
                return out
        except SyntaxError as exn:
            raise MalformedOutput(exn, opts, out, err)
    elif bap.returncode < 0:
        raise Killed(-bap.returncode, opts, out, err)
    else:
        raise Failed(bap.returncode, opts, out, err)
