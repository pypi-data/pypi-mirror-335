# Compute a substitution 

def induce(e, i, flipped):
	"""
	Compute one step of induction on place, and return the associated substitution.
	e : couple of lists, before and after exchange
	i : top or bottom induction (i=0: bottom losing letter, i=1: top losing letter)
	"""
	from sage.combinat.words.morphism import WordMorphism
	if i == 0:
		i0 = 0
		i1 = 1 # losing letter
	else:
		i0 = 1
		i1 = 0 # losing letter
	d = dict()
	for i in e[0]:
		d[i] = [i]
	d[e[i1][-1]] = [e[1][-1], e[0][-1]]
	if flipped[e[i0][-1]]:
		from operator import xor
		e[i1].insert(e[i1].index(e[i0][-1]), e[i1][-1])
		flipped[e[i1][-1]] = not flipped[e[i1][-1]]
	else:
		e[i1].insert(e[i1].index(e[i0][-1])+1, e[i1][-1])
	e[i1].pop()
	return WordMorphism(d)

def which_int (x, v):
	"""
	Return the index of the interval in which is x, where v gives lengths.
	"""
	from sage.functions.generalized import sign
	s = 0
	for i,t in enumerate(v):
		s += t
		if sign(s-x) == 1:
			return i

def translation (i, p, v):
	"""
	Compute the translation of ith interval.
	"""
	s = 0
	for j in p:
		if j == i+1:
			break
		s += v[j-1]
	for j in range(i):
		s -= v[j]
	return s

def IET (x, p, v):
	"""
	Compute the image of x by the IET given by permutation p and lengths v
	"""
	i = which_int(x,v)
	s = 0
	for j in p:
		if j == i+1:
			break
		s += v[j-1]
	for j in range(i):
		s -= v[j]
	return x+s

def orbit (x, per, v, N=20):
    """
    Compute N steps of the orbit of x.

    INPUT:

        - ``x`` - a number

        - ``per`` - permutation, given as a string or list of int

        - ``v`` - vector of lengths

        - ``N`` - length of the orbit to compute

    EXAMPLES::

        sage: from eigenmorphic import *
        sage: orbit(random(), "321", [.23, .34, .43])		# random
        word: 31313231322313223132

    """
    from sage.combinat.words.word import Word
    if isinstance(per, str):
        per = [int(c) for c in per]
    lt = [translation(i, per, v) for i in range(len(per))]
    w = []
    for _ in range(N):
        i = which_int(x,v)
        w.append(i+1)
        x = x + lt[i]
    return Word(w)

def rauzy_path_substitution(per, path, flips=None, get_per=True, verb=False):
	from copy import copy
	from sage.combinat.words.morphism import WordMorphism
	if isinstance(per, str):
		per = [int(c) for c in per] # convert it to numbers
	try:
		per[0][0]
		e = per
	except:
		e = [list(range(1,len(per)+1)), per]
	if verb > 0:
		print("e = %s" % e)
	if isinstance(path, str):
		path = [int(c) for c in path] # convert it to numbers
	if verb > 0:
		print("path = %s" % path)
	if flips is None:
		f = {i:False for i in range(1,len(e[0])+1)}
	else:
		f = copy(flips)
	if verb > 0:
		print("flips = %s" % f)
	d = dict()
	for i in e[0]:
		d[i] = [i]
	s = WordMorphism(d)
	for i in path:
		if verb > 0:
			print(e)
			print(f)
		s0 = induce(e, i, f)
		if verb > 0:
			print(s0)
		s = s*s0
	if verb > 0:
		print(e)
		print(f)
		print(s)
		print("per = %s" % per)
	if get_per:
		return s, e #[e[0].index(t)+1 for t in e[1]]
	return s

