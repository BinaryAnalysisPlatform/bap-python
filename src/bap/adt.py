#!/usr/bin/env python
"""Algebraic Data Types for Python.

Algebraic Data Types is not an attempt to add a strict typing
discipline to Python, and the word ``type'' here has a much broader
meaning. Types represent models of reasoning about objects. This
models we, humans, employ everyday (at least those of us, who do the
thinking). These are just methods (among others) that we're using to
structure our knowledge. For example, we can say, that both
``Bananas`` and ``Apples`` are ``Fruits`` (biologists, please stop
reading at this point). With this phrase we constructively defined a
new type (concept, idea), that we named the ``Fruit``. To contrast
with abstraction, we didn't try to find anything common between these
two entities, and to remove the differences, we just stated, that the
Fruit is either Banana or Apple. No more, no less. We just used an
alteration to define something. Another example of the alteration
would be to say, that a human is either a man or woman.

If we will reason about types, as sets, then the alteration can be
viewed as a union. A disjoint union in our case, as we're not loosing
any information (we are not abstracting anything out). The union
operation is isomorphic to the summation in arithmetic, that's why we
call such types - sum types. A dual of the sum is a product. The
product models and idea of a composition, i.e., when an entity is
composed of other entities. For example, a ``Bicycle`` is a
combination of ``Wheels``, ``Frame`` and ``Handlebars``. And a ``Car``
is a combination of ``Wheels``, ``Body``, ``Doors``, and
``Engine``. Again, we described concepts constructively, we didn't try
to make any abstractions. (In fact, we employed an abstraction, when
we made a choice how to represent the compound object, by omitting
parts that are not relevant, with respect to our task. But this is a
completely different modus of reasoning, that is in fact orthogonal to
ADT).

Finally, we can mix both concepts together to model even more complex
ideas. For example, we can define that a ``Vehicle`` is either a
``Car`` or ``Bicycle``. Suppose, that we're trying to model road
traffic. In that case we can tell that we have two kinds of road
users, either a ``Motorist`` that is a combination of a ``Car``,
``Driver``, ``Passengers`` and ``Luggage``, and a ``Bicyclist`` that
is a composition of ``Bicycle`` and the ``Driver``. You may see, that
we apply the sum and product recursively, that's why the ADT types are
also called recursive types. The same way as you can build complex
algebraic expressions using sum and product, we can build complex data
using a combination of sum and product. The whole set of algebraic
data types is a closure of sum and product operations.

We can define such complex concepts as lists, tables, trees and, even,
natural numbers, using only ADT. For example, a list is either Empty,
or it is a Pair of an element and the rest of a List (note that since
the type is recursive, we can use the type in its own definition). For
example, ``[1,2,3]`` can be represented as
``Pair(1,Pair(2,Pair(3,Empty())))``. A Natural number is either Zero
or a Successor of a Natural number, so that we can represent 3 as
``Successor(Successor(Successor(Zero())))``. So, we don't even need
numerals, to represent the list [1,2,3]:

```
Pair(Successor(Zero()),
  Pair(Successor(Successor(Zero())),
    Pair(Successor(Successor(Successor(Zero()))),
      Empty())))
```

You may notice, that these examples are actually syntactically valid
Python code.  So we're now close to the point, where we can define,
how we will represent ADT in Python. It is believed, that Python
doesn't support ADT (at least it is not listed in wikipedia as one of
such languages), but as examples above show, this is not true.

We will use inheritance to represent sum types. For example to say, that
Fruit is Banana or Apple, we do the following:

    class Fruit(ADT): pass
    class Banana(Fruit): pass
    class Apple(Fruit): pass


The product types, aka tuples, are already in the language, so we're
done. We will use the following syntax, to say that a Bicycle is a
product of Wheels, Frame and Handlebars:

    class Bicycle(ADT) : pass
    class Wheels(ADT) : pass
    class Frame(ADT) : pass
    class Handlebars(ADT) : pass

    Bicycle(Wheels(), Frame(), Handlebars())

We're not trying to enforce the type discipline here, by guaranteeing,
that it is only possible to construct a Bicycle only from this three
things. This is Python anyway.

So, it looks like that we didn't introduce anything at all, other than
extra verbose syntax, hidden by some type theoretic mumbo jumbo. Well
yes, but this is only on a surface. The idea behind this library is
that ADT is a great generalization, which we can employ to write code,
that will work for any ADT.

The first generalization, is that we can easily print any ADT in a
unified syntax, and this syntax can be chosen to be a valid subset of
Python syntax. In fact it is also a valid subset of many other
programming languages, such as Ruby, JavaScript, Java, C, OCaml,
Haskell, etc. That also mean, that we can easily parse them back,
especially if the language provides an access to the parser (like
Python). Thus, ADT is a nice data representation format (like json,
xml, S-expressions), that is very suitable for storing hierarchical data.

The second generalization, is that we can employ the same method of
processing ADT. A usual way of processing lists and other iterable
objects, is to apply some operation over every consecutive element of
the list. ADT are more general, than lists (in fact lists a special
case of ADT). ADT are hierarchical, so the elements have also
ancestor/descendant relationships in addition to the
successor/predecessor. Also, every element of an ADT value, is tagged
by a name. And theses names also forms a separate type hierarchy, so
that we have both object and type hierarchies. Given such a general
structure, we need to find a general way of iteration over it. We will
call it visiting. So visiting is a generalization of an iteration,
where the computation is represented by an object called Visitor, that
applies itself to each structural element of the ADT object. The
visitor object has a method for each type of structural component, and
thanks to a unified representation of the ADT type, it knows how to
deconstruct any instance of ADT. So, we generalized a way of
traversing data structure, so that a user of it needs only to specify
the computation, that needs to be applied for each, or some
elements.

We can compare visiting with a regular iteration over some
hierarchical data structures, like compounds of lists and
maps. Suppose, that we're modeling a library, and started with the
following representation:


     Library -> Shelf -> Book -> (Author, Title)

And we wrote a function that will count a total number of distinct authors:

     def count_authors(library):
         authors = set()
         for shelf in library:
             for book in shelf:
                 authors.add(book.author)
         return len(authors)

The code looks fine, but it has one problem, it hardcodes the
structure of our library. If at some point of time we decide, that we
chose a wrong representation and it is much better to represent it as:

    Author -> Title -> Library -> Shelf

Then we need to rewrite our ``count_authors`` function. On the other
hand, with the visitor approach the following code will work with both
representations.


    class AuthorCounter(Visitor):
        def __init__(self):
            self.authors = set()
        def visit_Author(self, author):
            self.authors.add(author)

     def count_authors(library):
        counter = AuthorCounter()
        counter.run(library)
        return len(counter.authors)


This variant is slightly more verbose, but is easier to implement, as
we don't need to know the hierarchical structure of the data, and
anything about the data representation. Moreover, it is easier to
support, as it will not break, when something is added or removed from
the library structure.

The visitor pattern really starts to shine, when the hierarchy is much
more complex, than in the example, that we provided above. For
example, Abstract Syntax Trees (AST) tend to be very complex even for
toy languages, and writing the traversing code for them is very
tedious. Moreover, the code needed to be repeated over and over again,
leading to fragile and hard to support programs.


"""

