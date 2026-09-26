# Expand a construction into a statement

September 25, 2026 · Experimental integer translation; optional solver adapter

After a finite comparison, **Expand construction** exposes the arithmetic that
produced the selected fields. Choose which named parameters vary over integers,
write assumptions, and optionally declare pairs coprime. The independent key
domain stays part of the conclusion. Geometry and motion remain inspectable in
the original capture, but are not part of this integer equality claim.

## Try the quotient construction

1. Open **Two quotient fields make one**. Select **Moving cover → Details →
   More tools → Compare exact fields**.
2. Compare its `value` with **Independent ones**. Choose `i`, then `j`, as the
   keys of both operands and the independent expected domain. Compare captured
   values. All 24 keys agree at `a=7, b=5`.
3. Open **Expand construction**, vary `a` and `b`, and enter
   `a > 1 and b > 1`. Add the coprime pair `a`, `b`. Press **Expand statement**.
4. Read the two indicators and their exact integer rectangle. Open
   **Construction obligations** to see extent and keyed-read requirements.
5. **Save this comparison** keeps the choices, assumptions, definitions, exact
   case, evidence, history and view. Open rechecks the captured values; press
   **Expand statement** to derive the algebra again. No saved verdict is trusted.
6. Change the case to `a=6, b=4`, compare and expand with the same assumptions.
   The overlap at key `(1,2)` fails finite equality, but this case violates the
   declared coprimality assumption. It does not refute the conditional claim.
   Remove the coprime assumption to investigate a stronger claim that this case
   can refute. Neither choice changes the captured construction.

In conventional notation, the generated pointwise equation is

\[
[b(j+1)\le a(i+1)]+[a(i+1)\le b(j+1)]=1,
\qquad 0\le i<b-1,\quad 0\le j<a-1.
\]

Here `[P]` denotes the integer indicator of predicate P. The view calls the
declared key components `k[0]`, `k[1]`; these are bound integer coordinates,
distinct from named parameters. Both domains were constructed independently,
and the second incidence deliberately has reversed storage order. The translator
follows the declared keys, rather than pairing array positions.

Compare **Counted area** with **Rectangle area** by `key` to obtain the bounded
double sum on each side. The translator retains summation bounds and the
singleton total's domain. It does not invent a floor-sum rewrite or a gcd lemma.
The mathematical argument for those steps remains in the
[quotient investigation](QUOTIENT_EQUALITY.md).

For a transfer test, open **A box of ones**, compare **Cell
owners** with **One per cell** by `i,j,k`, and expand the three indicators with
`a,b,c` varied. Pairwise coprimality means three separate pair assumptions; it is
stronger than `gcd(a,b,c)=1`. This uses the same controls and translation rules.

## Three kinds of condition

| Information | Meaning | Who supplies it? |
| --- | --- | --- |
| Integer parameter domains and fixed bindings | Only selected global parameters vary; all other bindings/literals stay fixed | Author choices and captured definitions |
| Author hypotheses | Restrictions such as `a > 1`, `b > 1`, `gcd(a,b)=1` | Author; never inferred from one successful example |
| Construction obligations | Nonnegative extents, positive moduli, nonzero floor divisors, singleton scalar reads, complete keyed reads, recorded `require` checks | Translation rules; these are goals to establish under the hypotheses |
| Finite evidence | Current field comparison and current-case satisfaction of the displayed conditions | Captures and a bounded interpreter of statement conditions |

The intended proof task is: **for every varied integer parameter satisfying the
author hypotheses, establish the construction obligations, exact key coverage,
and equality of the selected fields.** Obligations are not silently appended to
the assumptions. A failed obligation, an inconsistent hypothesis, an unsupported
operation, or a solver timeout must never become a proof badge.

The conclusion includes `dom(L) = dom(R) = D`. This preserves missing-both keys
even when both displayed fields agree wherever they exist. Empty domains allow
vacuous pointwise equality, but a total reduction still has one occurrence with
value zero. Counting native-axis fibers preserves zero groups when an eliminated
axis is empty. Reducing an already reduced collection by an observed field has a
different coverage policy and currently stops expansion.

## Supported projection and explicit limits

| Construction | Translation |
| --- | --- |
| Grid, tuple grid, sequence | Finite integer coordinate ranges, row-major ordinal, declared value expression |
| Literal integer table | Fixed table with its exact entries; never inferred as a formula or variable-sized family |
| Values, annotation | Field substitution; annotation expressions all see the original source |
| Scoped parameter cases | Simultaneous outer-scope bindings, then a distinct child environment |
| Incidence | Typed Boolean predicate |
| Count, weighted sum, any | Indicator/summand and bounded sums, with native retained axes or an explicit singleton total |
| Keyed read | Source-coordinate bijection plus requested-key coverage obligations; retained key order is explicit |
| Scalar read | Singleton arity obligation, then source field substitution |
| Recorded requirement | Predicate over its full check domain becomes an obligation |
| Arrange, move, explicit positions | Documented projection onto integer fields/domain only; geometry is excluded |

