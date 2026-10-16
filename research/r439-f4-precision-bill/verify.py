#!/usr/bin/env python3
"""Exact completed F4 scalar-envelope bill; no supplier or kappa claim.

Apache-2.0. Prepared for applebees2 with substantial OpenAI Codex assistance.
F4 construction: Aaron Wang / PR1782 and geckods / PR2721. Exporter: Dylan Crow.
"""
import argparse
from collections import Counter
import copy
import gzip
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
EXPORTER = 'research/e8-bit-carrier-skeleton/code/bit/export_records.py'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def build(word, late=False):
    """Literal F4: helper 277 borrows target 221 until just before D gate 110."""
    helper, target, cut = 277, 221, 110
    need(len(word['D']) == 111 and word['D'][-1][1] == target, 'F4 instance moved')
    need(all(g[0] == 0 for g in word['D']), 'D not at frame zero')
    need(sum(g[1] == target for g in word['D']) == 1, 'target is not constant during wrap')
    need(word['start'][helper] == word['start'][target] == 0, 'nonzero entrance')
    body = copy.deepcopy(word['D'])
    changed = 0
    for i, gate in enumerate(body):
        if i < cut and helper in gate[2]:
            need(target not in gate[2], 'compensation already present')
            gate[2] = sorted(gate[2] + [target])
            changed += 1
    need(changed == 67, 'F4 compensation domain moved')
    feed = [0, helper, [target]]
    result = copy.deepcopy(word)
    result['D'] = [feed] + (body + [feed] if late else body[:cut] + [feed] + body[cut:])
    return result


def operations(word):
    ops = [('add', d, s) for sec in ('D', 'A') for _, d, ss in word[sec] for s in ss]
    temp = 2 * word['v'] + word['R']
    for j, centre in enumerate(word['ret']):
        ops.append(('copy', temp, centre))
        ops += [('add', word['v'] + i, temp) for i, ss in enumerate(word['scatter']) if j in ss]
        ops.append(('erase', temp, centre))
    ops += [('add', d, s) for sec in ('B', 'C') for _, d, ss in word[sec] for s in ss]
    return ops


def oriented(ops, reverse):
    for kind, dst, src in (reversed(ops) if reverse else ops):
        if reverse:
            kind = {'add': 'add', 'copy': 'erase', 'erase': 'copy'}[kind]
        yield kind, dst, src


def replay(word, reverse=False, dense=False):
    """Packed GF2 rows check arbitrary dirt; dense nonnegative rows price every prefix."""
    n = 2 * word['v'] + word['R']
    if dense:
        rows = [[int(i == j) for j in range(n)] for i in range(n)] + [[0] * n]
    else:
        rows = [1 << i for i in range(n)] + [0]
    peak = 1
    for kind, dst, src in oriented(operations(word), reverse):
        if kind == 'add':
            rows[dst] = ([a + b for a, b in zip(rows[dst], rows[src], strict=True)]
                         if dense else rows[dst] ^ rows[src])
        elif kind == 'copy':
            need(not any(rows[dst]) if dense else rows[dst] == 0, 'copy into occupied temp')
            rows[dst] = list(rows[src]) if dense else rows[src]
        else:
            # Positive majorants do not cancel; equality is a GF2 semantic obligation only.
            if not dense:
                need(rows[dst] == rows[src], 'erase does not restore copy')
            rows[dst] = [0] * n if dense else 0
        if dense:
            peak = max(peak, sum(rows[dst]))
    need(not any(rows[-1]) if dense else rows[-1] == 0, 'live final temporary')
    if not dense:
        expected = [(1 << i) ^ (1 << (i-word['v'])) if word['v'] <= i < 2*word['v']
                    else 1 << i for i in range(n)]
        need(rows[:-1] == expected, 'arbitrary-dirty boundary mismatch')
    return peak