from collections import Iterable,Sequence,Mapping

class ADT(object):
    """Algebraic Data Type.

    This is a base class for all ADTs. ADT represented by a tuple of
    arguments, stored in a `arg` field. Arguments should be instances
    of ADT class, numbers, strings or lists. Empty set of arguments is
    permitted.  A one-tuple is automatically untupled, i.e., `Int(12)`
    has value `12`, not `(12,)`.  A name of the constructor is stored
    in the `constr` field

    A structural comparison is provided.

    """
    def __init__(self, *args):
        self.constr = self.__class__.__name__
        self.arg = args if len(args) != 1 else args[0]

    def __cmp__(self,other):
        return self.__dict__.__cmp__(other.__dict__)

    def __repr__(self):
        def qstr(x):
            if isinstance(x, (int)):
                return '0x{0:x}'.format(x)
            elif isinstance(x, ADT):
                return str(x)
            elif isinstance(x, tuple):
                return "(" + ", ".join(qstr(i) for i in x) + ")"
            else:
                return '"{0}"'.format(x)
        def args():
            if isinstance(self.arg, tuple):
                return ", ".join(qstr(x) for x in self.arg)
            else:
                return qstr(self.arg)

        return "{0}({1})".format(self.constr, args())


class Visitor(object):
    """ADT Visitor.
    This class helps to perform iterations over arbitrary ADTs.


    When visitor runs, it will visit each constituent of an ADT.
    When an ADT instance is visited, the visitor will first look
    for method named `enter_C` for each class `C` in the MRO of
    the ADT instance. All found methods will be invoked.

    Then it will look for a method called `enter_C` for each class `C`
    in the MRO sequence of the ADT class. If one is found,
    then it will be called, other classes in the MRO sequence will not
    be considered.

    Finally, the visitor will look for a method called `leave_C` using
    the same algorithm as described for the `enter_C` method.

    The algorithm, described above, actually implements the
    depth-first traversal. Methods starting with the prefix `enter`
    are called right before the corresponding subtree is visited
    (preorder).  Methods starting with the `leave` are called just
    after the subtree is visited. Methods starting with `visit`
    actually perform the visiting. If it is not overridden, then
    `visit_ADT` method is invoked, that will continue traversal to the
    subtree. If `visit_C` method is overridden (where `C` is name of
    class in the MRO of the ADT instance), then it is responsibility
    of the `visit_C` method to call `run` method to continue
    traversal. If `run` is not called, then the traversal will not
    continue. It is possible to change the order of traversal, by
    overriding `visit` methods. Usually, it is better to keep away
    from the `visit` methods, and use `enter` (the preorder traversal)
    if possible. However, if it is needed to inject some code between
    the traversal of two subtrees of a tree, or if an order should be
    changed, then the visit method is a way to go.

    By default, every element of an ADT is traversed. It is possible
    to terminate the traversal abnormally (to short-circuit) by
    returning not-a-None value from any of the methods. The returned
    value will be a result of the `run` method.


    Example
    -------

    Suppose we have a small expression language with defined as
    follows:

    >>> class Exp(ADT)   : pass
    >>> class Binop(Exp) : pass
    >>> class Unop(Exp)  : pass
    >>> class Value(Exp) : pass
    >>> class Add(Binop) : pass
    >>> class Mul(Binop) : pass
    >>> class Neg(Unop)  : pass
    >>> class Var(Value) : pass
    >>> class Int(Value) : pass


    We will write an abstract interpreter that will calculate a sign
    of expression. In our abstraction, we now a sign of constants,
    signs of variables are unknown. The negation operation negates the
    sign of expression, and any binary operation preserves the sign,
    if both operands have the same sign, otherwise the sign is
    undefined. We will use the following lattice to represent our
    abstraction:


                          True  False
                            |     |
                            +--+--+
                               |
                              None

    The same expressed in Python:


    >>> class Sign(Visitor) :
            def __init__(self):
                self.neg = None

            def visit_Binop(self,exp):
                self.run(exp.arg[0])
                lhs = self.neg
                self.run(exp.arg[1])
                rhs = self.neg
                if lhs != rhs:
                    self.neg = None

            def leave_Neg(self,exp):
                if self.neg is not None:
                    self.neg = not self.neg

            def enter_Var(self,var):
                self.neg = None

            def enter_Int(self,n):
                self.neg = n < Int(0)

    We overrode method ``visit_Binop`` that will be invoked for both,
    addition and subtraction, since in our abstraction they behave the
    same. We chose to override the ``visit`` stage instead of the
    ``enter`` or leave, because we wanted to inject our code between
    visiting left and right branch of the expression. We overrode
    `leave_Neg` to switch the sign _after_ the enclosed expression is
    visited. Since variable can have arbitrary sign, we're must stop
    the sign analysis as soon as we have a variable. Finally, for constants
    we just look at their sign.


    To test our sign analysis let's write a simple expression,

    >>> exp = Add((Neg(Neg(Int(1)))), Mul(Int(2), Neg(Neg(Int(3)))))

    It is easy to see that it is positive (in fact it is not).  In the
    infix notation, the expression corresponds to


    >>> -(-1) + 2 * -(-3)
    7

    So, let's run the analysis:

    >>> exp = Add((Neg(Neg(Int(1)))), Mul(Int(2), Neg(Neg(Int(3)))))
    >>> ai = Sign()
    >>> ai.run(exp)
    >>> print("exp {0} is {1}".format(exp,
                                      "negative" if ai.neg else
                                      "unknown"  if ai.neg is None else
                                      "positive"))

    For an ADT of type C the method `visit_C` is looked up in the
    visitors methods dictionary. If it doesn't exist, then `visit_B` is
    looked up, where `B` is the base class of `C`. The process continues,
    until the method is found. This is guaranteed to terminate,
    since visit_ADT method is defined.

    Note: Non ADTs will be silently ignored.

    Once the method is found it is called. It is the method's responsiblity
    to recurse into sub-elements, e.g., call run method.

    For example, suppose that we want to count negative values in
    some BIL expression:

    class CountNegatives(Visitor):
        def __init__(self):
            self.neg = False
            self.count = 0

        def visit_Int(self, int):
            if int.arg < 0 and not self.neg \
              or int.arg > 0 and self.neg:
                self.count += 1

        def visit_NEG(self, op):
            was = self.neg
            self.neg = not was
            self.run(op.arg)
            self.neg = was

    We need to keep track on the unary negation operator, and, of
    course, we need to look for immediates, so we override two methods:
    visit_Int for Int constructor and visit_NEG for counting unary minuses.
    (Actually we should count for bitwise NOT operation also, since it will
    change the sign bit also, but lets forget about it for the matter of the
    exercise (and it can be easily fixed just by matching visit_UnOp)).

    When we hit visit_NEG we toggle current sign, storing its previous value
    and recurse into the operand. After we return from the recursion, we restore
    the sign.

    """

    def visit_ADT(self, adt):
        """Default visitor.

        This method will be called for those data types that has
        no specific visitors. It will recursively descent into all
        ADT values.
        """
        if isinstance(adt.arg, tuple):
            return self.__induct(adt.arg)
        elif isinstance(adt.arg, ADT):
            return self.run(adt.arg)

    def __induct(self, xs):
        return next((r for r in (self.run(x) for x in xs) if r), None)

    def visit_Seq(self,adt):
        """Deconstructs sequences"""
        return self.__induct(adt.arg[0])

    def visit_Map(self,adt):
        """Deconstructs maps"""
        return self.__induct(adt.arg[0])


    def run(self, adt):
        """visitor.run(adt) -> result

        """
        if isinstance(adt, ADT):

            for meth in ("enter", "visit", "leave"):
                for cls in adt.__class__.mro():
                    name = "{0}_{1}".format(meth, cls.__name__)
                    fn = getattr(self, name, None)
                    if fn is not None:
                        r = fn(adt)
                        if r is not None:
                            return r
                        if meth == "visit":
                            break

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

        If a key is a number, or an instance of `bil.Int' class or is
        an integer, then a term with a matching address is returned.

        Example
        -------

        In the following example, all searches return the
        same object


        >>> main = proj.program.subs.find('main')
        >>> main = proj.program.subs.find(main.id)
        >>> main = proj.program.subs.find(main.id.name)

        """
        def by_id(t, k) : return t.id.number == k
        def by_name(t,k) :
            if k.startswith(('@','%')):
                return t.id.name == k
            else:
                return hasattr(t, 'name') and t.name == k
        def by_addr(t,k) :
            value = t.attrs.get('address', None)
            if value is not None:
                return parse_addr(value) == key

        test = by_addr
        if isinstance(key,str):
            test = by_name
        elif hasattr(key,'constr') and key.constr == 'Tid':
            key = key.number
            test = by_id
        elif hasattr(key,'constr') and key.constr == 'Int':
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


def visit(visitor, adt):

    if isinstance(adt, Iterable):
        for x in adt:
            visitor.run(x)
    else:
        visitor.run(adt)
    return visitor




if __name__ == "__main__":
    class Fruit(ADT) : pass
    class Bannana(Fruit) : pass
    class Apple(Fruit) : pass

    assert(Bannana() == Bannana())
    assert(Bannana() != Apple())
    assert(  Apple() <  Bannana())
