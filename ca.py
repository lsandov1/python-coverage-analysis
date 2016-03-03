#!/usr/bin/python

import coverage
import glob
import itertools


# A-B, A /\ B, B-A, A \/ B
def sets(A,B):
    AminusB = [a for a in A if not a in B]
    BminusA = [b for b in B if not b in A]
    AinterB = [a for a in A if a in B]
    AplusB = A + BminusA
    return (AminusB, AinterB, BminusA, AplusB)

# (A-B) + (B-A)
# -------------
#      A+B
def similarity(A, B):
    AminusB, _, BminusA, AplusB = sets(A,B)
    
    lenAplusB = len(AplusB)
    if not lenAplusB:
        return float(1)

    lenAminusB = len(AminusB)
    lenBminusA = len(BminusA)
    
    return (float(lenAminusB) + float(lenBminusA)) / float(lenAplusB)

class CA(object):
    def __init__(self, cfn1, cfn2):
        self._cfn1 = cfn1
        self._cfn2 = cfn2
        self._c1 = coverage.CoverageData()
        self._c1.read_file(self._cfn1)
        self._c2 = coverage.CoverageData()
        self._c2.read_file(self._cfn2)
        self._lc1 = self._c1.line_counts(True)
        self._lc2 = self._c2.line_counts(True)
        self._lenFS1minusFS2, self._lenFS1interFS2, self._lenFS2minusFS1, self._lenFS1unionFS2, self._sim = self._similarity()

    def __str__(self):
        return ("%s %s %s %s %s %s %s" % 
                (self._cfn1, self._cfn2, self._lenFS1minusFS2, self._lenFS1interFS2, self._lenFS2minusFS1, self._lenFS1unionFS2, self._sim))

    def _similarity(self):
        files1 = self._lc1.keys()
        files2 = self._lc2.keys()
        FS1minusFS2, FS1interFS2, FS2minusFS1, FS1unionFS2 = sets(files1, files2)
        lenFS1minusFS2, lenFS1interFS2, lenFS2minusFS1, lenFS1unionFS2 = map(len, [FS1minusFS2, FS1interFS2, FS2minusFS1, FS1unionFS2])

        s = 0.0
        s += float(lenFS1minusFS2)
        s += float(lenFS2minusFS1)

        for f in FS1interFS2:
            lines1 = self._c1.lines(f)
            lines2 = self._c2.lines(f)
            s += similarity(lines1, lines2)

        return lenFS1minusFS2, lenFS1interFS2, lenFS2minusFS1, lenFS1unionFS2, s/lenFS1unionFS2

if __name__ == "__main__":
    fns = glob.glob('.coverage.*')
    for fn1,fn2 in itertools.combinations(fns, 2):
        print CA(fn1, fn2)
