#!/usr/bin/env python3
"""Reproduce canonical rankings; no external packages or network needed."""
from pathlib import Path
from decimal import Decimal
import csv,json
base=Path(__file__).resolve().parent

def read(name):
    with (base/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter=';'))
model=read('SCORING_MODEL.csv');matrix=read('SCORE_MATRIX.csv')
weights={r['criterion_id']:Decimal(r['weight_percent']) for r in model}
assert sum(weights.values())==100 and len(matrix)==96
from collections import defaultdict
by=defaultdict(dict)
for x in matrix:
    pid,c=x['pool_id'],x['criterion_id']; assert c not in by[pid]
    level=int(x['observed_evidence_level_0_4']); assert 0<=level<=4
    by[pid][c]=x
scores={pid:sum((weights[c]*Decimal(int(v['observed_evidence_level_0_4']))/4 for c,v in rows.items()),Decimal(0)) for pid,rows in by.items()}
eligible=[pid for pid,r in by.items() if next(iter(r.values()))['included_in_ranking']=='ДА']
assert len(eligible)==14
ranks={pid:1+sum(scores[q]>scores[pid] for q in eligible) for pid in eligible}
actual={v['poolId']:(Decimal(str(v['score'])),v['position']) for v in json.loads((base/'RESULTS.json').read_text(encoding='utf-8'))['allEligibleParticipants']}
assert actual=={pid:(scores[pid],ranks[pid]) for pid in eligible}
for pid in sorted(eligible,key=lambda x:(-scores[x],x)):
    print(f'{ranks[pid]:2d}. {pid} {scores[pid]:6.2f}  {by[pid]["C1"]["provider"]} | {by[pid]["C1"]["course"]}')
print('PASS: exact score, rank and output checks')
