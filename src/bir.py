#!/usr/bin/env python

"""BIR - BAP Intermediate Representation"""

from collections import Sequence,Mapping
from adt import *
from bil import *


class Project(ADT) :
    """A collection of data associated with a disassembled program"""
    @property
    def attrs(self) :
        """A dictionary of attributes that are global to a project.

        Example:
        >>> file = proj.attrs['filename']
        """
        return self.arg[0]

    @property
    def sections(self) :
        """code and data sections of a file.

        Often a binary is split into several named sections.  This is
        the mapping from names (that varies by particular, underlying
        file format, and data, that represents the section)

        Example:

        >>> code = proj.sections['.text']
        """
        return self.arg[1]

    @property
    def memmap(self) :
        """a mapping from memory regions to arbitrary attributes.

        Some facts may be discovered about a particular memory region
        and attributed to it.
        """
        return self.arg[2]

    @property
    def program(self) :
        """a program in BAP Intermediate Representation (BIR)"""
        return self.arg[3]

class Term(ADT) :
    """Term(id,attrs,...) a program term.

    Every term has a dictionary of attributes, associated with it, and
    a unique term identifier.
    """
    @property
    def id(self) :
        "term.id() -> Tid(id,name)"
        return self.arg[0]

    @property
    def attrs(self) : return self.arg[1]

class Program(Term) :
    """Program(id,attrs,Subs(s1,s2,..,sN))
     A program is a term that contains a set of subroutines."""

    @property
    def subs(self) : return self.arg[2]

class Sub(Term) :
    """Sub(id,Attrs(...),name,Args(...),Blks(...))
    A subroutine has a sequence of arguments and basic blocks
    """

    @property
    def name(self) :
        "subroutine name"
        return self.arg[2]

    @property
    def args(self) :
        "a list of subroutine arguments"
        return self.arg[3]

    @property
    def blks(self) :
        "subroutine basic blocks, the first is the entry"
        return self.arg[4]

class Arg(Term) :
    """Arg(id,attrs,lhs,rhs,intent=None) - a subroutine argument"""

    @property
    def var(self) :
        """a variable associated with the argument, e.g.,

        >>> main = proj.subs.find('main')
        >>> main.args[0].var.name
        'main_argc'

        """
        return self.arg[2]

    @property
    def exp(self) :
        "a BIL expression associated with the argument"
        return self.arg[3]

    @property
    def intent(self) :
        "an instance of Intent class or None if unknown"
        None if len(self.arg) == 4 else self.arg[4]

class Blk(Term) :
    """Blk(id,attrs,(p1,..,pL),(d1,..,dM),(j1,..,jN))
       A basic block is a sequence of phi-nodes, defintions and jumps.
    """
    @property
    def phis(self) :
        "phi-nodes"
        return self.arg[2]
    @property
    def defs(self) :
        "definitions"
        return self.arg[3]
    @property
    def jmps(self) :
        "jumps"
        return self.arg[4]

class Def(Term) :
    "Def(id,attrs,Var(lhs),Exp(rhs)) assign rhs to lhs"
    @property
    def lhs(self) :
        "an assigned variable"
        return self.arg[2]
    @property
    def rhs(self) :
        "value expression"
        return self.arg[3]


class Jmp(Term) :
    "Jmp(id,attrs,cond,target) base class for jump terms"
    @property
    def cond(self) :
        "guard condition"
        return self.arg[2]

    @property
    def target(self) :
        "jump target"
        return self.arg[3]

class Goto(Jmp) :
    "Goto(id,attrs,cond,target) control flow local to a subroutine"
    pass

class Call(Jmp) :
    """Call(id,attrs,(calee,returns))
    a transfer of control flow to another subroutine"""

    @property
    def calee(self) :
        "call destination"
        return self.target[0]

    @property
    def returns(self) :
        "a basic block to which a call will return if ever"
        return self.target[1] if len(self.target[1]) == 2 else None

class Ret(Jmp)  :
    "Ret(id,attrs,label) - return from a call"
    pass

class Exn(Jmp)  :
    "Exn(id,attrs,(number,next)) - CPU exception"
    @property
    def number(self) :
        "exception number"
        return self.target[0]

    @property
    def next(self) :
        """next instruction to be executed after the
        exception handler finishes"""
        return self.target[1]

class Label(ADT) : pass

class Direct(Label) :
    "Direct(tid) a statically known target of a jump"
    pass

class Indirect(Label) :
    "Indirect(exp) indirect jump that is computed at runtime"
    pass

class Intent(ADT) :
    "argument intention"
    pass
class In(Intent) :
    "input argument"
    pass
class Out(Intent) :
    "output argument"
    pass
class Both(Intent) :
    "input/output argument"
    pass

class Phi(Term) :
    """Phi(id,attrs,lhs,Values(b1,..,bM))) a term whose value
    depends on chosen control flow path"""
    @property
    def lhs(self) :
        "defined variable"
        return self.arg[2]

    @property
    def value(self) :
        """a mapping from the tid of the preceeding block to
        an expression that defines a value of phi-node"""
        return self.arg[3]

