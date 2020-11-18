BAP python bindings

# Installing

Install python bindings with pip (after you have installed `bap`):

```bash
$ pip install bap
```

Alternatively you can just copy paste files into your project, or clone it
with git-subtree.


## Installing low-level bindings

An optional low-level interface, called [rpc] depends on the requests
library and the bap-server package. To use it, you need to install
them from pip and opam correspondigly:

```bash
$ pip install bap[rpc]
$ opam install bap-server
```

## Installing development version

You can also install directly from github:

```bash
pip install git+git://github.com/BinaryAnalysisPlatform/bap-python.git
````

# Using

```python
>>> import bap
>>> proj = bap.run('/bin/true')
>>> main = proj.program.subs.find('main')
>>> entry = main.blks[0]
>>> next = main.blks.find(entry.jmps[0].target.arg)
```

For more information, read builtin documentation, for example with
`ipython`:

```python
    >>> bap?
```


# Using low-level interface

The low-level interface provides an access to disassembler and image
loader. It uses RPC interface to make calls to the library. So make
sure that you have installed `requests` and `bap-server` (see
Installation section).


```python
    >>> import bap
    >>> print '\n'.join(insn.asm for insn in bap.disasm(b"\x48\x83\xec\x08"))
        decl    %eax
        subl    $0x8, %esp
```

A more complex example:

```python
    >>> img = bap.image('coreutils_O0_ls')
    >>> sym = img.get_symbol('main')
    >>> print '\n'.join(insn.asm for insn in bap.disasm(sym))
        push    {r11, lr}
        add     r11, sp, #0x4
        sub     sp, sp, #0xc8
        ... <snip> ...
```
