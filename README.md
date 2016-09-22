BAP python bindings

# Installing

Install python bindings with pip (after you installed `bap`):

```bash
$ pip install bap
```

Alternatively you can just copy paste files into your project, or clone it
with git-subtree, or whatever...


## Installing low-level bindings

An optional low-level interface, called [rpc] depends on requests, so
install [requests] package from pip and `bap-server` from opam:

```bash
$ pip install bap[rpc]
$ opam install bap
```

## Installing development version

You can also install directly from github:

```bash
pip install git+git://github.com/BinaryAnalysisPlatform/bap-python.git
````

# Using

```python
>>> import bap
>>> proj = bap.run('/bin/true', ['--symbolizer=ida'])
>>> text = proj.sections['.text']
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
    >>> print '\n'.join(insn.asm for insn in bap.disasm("\x48\x83\xec\x08"))
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