The expression fragment supports integer `+`, `-`, `*`, `//`, `%`, unary minus,
absolute value, comparisons and Boolean operations. `//` is floor division,
including negative divisors. `%` requires a **positive** integer modulus and
least nonnegative residues. Shape matters: a scalar zero divisor is invalid even
when the receiving arrangement is empty; an empty divisor column has no entries
to validate. Reduction weights are checked over the original source, including
nonmatching occurrences. Simplifying `0*x` never discards these obligations.

Gather, Roll, Tile, arbitrary key inversion, observed grouping, Prefix/Rank,
recurrences, incidence Boolean nodes, floating operations, powers, and geometry
reads are not translated yet. Failure names the source operation/node. The
finite question and all original evidence remain usable. Literal tables with
non-coordinate keys need a future explicit dictionary-domain rule. Some integer
fields with irrelevant unsupported sibling expressions also stop conservatively.

This is a mathematical integer projection, not an executability claim for every
parameter on a particular host: item/bit/render budgets and geometry validity are
outside it. Translation has separate node/expression/nesting bounds; finite
condition inspection has a work budget and reports unavailability explicitly.
An expanded-term budget also catches exponential duplication in a small shared
graph before printing or hashing it. Named shared subexpressions are a future
extension; the current adapter reports this limit explicitly.
The translator and its few unconditional arithmetic folds are currently trusted
code, supported by finite regression cases, not a formally verified compiler.

## Module ownership and compatibility

| Owner | Changeable decision |
| --- | --- |
| `examples/statements/terms.py` | Typed neutral terms, exact serialization, notation, bounded finite interpretation |
| `examples/statements/expansion.py` | Meaning of supported graph-to-field/domain projections, lexical scope, obligations |
| `examples/studio/statements.py` | Comparison request, author assumptions, source identities, statement fingerprint |
| `web/statement.js` | Parameter/assumption controls and progressive disclosure |
| Existing comparison/evidence/history modules | Finite key comparison, contributor references, captured restoration |
| `examples/statements/solver.py` | Optional Z3 lowering, named arithmetic rules, explicit goals, budgets, result taxonomy and exact model replay |
| Future checked-proof adapters | Proof source/certificates, permitted axioms and independent checker versions |

These are experimental authoring adapters, not new core operations or an
arrangement superclass. Numerical evaluation and replay do not import them.
The translation cache includes the node **and its lexical environment**. Source
IDs, domains, assumptions, exact fixed values, statement semantics and translator
version contribute to a reproducible fingerprint. It is an identity for a future
proof request, not a signature or proof certificate; changing even a varied
parameter's captured case produces a different request identity.

The `kaleion-comparison` envelope remains version 1. Its question is version 1
without expansion, or version 2 with validated `expansion` choices and the
`kaleion-integer-projection/1` translator identifier. Version-1 questions remain
readable. Old readers reject version-2 questions. A different translator version
needs an explicit migration rather than silently retaining a claim. Saved
questions contain no proof status or trusted expanded text. The typed expression
tree is returned by the Python adapter and regenerated from the captured graph.
Workspace schemas and their original JSON bytes are unchanged.

## Programmatic entry point

From the repository's activated virtual environment:

```python
from examples.quotient_equality import quotient_equality
from examples.statements import Expansion
from examples.statements.terms import domain_text, render

workspace = quotient_equality()
expansion = Expansion(workspace.state.parameters, vary=("a", "b"))
domain, value = expansion.keyed(
    workspace.state.roots["Moving cover"], ("i", "j"), "value"
)
print(domain_text(domain))
print(render(value))
```

`examples.studio.statements.comparison_statement` adds both operands, independent
domain, hypotheses and fingerprint. It returns a JSON-safe typed report; integer
literals are strings. Neither entry point runs a prover. The optional
[proof-assistance adapter](PROOF_ASSISTANCE.md) consumes that report without
changing the construction or saved comparison.

The solver adapter recognizes one deliberately narrow number-theory hypothesis:
`gcd(x,y)=1`. It records `bezout-coprime/1` and introduces hidden integer
coefficients for Bézout's identity. When the goal domain is exactly the open
rectangle `0 <= i < y-1`, `0 <= j < x-1`, it may also record
`coprime-interior/1`, excluding `x(i+1)=y(j+1)`. A rectangle including the far
corner does not match and yields a replayable counterexample. General gcd values,
bounded sums and division remain unsupported by this backend.
