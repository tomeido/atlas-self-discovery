"""Finite-state, exact-arithmetic and schema checks for the original task bank.

Language/inference tasks also require the editorial review documented by their
explanations; this script does not claim to establish psychometric validity.
"""
import itertools
import json
import math
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

BASE = Path(__file__).parent / 'dist'
bank = json.loads((BASE / 'performance-bank.json').read_text())
challenges = json.loads((BASE / 'frontier-challenges.json').read_text())
assert len(bank) == 36
assert len(challenges) == 8
assert len({q['id'] for q in bank}) == 36
assert Counter(q['domain'] for q in bank) == {
    'logic': 6, 'quantitative': 6, 'spatial': 6,
    'verbal': 6, 'causal': 6, 'calibration': 6,
}
for q in bank:
    assert set(q) == {'id', 'domain', 'title', 'prompt', 'options', 'correct', 'explanation', 'skill'}
    assert len(q['options']) == 4
    assert len(set(q['options'])) == 4
    assert all(isinstance(option, str) for option in q['options'])
    assert q['correct'] in range(4)
for challenge in challenges:
    assert set(challenge) == {'id', 'title', 'prompt', 'constraints', 'rubric', 'experiment'}
    assert len(challenge['rubric']) == 4
    assert all('0=' in r['description'] and '4=' in r['description'] for r in challenge['rubric'])

expected_answers = {
    'logic-01': '20개', 'logic-02': '3개',
    'logic-03': '어떤 진은 타가 아니다.',
    'logic-04': 'A는 승인되지 않고 D는 승인된다.',
    'logic-05': 'B', 'logic-06': '2명',
    'quantitative-01': '12L', 'quantitative-02': '15/28',
    'quantitative-03': '15/4회', 'quantitative-04': '8시간',
    'quantitative-05': '44점', 'quantitative-06': '122',
    'spatial-01': 'C', 'spatial-02': 'B, C, F',
    'spatial-03': '(1,−3,2)', 'spatial-04': '9개',
    'spatial-05': '12개', 'spatial-06': '34개',
    'verbal-01': '사전 등록을 마치고 출입 허가를 받은 사람은 안전교육을 이수했다.',
    'verbal-02': '보조금 규모가 큰 서비스일수록 초기 가입자는 많지만, 보조금 종료 후 이용 유지율은 초기 가입 수와 뚜렷한 관계가 없다.',
    'verbal-03': '이 설문에서는 주 2회 이상 운동하는 집단과 더 높은 평균 만족도가 함께 관찰되었다.',
    'verbal-04': 'M은 조사한 동일 조건에서 재현성을 보였지만 새로운 현장으로의 일반화는 약했다.',
    'verbal-05': '연구자가 그 인용문을 발언했다는 주장은 부정된다.',
    'verbal-06': '절차의 효과는 숙련도와 평가 항목에 따라 달랐고 하나의 합산 점수는 이 차이를 숨길 수 있다.',
    'causal-01': '미보고 이유와 가능한 성과 범위를 조사하고, 최초 배정 집단을 기준으로 결측 가정별 추정이나 민감도 분석을 수행한다.',
    'causal-02': '둘 중 어느 능력이든 선발에 영향을 주는 조건에 맞춘 선택 때문에 합격자 안에서 관계가 생길 수 있다.',
    'causal-03': 'A만 통제하고 M은 통제하지 않는다.',
    'causal-04': '오류 4건 감소',
    'causal-05': 'A는 각 난이도 안에서 성공률이 더 높지만, 난이도 구성 차이 때문에 전체 성공률은 더 낮다. 이 표만으로 방법의 인과적 우열을 확정할 수는 없다.',
    'causal-06': '팀을 무작위로 기능 제공·미제공에 배정하고 팀 단위의 영향과 변동을 반영하여 분석한다.',
    'calibration-01': '10/109', 'calibration-02': '16/17',
    'calibration-03': '0.19', 'calibration-04': '3/4',
    'calibration-05': '3/4', 'calibration-06': 'B가 0.015점 더 좋다.',
}
for q in bank:
    assert q['options'][q['correct']] == expected_answers[q['id']], q['id']

checks = {}
orders = [x for x in itertools.permutations('ABCDEF')
          if x.index('A') < x.index('D')
          and x.index('B') < x.index('E')
          and x.index('D') < x.index('F')
          and abs(x.index('C') - x.index('F')) == 1
          and x[0] != 'C']
checks['logic-01'] = len(orders) == 20
states = []
for state in itertools.product([False, True], repeat=5):
    p, q, r, s, t = state
    if sum(state) == 3 and (not p or q) and (q == (r != s)) and (not t or r) and (not s or not p):
        states.append(state)
