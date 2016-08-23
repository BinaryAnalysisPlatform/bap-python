# Installing
BAP python bindings

And if you're interested in python bindings, then you can install them using pip:

```bash
$ pip install git+git://github.com/BinaryAnalysisPlatform/bap-python.git
```


# Using

After BAP and python bindings are properly installed, you can start to
use it:

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

For more information, read builtin documentation, for example with
`ipython`:

```python
    >>> bap?
```

Currently, only disassembler and lifter are exposed via python interface.
