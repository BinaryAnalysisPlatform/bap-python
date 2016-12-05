r"""Python inteface to BAP.


Porcelain Interace
==================

The high level interface allows to run ``bap`` and get back the information
that we were able to infer from the file. It consists only from one function,
``bap.run``, that will drive ``bap`` for you. It is quite versatile, so read the
documentation for the further information.


Example
-------

>>> import bap
>>> proj = bap.run('/bin/true', ['--symbolizer=ida'])
>>> text = proj.sections['.text']
>>> main = proj.program.subs.find('main')
>>> entry = main.blks[0]
>>> next = main.blks.find(entry.jmps[0].target.arg)

It is recommended to explore the interface using ipython or similiar
interactive toplevels.

We use ADT syntax to communicate with python. It is a syntactical
subset of Python grammar, so in fact, bap just returns a valid Python
program, that is then evaluated. The ADT stands for Algebraic Data
Type, and is described in ``adt`` module. For non-trivial tasks one
should consider using ``adt.Visitor`` class.



Plumbing interface [rpc]
========================

The low level interface provides an access to internal services. It
uses ``bap-server``, and talks with bap using RPC protocol. It is in
extras section and must be installed explicitly with ``[rpc]`` tag.

In a few keystrokes:

    >>> import bap
    >>> print '\n'.join(insn.asm for insn in bap.disasm("\x48\x83\xec\x08"))
        decl    %eax
        subl    $0x8, %esp

A more complex example:

    >>> img = bap.image('coreutils_O0_ls')
    >>> sym = img.get_symbol('main')
    >>> print '\n'.join(insn.asm for insn in bap.disasm(sym))
        push    {r11, lr}
        add     r11, sp, #0x4
        sub     sp, sp, #0xc8
        ... <snip> ...

Bap package exposes two functions:

#. ``disasm`` returns a disassembly of the given object
#. ``image``  loads given file

Disassembling things
--------------------

``disasm`` is a swiss knife for disassembling things. It takes either a
string object, or something returned by an ``image`` function, e.g.,
images, segments and symbols.

``disasm`` function returns a generator yielding instances of class
``Insn`` defined in module :mod:`asm`. It has the following attributes:

* name - instruction name, as undelying backend names it
* addr - address of the first byte of instruction
* size - overall size of the instruction
* operands - list of instances of class ``Op``
* asm - assembler string, in native assembler
* kinds - instruction meta properties, see :mod:`asm`
* target - instruction lifter to a target platform, e.g., see :mod:`arm`
* bil - a list of BIL statements, describing instruction semantics.

``disasm`` function also accepts a bunch of keyword arguments, to name a few:

* server - either an url to a bap server or a dictionay containing port
  and/or executable name
* arch
* endian  (instance of ``bil.Endian``)
* addr    (should be an instance of type ``bil.Int``)
* backend
* stop_conditions

All attributes are self-describing I hope. ``stop_conditions`` is a list of
``Kind`` instances defined in :mod:`asm`. If disassembler meets instruction
that is instance of one of this kind, it will stop.

Reading files
-------------

To read and analyze file one should load it with ``image``
function. This function  returns an instance of class ``Image`` that
allows one to discover information about the file, and perform different
queries. It has function ``get_symbol`` function to lookup symbol in
file by name, and the following set of attributes (self describing):

* arch
* entry_point
* addr_size
* endian
* file (file name)
* segments

Segments is a list of instances of ``Segment`` class, that also has a
``get_symbol`` function and the following attributes:

* name
* perm (a list of ['r', 'w', 'x'])
* addr
* size
* memory
* symbols

Symbols is a list of, you get it, ``Symbol`` class, each having the
following attributes:

* name
* is_function
* is_debug
* addr
* chunks

Where chunks is a list of instances of ``Memory`` class, each having the
following attributes:

* addr
* size
* data

Where data is actual string of bytes.
"""

from .bap import run

try :
    from .rpc import disasm, image
except ImportError:
    pass