class Def(Term) :
    "Def(id,attrs,lhs,rhs) - assignment"
    @property
    def lhs(self) :
        "program variable to be assigned"
        return self.arg[2]

    @property
    def rhs(self) :
        "value expression"
        return self.arg[3]

class Seq(ADT,Sequence) :
    def __init__(self, *args) :
        super(Seq,self).__init__(args)
        self.elements = args[0]

    def __getitem__(self,i) :
        return self.elements.__getitem__(i)

    def __len__(self) :
        return self.elements.__len__()

    def find(self,key, d=None) :
        """find(key[, d=None]) -> t

        Looks up for a term that matches with a given key.

        If the key is a string, starting with `@' or `%', then a term
        with the given identifier name is returned.  Otherwise a term
        with a matching `name' attribute is returned (useful to find
        subroutines).

        If a key is an instance of Tid class, then a term with
        corresponding tid is returned.

        If a key is a number, or an instance of `bil.Int' class, then
        a term with a matching address is returned.

        Example
        -------

        In the following example, all searches return the
        same object


        >>> main = proj.program.subs.find('main')
        >>> main = proj.program.subs.find(main.id)
        >>> main = proj.program.subs.find(main.id.name)
        """
        def by_id(t,key) : return t.id == key
        def by_name(t,key) :
            if key.startswith(('@','%')):
                return t.id.name == key
            else:
                return hasattr(t,'name') and t.name == key
        def by_addr(t,key) :
            value = t.attrs.get('address', None)
            if value is not None:
                return parse_addr(value) == key

        test = by_addr
        if isinstance(key,str):
            test = by_name
        elif isinstance(key,Tid):
            test = by_id
        elif isinstance(key,Int):
            key = key.value
            test = by_addr

        for t in self :
            if test(t,key) : return t
        return d


class Map(ADT,Mapping) :
    def __init__(self, *args) :
        super(Map,self).__init__(args)
        self.elements = dict((x.arg[0],x.arg[1]) for x in args[0])

    def __getitem__(self,i) :
        return self.elements.__getitem__(i)

    def __len__(self) :
        return self.elements.__len__()

    def __iter__(self) :
        return self.elements.__iter__()

class Attrs(Map) :
    "A mapping from attribute names to attribute values"
    pass

class Attr(ADT) :
    """Attribute is a pair of attribute name and value,
    both represented with str"""
    pass

class Values(Map) :
    """A set of possible values, taken by a phi-node.

    It is a mapping from the tid of a preceeding block,
    to an expression that denotes a value.
    """
    pass

class Tid(ADT) :
    """Tid(id,name=None) term unique identifier.

    name is an optional human readable identifier, that
    doesn't affect the identity.

    """

    def __init__(self,*args):
        super(Tid,self).__init__(*args)
        noname = not isinstance(self.arg, tuple)
        self.number = self.arg if noname else self.arg[0]
        self.name = None if noname else self.arg[1]

    def __cmp__(self, other):
        return cmp(self.number, other.number)

    def __hash__(self):
        return hash(self.number)

class Subs(Seq) :
    "a set of subroutines"
    pass

class Args(Seq) :
    "sequence of arguments"
    pass
class Blks(Seq) :
    "sequence of basic blocks"
    pass
class Phis(Seq) :
    "sequence of phi-nodes"
    pass
class Defs(Seq) :
    "sequence of definitions"
    pass
class Jmps(Seq) :
    "sequence of jump terms"
    pass

class Memmap(Seq) :
    "sequence of memory annotations "
    pass

class Region(ADT) :
    "Region(beg,end) a pair of addresses, that denote a memory region"
    @property
    def beg(self) : return self.arg[0]

    @property
    def end(self) : return self.arg[1]

class Section(ADT,Sequence) :
    """A contiguous piece of memory in a process image"""

    @property
    def name(self) :
        "name associated with the section"
        return self.arg[0]

    @property
    def beg(self) :
        "starting address"
        return self.arg[1]

    @property
    def data(self) :
        "an array of bytes"
        return self.arg[2]

    @property
    def end(self) :
        "an address of last byte"
        return beg + len(self.data)

    def __getitem__(self,i) :
        return self.data.__getitem__(i)

    def __len__(self) :
        return self.data.__len__()

class Sections(ADT,Mapping) :
    " a mapping from names to sections"
    def __init__(self, *args):
        super(Sections, self).__init__(args)
        self.elements = dict((x.name,x) for x in args[0])

    def __getitem__(self,i) :
        return self.elements.__getitem__(i)

    def __len__(self) :
        return self.elements.__len__()

    def __iter__(self) :
        return self.elements.__iter__()

class Annotation(ADT) :
    """Annotation(Region(beg,end), Attr(name,value))

    Each annotation denotes an association between a memory region and
    some arbitrary property, denoted with an attribute.
    """
    pass

def parse_addr(str):
    return int(str.split(':')[0],16)

def loads(s):
    "loads bir object from string"
    return eval(s)