def rauzy_loop_substitution(per, loop, flips=None, max_len=1000, get_preperiod=False, get_cmp=False, verb=False):
	"""
	Compute the susbtitution of a loop in the Rauzy graph from a given permutation per.

	INPUT:

		- ``per`` - list -- a permutation
			The i-th element of the list is the image of (i+1) by the permutation.

		- ``loop`` - list or string or vector -- list with values in {0,1} indicating which rauzy induction
			where 0 indicate that the losing letter is at bottom and
				  1 indicate that the losing letter is at top
			or vector of lengths (with same length as per).

		- ``flips`` - dict (default: ``None``) -- dictionnary indicating for each letter whether it is flipped (value True) or not (value False).

		- ``max_len`` - int (default: ``1000``) - maximum length of the Rauzy loop if a vector of lengths is given

		- ``get_preperiod`` - bool (default: ``False``) - if ``True``, return a couple of substitutions corresponding to (pre-period, period)
		
		- ``get_cmp`` - bool (default: ``False``) - if ``True``, return the list of comparaisons

		- ``verb`` - int (default: ``False``) - if >0, print informations.

	OUTPUT:
		A WordMorphism

	EXAMPLES:

		sage: from eigenmorphic import *
		sage: per = [9, 8, 7, 6, 5, 4, 3, 2, 1] # permutation
		sage: loop = "11010101101100011110000011111010000000110"
		sage: rauzy_loop_substitution(per, loop)
		WordMorphism: 1->17262719, 2->172627262719, 3->172635362719, 4->1726354445362719, 5->172635445362719, 6->1726362719, 7->172719, 8->18181819, 9->181819

		sage: a = AA(2*cos(pi/7))
		sage: l = [1, 2*a-3, 2-a, a^2-a, 2*a^2-3*a-1, -3*a^2+5*a+1]
		sage: rauzy_loop_substitution([4,3,2,6,5,1], l)
		WordMorphism: 1->14164, 2->142324, 3->1423324, 4->1424, 5->154154164, 6->154164

	"""
	from copy import copy
	from sage.combinat.words.morphism import WordMorphism
	if isinstance(per, str):
		per = [int(c) for c in per] # convert it to numbers
	per0 = copy(per)
	e = [list(range(1,len(per)+1)), per]
	if flips is None:
		f = {i:False for i in range(1,len(per)+1)}
	else:
		f = copy(flips)
	f0 = copy(f)
	if verb > 0:
		print("flips = %s" % f)
	d = dict()
	for i in e[0]:
		d[i] = [i]
	s = WordMorphism(d)
	if isinstance(loop, str):
		loop = [int(c) for c in loop] # convert it to numbers
	if verb > 1:
		print("per = %s, loop = %s" % (per, loop))
	if len(loop) == len(per) and len([i for i in loop if i not in [0,1]]) != 0:
		from sage.modules.free_module_element import vector
		if verb > 0:
			print("loop is a vector")
		v = vector(loop)
		v /= sum(v)
		v0 = vector(v)
		seen = dict()
		ls = []
		lcmp = []
		for i in range(max_len):
			cmp = int(v[e[0][-1]-1] < v[e[1][-1]-1])
			if verb > 1:
				print(cmp)
			lcmp.append(cmp)
			s0 = induce(e, cmp, flipped=f)
			if verb > 0:
				print(s0)
			s = s*s0
			m = s0.incidence_matrix()
			v = m.inverse()*v
			if verb > 1:
				print(v)
			v /= sum(v)
			if v == v0:
				break
			if tuple(v) in seen:
				if get_preperiod:
					from sage.misc.misc_c import prod
					i = seen[tuple(v)]
					if get_cmp:
						return (lcmp[:i], prod(ls[:i])), (lcmp[i:], prod(ls[i:]+[s0]))
					else:
						return prod(ls[:i]), prod(ls[i:]+[s0])
				else:
					raise ValueError("It is pre-periodic with a non-trivial pre-period (you can compute it with get_preperiod=True).")
			seen[tuple(v)] = i+1
			ls.append(s0)
			if verb > 1:
				print(v)
				#print([t.n() for t in v])
		else:
			raise ValueError("The given lengths vector does not give a loop, or the loop is longer than max_len=%s. Try with bigger max_len." % max_len)
	else:
		if verb > 0:
			print("loop is a list of inductions")
		for i in loop:
			if verb > 0:
				print(e)
				print(f)
			s0 = induce(e, i, f)
			if verb > 0:
				print(s0)
			s = s*s0
		if verb > 0:
			print(e)
			print(f)
			print(s)
			print("per = %s" % per)
		# check if it is indeed a loop
		for i in range(len(e[0])):
			if e[0][i] != i+1 or e[1][i] != per0[i]:
				raise ValueError("This is not a loop in the Rauzy graph !\n%s != %s" % (e,[list(range(1,len(per)+1)), per0]))
		if f != f0:
			raise ValueError("This is not a loop in the Rauzy graph (flips are different) !\n%s != %s" % (f,f0))
	if get_cmp:
		return lcmp,s
	return s

