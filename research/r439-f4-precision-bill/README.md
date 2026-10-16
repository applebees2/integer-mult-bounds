# F4 target feedback: completed scalar-envelope bill

**Independent corroboration; no new kappa.** This reproduces the exact scalar
bill already reported by **Wentao Li / closed PR1820** and adds a dense integer
coefficient-row cross-check against actual native records. No priority for
these numbers or a new pricing claim is asserted. The F4 word introduced by Aaron Wang in
PR1782 and admitted under a proposed weaker framed contract by geckods in
[PR2721](https://github.com/CrocSwap/integer-mult-bounds/pull/2721) fits the
retained local and nine-stage scalar precision guards. Its identical Boolean
endpoint does not preserve its positive integer envelope.

| Complete word | ADDs | COPY / ERASE | forward F | reverse B | local bits | nine-stage bits |
|---|---:|---:|---:|---:|---:|---:|
| PR589 baseline | 24,305 | 9 / 9 | 49,347 | 1,113,070 | 93 | 177 |
| F4 target feedback | 24,374 | 9 / 9 | 50,535 | 2,995,586 | 96 | 183 |

The inherited expressions are `64 F^3 B^2 < 2^104` and
`2^18 F^5 B^4 < 2^192`. Strict comparisons and both retained numerators use
integers. F4 costs **69 added ADDs**. Both words have byte-equal emitted MOVE
itineraries and COPY/ERASE records, paid profile
`{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}`, and rank mass 5,129.

## Object and checks

Helper 277 borrows target 221 before D. Each of the 67 earlier D rows reading
helper 277 also reads target 221. The helper is restored immediately before
D's final gate, the sole write to target 221. This is the existing fixed F4
instance, not an optimization or search.

The checker reconstructs F4 without importing the predecessor verifier. It
checks all **661 basis columns** through the complete literal program in both
directions: `y ^= x`, all sources/helpers restored, one initially clean COPY
temporary erased. Linearity covers arbitrary Boolean dirt for this word.
Two representations compute every positive prefix:

- Dense nonnegative integer coefficient rows, initialized to all basis vectors;
  every intermediate row sum is inspected. Nonnegativity makes the row sum
  exactly its all-ones positive-envelope value, rather than a sampled bound.
- The unchanged Dylan Crow exporter emits native six-integer records. A
  separate scalar-bound interpreter prices them in both directions, including
  COPY and ERASE. Both peaks agree exactly with the dense-row method.

The actual records also supply the frame itinerary and complete recursive
rank profile. No helper preparation, source read, restoration or child is
removed from the bill. Baseline MOVE/COPY geometry is inherited, with byte
identity checked here; no new physical realization theorem is claimed.
Five controls reject: late restoration, omitted restoration, omitted native
ERASE, and equality at either strict bit cap. The integers just below the caps
pass. The chronological controls corroborate predecessor observations.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python -I -B research/r439-f4-precision-bill/verify.py
```

Expected, about four seconds on the measured Windows host:

```text
PASS_R439_F4_PRECISION_BILL ADDs=24305->24374 bits=93/177->96/183 controls=5 no_new_kappa
```

`-O` is supported; `--out PATH` writes a fresh report after comparison with
`CERTIFICATE.json`. Missing certificates fail. Source hashes precede decompression
and exporter execution. Temporary exports are removed normally. Registered replay:
`python -B scripts/research_package.py --package research/r439-f4-precision-bill`.

## Scope and provenance

Base `4bb3629e638edc9d70ea124eb50f80e71433be05`, priority revision 5;
chooser nonce `97149c0712331b6eb35989b9ca86cd6c`, bit-mechanisms.
Scope **changed** from searching for an H2/K lemma to closing one explicit
precision obligation of an existing proposed replacement. TASK.json records
the original card and stopping rule; SOURCES.json pins every external input.

Three candidates: a generic semantic-D bridge (covered by PR1194/2556), the
205-pair helper-only bill (covered by PR2191), and this F4 bill. PR2721 at
`6b14e212a1aba401d29f2bf7378e745ee2aed7f2` explicitly leaves its F/B bounds,
guards and profile uncomputed. Its theorem remains **pending**; this invoice
does not assume or verify it. F4's formula already appears in the pinned
merged PR1782 verifier/certificate. PR1062 supplies the tariff machinery;
PR2567 optimizes a different bounded target-feedback domain.
The final closed-PR check found **PR1820**, whose README at
`ff27b7175c6b5cf83346b3321bb15abb4217ff44` already reports every bill value
in this table. That package was deferred as a freestanding claim. This package
is therefore supplementary independent evidence, intended for a pointer on
PR2721 rather than a duplicate contribution PR.

The local overlap helper lacked live GitHub CLI coverage. Targeted live PR
body searches and Discussion2684 were checked instead. This is not a novelty
certificate. The donor requested publication only after completion.

The bit supplier is nonbinding. No saving, supplier adoption or new kappa is
established. C++ 5/9/11-stage engines, hosted invoice, physical streams, tape
implementation and outer assembly were not replayed. All-size/compiler,
ownership/routing, exact-recovery and analytic obligations remain inherited.
Matching a scalar guard does not implement a tape algorithm. Selected and frozen
predecessor files are unchanged.

## Open next questions

Could a cheaper target-feedback word satisfy the proposed framed contract and
these complete guards? First supply one pinned saving word and its actual
consumer contract, then apply this bill before native/hosting work. Those are
the blockers. The present +69 control removes a particular precision objection
but supplies no reason to expand an optimization campaign.

## Attribution

Prepared for **applebees2** with substantial **OpenAI Codex assistance**.
Credit **Wentao Li / PR1820** (the already reported complete F4 bill),
**Aaron Wang / PR1782** (F4), **Abhinav Ramachandran / geckods / PR2721**
(proposed framed relaxation), **woklerx / PR1194** (semantic substitution),
**Sagar Thakrar / PR1062** (precision-billing pattern), **Dylan Crow** (unchanged
exporter), **DreamingOfClouds / PR589**, **eumemic / PR555**, and the retained
bit-interface lineage. Original notices remain intact. New work: Apache-2.0.
No independent human review, hosted CI success or full-theorem proof is claimed.