def export(word, directory):
    directory.mkdir()
    path = directory / 'word.json.gz'
    path.write_bytes(gzip.compress(canonical(word), mtime=0))
    proc = subprocess.run([sys.executable, '-I', '-B', str(ROOT/EXPORTER), str(path), str(directory/'rec')],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    need(proc.returncode == 0, 'export failed: '+proc.stderr.decode(errors='replace'))
    raw = (directory/'rec/249-records.bin').read_bytes()
    need(len(raw) % 24 == 0, 'record alignment')
    return list(struct.iter_unpack('<6i', raw)), hashlib.sha256(raw).hexdigest()


def record_bill(records, n):
    """Independent record interpretation: scalar bounds, not dense matrices."""
    peaks = []
    for reverse in (False, True):
        bounds = [1] * n + [0]
        peak, live = 1, False
        for op, a, b, c, _, _ in (reversed(records) if reverse else records):
            if op == 0:
                continue
            if reverse and op in (2, 3):
                op = 5 - op
            if op == 1:
                need(c == 1, 'unexpected scalar coefficient')
                bounds[a] += bounds[b]
                peak = max(peak, bounds[a])
            elif op == 2:
                need(not live and bounds[b] == 0, 'occupied native COPY')
                bounds[b], live = bounds[a], True
            elif op == 3:
                need(live, 'native ERASE without COPY')
                bounds[b], live = 0, False
            else:
                raise ValueError('unknown native opcode')
        need(not live, 'unclosed native COPY')
        peaks.append(peak)
    F, B = peaks
    local, nine = 64 * F**3 * B**2, (1 << 18) * F**5 * B**4
    need(local < (1 << 104) and nine < (1 << 192), 'precision guard fails')
    counts = Counter(r[0] for r in records)
    return dict(F=F, B=B, ADDs=counts[1], COPYs=counts[2], ERASEs=counts[3],
                local_numerator=local, nine_stage_numerator=nine,
                local_bits=local.bit_length(), nine_stage_bits=nine.bit_length())


def run():
    for entry in json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))['files']:
        if entry['usage'] == 'input':
            need(hashlib.sha256((ROOT/entry['path']).read_bytes()).hexdigest() == entry['sha256'],
                 'source pin mismatch: '+entry['path'])
    word = json.loads(gzip.decompress((ROOT/WORD).read_bytes()))
    feed = build(word)
    cert = json.loads((ROOT/'research/r439-copyshare-h2sem-admission/CERTIFICATE.json').read_text(encoding='utf-8'))
    need(sum(len(g[2]) for g in feed['D']) == cert['f4_target_feed_probe']['d_source_reads'] == 18154,
         'predecessor F4 source-read mismatch')
    result, all_records = {}, {}
    n = 2 * word['v'] + word['R']
    with tempfile.TemporaryDirectory(prefix='r439-f4-invoice-') as tmp:
        for name, instance in [('baseline', word), ('F4', feed)]:
            for rev in (False, True):
                replay(instance, rev)
            records, digest = export(instance, Path(tmp)/name)
            bill = record_bill(records, n)
            dense = [replay(instance, rev, dense=True) for rev in (False, True)]
            need(dense == [bill['F'], bill['B']], 'dense/record bound disagreement')
            bill['records_sha256'] = digest
            bill['word_canonical_sha256'] = hashlib.sha256(canonical(instance)).hexdigest()
            result[name], all_records[name] = bill, records
    moves = lambda rs: [r for r in rs if r[0] == 0]
    copies = lambda rs: [r for r in rs if r[0] in (2, 3)]
    need(moves(all_records['baseline']) == moves(all_records['F4']), 'frame itinerary changed')
    need(copies(all_records['baseline']) == copies(all_records['F4']), 'COPY/ERASE interface changed')
    profile = Counter(r[4] for r in all_records['F4'] if r[0] == 0)
    profile.update(r[5] for r in all_records['F4'] if r[0] == 2)
    need(dict(profile) == {1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}, 'paid profile mismatch')
    need(result['F4']['ADDs'] - result['baseline']['ADDs'] == 69, 'unpriced F4 gates')
    controls = []
    def reject(label, action):
        try:
            action()
        except ValueError:
            controls.append(label)
        else:
            raise ValueError('accepted negative control: '+label)
    reject('restore_after_target_write', lambda: replay(build(word, late=True)))
    bad = copy.deepcopy(feed)
    del bad['D'][111]
    reject('omitted_helper_restore', lambda: replay(bad))
    bad_records = list(all_records['F4'])
    del bad_records[next(i for i, r in enumerate(bad_records) if r[0] == 3)]
    reject('omitted_native_ERASE', lambda: record_bill(bad_records, n))
    def strict_guard(value, bits):
        need(value < (1 << bits), 'strict boundary')
    for bits in (104, 192):
        strict_guard((1 << bits)-1, bits)
        reject('equality_at_'+str(bits)+'_bit_cap', lambda b=bits: strict_guard(1 << b, b))
    return dict(status='PASS_R439_F4_PRECISION_BILL', bills=result, columns=n, directions=2,
                paid_profile={str(k):v for k,v in sorted(profile.items())},
                paid_rank_mass=sum(k*v for k,v in profile.items()), controls=controls,
                kappa_claim=None, native_cpp_replay=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    report = run()
    need(report == json.loads((HERE/'CERTIFICATE.json').read_text(encoding='utf-8')), 'certificate mismatch')
    if args.out:
        args.out.write_text(json.dumps(report, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    print('PASS_R439_F4_PRECISION_BILL ADDs=24305->24374 bits=93/177->96/183 controls=5 no_new_kappa')