checks['logic-02'] = len(states) == 3
valid = []
for a, b, c, d in itertools.product([False, True], repeat=4):
    if (a or b) and (not a or c) and (not b or c) and (not c or d) and (not d or not a):
        valid.append((a, b, c, d))
checks['logic-04'] = valid == [(False, True, True, True)]
checks['logic-05'] = [sum([x in 'AB', x in 'BC', x == 'D', x != 'A']) for x in 'ABCD'] == [1, 3, 2, 2]
checks['logic-06'] = (12 - (8 + 7 + 6 - 5 - 4 - 3)) == 3 and 7 - 5 - 3 + 3 == 2
checks['quantitative-01'] = (F(3) + F(1, 2) * 12) / 2 / (F(12 + 12, 2) + 6) == F(1, 4)
checks['quantitative-02'] = F(math.comb(3, 1) * math.comb(5, 2), math.comb(8, 3)) == F(15, 28)
checks['quantitative-03'] = (1 + F(2, 3)) / (F(2, 3) ** 2) == F(15, 4)
checks['quantitative-04'] = (4 + 40 / 4 == 14) and (4 + 40 / 8 == 9) and (4 + 40 / 10 == 8)
checks['quantitative-05'] = max(5 * a + 4 * b for a in range(9) for b in range(10)
                               if 3 * a + 2 * b <= 24 and a + 2 * b <= 18) == 44
checks['quantitative-06'] = [n for n in range(100, 150) if n % 7 == 3 and n % 5 == 2] == [122]
faces = dict(U='A', D='F', N='B', S='E', W='C', E='D')
for direction in ['E', 'N', 'E', 'S']:
    old = faces.copy()
    cycle = {'E': ['U', 'E', 'D', 'W'], 'N': ['U', 'N', 'D', 'S'], 'S': ['U', 'S', 'D', 'N']}[direction]
    for index, face in enumerate(cycle):
        faces[face] = old[cycle[index - 1]]
checks['spatial-01'] = faces['U'] == 'C'
x, y, z = 2, -1, 3
x, y, z = -y, x, z
x, y, z = x, -z, y
checks['spatial-03'] = (x, y, z) == (1, -3, 2)
paint_counts = [sum((x == 3, y == 3, z == 3)) for x, y, z in itertools.product(range(4), repeat=3)]
checks['spatial-04'] = paint_counts.count(2) == 9
minimum = math.inf
for cells in itertools.product([1, 2, 3], repeat=9):
    if ([max(cells[r * 3:r * 3 + 3]) for r in range(3)] == [3, 2, 1]
            and [max(cells[c::3]) for c in range(3)] == [2, 3, 1]):
        minimum = min(minimum, sum(cells))
checks['spatial-05'] = minimum == 12
checks['spatial-06'] = math.comb(8, 4) - math.comb(4, 2) ** 2 == 34
checks['causal-04'] = (12 - 20) - (14 - 18) == -4
checks['causal-05'] = F(9, 10) > F(72, 90) and F(27, 90) > F(2, 10) and F(36, 100) < F(74, 100)
checks['calibration-01'] = F(1, 100) * F(9, 10) / (F(1, 100) * F(9, 10) + F(99, 100) * F(9, 100)) == F(10, 109)
checks['calibration-02'] = F(4, 5) ** 2 / (F(4, 5) ** 2 + F(1, 5) ** 2) == F(16, 17)
checks['calibration-03'] = F(3, 10) * F(4, 10) + F(7, 10) * F(1, 10) == F(19, 100)
checks['calibration-04'] = (F(1, 3) * F(6, 15)) / (F(1, 3) * F(6, 15) + F(2, 3) * F(1, 15)) == F(3, 4)
checks['calibration-05'] = (F(7, 10) - F(4, 10)) / (1 - F(6, 10)) == F(3, 4)
actual = [1, 0, 1, 0]
score = lambda array: sum((x - y) ** 2 for x, y in zip(array, actual)) / 4
checks['calibration-06'] = score([F(9, 10), F(7, 10), F(6, 10), F(2, 10)]) - score([F(6, 10), F(4, 10), F(6, 10), F(4, 10)]) == F(15, 1000)
assert all(checks.values()), checks
print(json.dumps({
    'performance_tasks': len(bank),
    'frontier_challenges': len(challenges),
    'exact_answer_checks': len(checks),
    'answer_key_text_checks': len(expected_answers),
    'correct_position_counts': dict(sorted(Counter(q['correct'] for q in bank).items())),
    'status': 'passed',
}, ensure_ascii=False))
