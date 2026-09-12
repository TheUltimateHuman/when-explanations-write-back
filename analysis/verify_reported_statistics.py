#!/usr/bin/env python3
from math import comb, isclose

def sign_p(k,n):
    m=min(k,n-k)
    return min(1.0, 2*sum(comb(n,i) for i in range(m+1))/(2**n))

checks=[
('PCA-008 Qwen',44,48,1.5138326148189662e-09),
('PCA-008 answer',41,48,6.240408438884515e-07),
('PCA-012 DIRECT',43,48,1.3680484300948592e-08),
('PCA-012 XOR',37,48,2.2224496262168714e-04),
('Mistral 28/48',28,48,0.31232680747326924),
('PR-002 primary',87,96,3.640258907444359e-17),
('PR-002 M1',70,96,8.049550377189253e-06),
('PR-002 M2',66,96,3.0559732759326285e-04),
('PR-002 content-free',63,96,0.002878610081200932),
('PR-002 natural',60,96,0.018433352931462543),
]
for name,k,n,expected in checks:
    got=sign_p(k,n)
    assert isclose(got,expected,rel_tol=1e-12,abs_tol=1e-18), (name,got,expected)
    print(f'PASS sign test {name}: {got:.12g}')

E1=0.0381362; E2=0.0281962; primary=0.0331662
assert isclose((E1+E2)/2,primary,abs_tol=1e-12)
print('PASS mapping-balance identity: (E1+E2)/2 = 0.0331662')

cal={'Qwen':(0.8333,19.29),'Mistral':(0.8750,15.58),'Phi':(1.0,52.26)}
elig={m:(acc>=0.90 and sens>=1) for m,(acc,sens) in cal.items()}
assert elig=={'Qwen':False,'Mistral':False,'Phi':True}
print('PASS PR-002 frozen capability gate:',elig)
assert not (elig['Qwen'] and (elig['Mistral'] or elig['Phi']))
print('PASS preregistered cross-architecture gate: NOT MET')
