# coding=utf8
r"""
Interface with a C++ code computing the balanced pair algorithm
"""
# *****************************************************************************
#  Copyright (C) 2025 Paul Mercat <mercatp@icloud.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#	This code is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty
#	of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  See the GNU General Public License for more details; the full text
#  is available at:
#
#				  http://www.gnu.org/licenses/
# *****************************************************************************
from __future__ import division, print_function, absolute_import

from libc.stdlib cimport malloc, free
#from libc.stdint cimport uint8_t, uint64_t, int8_t
#from libc.math cimport log, ceil, floor, round, fabs, M_PI as pi_number

#from cysignals.signals cimport sig_on, sig_off, sig_check

#import numpy as np
#cimport numpy as np

#from sage.sets.set import Set
#from sage.rings.qqbar import QQbar
#from sage.rings.padics.factory import Qp
#from sage.rings.integer import Integer
#from sage.combinat.words.morphism import WordMorphism
#from sage.rings.number_field.number_field import NumberField

cdef extern from "bpa.h":
    struct Word:
        long n
        char *l

    struct Substitution:
        int n
        Word *w
    
    struct BP:
        Word a,b
    
    struct Matrix:
        int nr, nc
        int **e
    
    void BaPA(Substitution s, Matrix m, BP *I, int n, int verb)

cpdef bpa_c(s, V, I, verb):
    """
    Call the C++ code for fast balanced pair algorithm.
    It stabilizes the set of balanced pairs I for substitution s, with equivalent relation given by V.
    
    INPUT:
        - ``s`` - WordMorphism -- the substitution
        - ``V`` - matrix in ZZ -- the projection
        - ``I`` - list -- list of initial balanced pairs
    """
    cdef list A = list(s.domain().alphabet())
    if verb > 0:
        print("A = %s" % A)
    if len(A) > 256:
        raise NotImplementedError("Sorry ! Implemented only for alphabet of size <= 256.")
    cdef Substitution sc
    cdef int i, j
    cdef BP *bp
    cdef Matrix m
    # convert th WordMorphism to a Substitution
    if verb > 1:
        print("Alloc Substitution...")
    sc.n = len(A)
    sc.w = <Word *>malloc(sizeof(Word)*sc.n)
    for i in range(sc.n):
        w = s(A[i])
        if verb > 3:
            print(w)
        sc.w[i].n = len(w)
        sc.w[i].l = <char *>malloc(sizeof(char)*sc.w[i].n);
        for j in range(sc.w[i].n):
            sc.w[i].l[j] = A.index(w[j])
    # convert the set of balanced pairs
    if verb > 1:
        print("Alloc %s balanced pairs..." % len(I))
    bp = <BP *>malloc(sizeof(BP)*len(I))
    for i,(w1,w2) in enumerate(I):
        bp[i].a.n = len(w1)
        bp[i].b.n = len(w2)
        bp[i].a.l = <char *>malloc(sizeof(char)*len(w1));
        for j in range(len(w1)):
            bp[i].a.l[j] = A.index(w1[j])
        bp[i].b.l = <char *>malloc(sizeof(char)*len(w2));
        for j in range(len(w2)):
            bp[i].b.l[j] = A.index(w2[j])
    # convert the matrix
    if verb > 1:
        print("Alloc Matrix...")
    m.nr = V.nrows()
    m.nc = V.ncols()
    m.e = <int **>malloc(sizeof(int *)*m.nr)
    for i in range(m.nr):
        m.e[i] = <int *>malloc(sizeof(int)*m.nc)
        for j in range(m.nc):
            m.e[i][j] = V[i][j]
    # call the C++ code
    if verb > 1:
        print("Call C code...")
    BaPA(sc, m, bp, len(I), verb-1)
    # Free
    if verb > 1:
        print("Free...")
    for i in range(m.nr):
        free(m.e[i]);
    free(m.e);
    for i,_ in enumerate(I):
        free(bp[i].a.l);
        free(bp[i].b.l);
    free(bp);
    for i in range(sc.n):
        free(sc.w[i].l);
    free(sc.w);

#def bpa(s, V, I, verb=0):
#    bpa_c(s, V, I, verb)
