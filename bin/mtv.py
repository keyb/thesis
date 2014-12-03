from charitems import to_binary, to_chars
from random import randint
from random import sample
from math import log
from itertools import combinations
from time import time
from memoisation import memoise

# Set of singletons
I = set()

# Sample
D = list()

# Summary:
C = set()

# Set of all attributes:
A = 'abcdef'
print 'Attributes (%d): %s' % (len(A), A)

def create_patterns(attributes, patterns, size):       
    """Creates all patterns of a given size and add them to patterns"""
    comb = combinations(A,size)
    for c in comb:
        pattern = to_binary(''.join(c))
        patterns.add(pattern)

patterns = set()
#add all itemsets of size 2 and 3 to patterns:
create_patterns(A, patterns, 2) 
create_patterns(A, patterns, 3)

#Add all singletons to sumary:
create_patterns(A, C, 1)

# Generate random sample D
while len(D) != 300:
    _sample = sample(A, randint(1, len(A)))
    D.append(''.join(sorted(_sample)))
print 'D (%d): %s' % (len(D), D)

for index, x in enumerate(D):
    D[index] = to_binary(x)

# Initialise sample space
T  = 2 ** len(A)

# Dict for values U_x
U = {} 
u0 = 2 ** -len(A)

def contains(a, b):
    """ True if a contains b """
    return a & b == b

def model(t, C, u0, U):
    res = 1.0
    for x in C:
        if contains(t, x):
            res = res * U[x]
    return u0 * res

def query(x, C, u0, U):
    p = 0.0
    for t in range(T):
        if contains(t, x):
            p += model(t, C, u0, U)
    return p

# Memoise: The function will cache previous results with the argument
# this assumes that D does not change between cached results.
@memoise
def fr(x):
    p = 0.0
    for xi in D:
        if contains(xi, x):
            p += 1
    p = p / float(len(D))
    assert p <= 1.0
    return p

def iterative_scaling(C):
    U = {}
    u0 = 2 ** -len(A)
    biggestdiff = -1
    for c in C:
        U[c] = 1.0
    converge_iterations = 0
    iterations = 0
    while iterations < 20: #((biggest_diff > 0.00000001 or biggest_diff == -1) and iterations < 100): # converge
        converge_iterations += 1
        biggest_diff = -1
        iterations += 1
        for x in C:

            p = query(x, C, u0, U)
            U[x] = U[x] * (fr(x) / p) * ((1 - p) / (1 - fr(x)))
            u0 = u0 * (1 - fr(x)) / (1 -  p)

            diff = abs(fr(x) - query(x, C, u0, U))
            if diff > biggest_diff:
                biggest_diff = diff
                # print 'biggest_diff:%f fx:%f p:%f' % (biggest_diff, fr(x), p)

    # print 'Converge iterations:%d biggest_diff:%f ' % (converge_iterations, biggest_diff)
    return u0, U

def find_best_itemset():
    """Returns a pattern that potentially will be included in the summary."""
    return patterns.pop()

def MTV():
    """ """
    global C
    global u0
    global U

    # Compute our initial, current best, model
    u0, U = iterative_scaling(C)

    # This is the current best score
    cur_score = s(C, u0, U)

    # Brute force all patterns
    while len(patterns) > 0: 

        # Possible best itemset to include in the summary
        X = find_best_itemset()

        # Candidate summary 
        _C = C.union([X])
        
        # Candidate model
        _u0, _U = iterative_scaling(_C) 
        
        # Candidate score
        temp_score = s(_C, _u0, _U)

        # If the score has improved, we use the 
        # candidate summary as our
        # current best summary
        if  temp_score < cur_score:
            cur_score = temp_score
            C = _C
            u0 = _u0
            U = _U

def s(C, u0, U):
    return -1 * (len(D) * (log(u0) +  sum([fr(x) * log(U[x]) for x in C]))) + 0.5 * len(C) * log(len(D))

start = time()
MTV()
print 'MTV run time: ', time() - start
print 'Final summary: '
for x in C:
    print to_chars(x)

for c in C:
    print 'query %s with fr %f query %f uX: %f' % (to_chars(c), fr(c), query(c, C, u0, U), U[c])
print 'u0: ', u0

def is_in_sumamry(y, C):
    for x in C:
        if y == x:
            return True
    return False

def query_unknowns(amount):
    """Attempts to create an amount of itemsets not in the summary, and
        print their frequency and estimated frequency
        amount: Amount of itemsets not in C to attempt to find
    """
    unknowns = 0
    for t in range(T):
        y = randint(0, T)
        if not is_in_sumamry(y, C):
            unknowns += 1
            print 'Unknown itemset: query %s with fr %f query %f' % (to_chars(y), fr(y), query(y, C, u0, U))
        if unknowns == amount:
            return

query_unknowns(10)

def total_probability():
    """ Assert and print the total probability of the model """
    total_prob = 0.0
    for t in range(T):
        p = model(t, C, u0, U)
        total_prob += p
    assert abs(total_prob - 1.0) < 0.001
    print 'total prob: ', total_prob
total_probability()

# def running_example():
#     # Summary from running example from Mampey et. al
#     abc  = to_binary('abc') # 00000111
#     cd   = to_binary('cd')  # 00001100
#     _def = to_binary('def') # 00111000

#     C.add(abc)
#     C.add(cd)
#     C.add(_def)

#     # Initial computed values from running example in Mampey
#     u0 = 2 ** -8
#     u1 = u2 = u3 = 1
#     U[abc] = u1
#     U[cd] = u2
#     U[_def] = u3
#     print '\nInitial where abc=0.125'
#     run()

#     # Query with converged values
#     u0 = 3 * 10 ** -4
#     u1 = 28.5
#     u2 = 0.12
#     u3 = 85.4
#     U[abc] = u1
#     U[cd] = u2
#     U[_def] = u3
#     print '\nConverged:'
#     run()