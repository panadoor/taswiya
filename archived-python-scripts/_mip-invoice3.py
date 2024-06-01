# Formulate and solve the following a MIP model to find optimal quantities
# and prices to match a given invoice amount. Given 2 product categories: c1 and c2
#  Minimize
#        amount - Sum(c1qi * c1pi) - Sum(c2qi * c2pi)
#        ideally the above should be 0
#  subject to
#        q (quantity) must be positive
#        p (price) must be within a certain range and must have 2 decimals max
#        x, y, z binary

import gurobipy as gp
from gurobipy import GRB, quicksum

from dataclasses import dataclass
from typing import List

@dataclass
class Solution:
    # idx: int
    c1q: List[float]
    c1p:  List[float]
    c2q: List[float]
    c2p:  List[float]
    total: float


def getPrices(lb, ub):
    prices = []
    i = lb
    while (i <= ub):
        prices.append(i)
        i = round(i + 0.01, 2)
    return prices

solutions = []

# try:
amountTTC = 5000
# Reduce 20% VAT from the amount
amount = amountTTC / 1.2
amountTolerance = 0.01

# Product Category 1 lower bound price
c1p = 180
c1pMaxDecimal = 0.4

# Product Category 2 lower bound price
c2p = 200
c2pMaxDecimal = 0.4

c11prices = getPrices(c1p, c1p + c1pMaxDecimal)
c12prices = getPrices(c1p - c1pMaxDecimal, c1p)

c21prices = getPrices(c2p, c2p + c2pMaxDecimal)
c22prices = getPrices(c2p - c2pMaxDecimal, c2p)
print(c22prices)

prices = [([c11p], [c21p, c22p])
          for c11p in c11prices
          #for c12p in c12prices
          for c21p in c21prices
          for c22p in c22prices]
print('Prices cartesian product - length:', len(prices))

# Number of products in category 1
c1count = 1
# Number of products in category 2
c2count = 2
# Create a new model
m = gp.Model("optimize-qty-price")

# Want c1q[i], c2q[j] to be strictly integers
# Want c1p[i], c2p[j] to only have 2 decimal digits
# e.g., A value of c1p[0] = 200.124 is NOT allowed 200.12 is ok.
# These are prices to use in invoices
# and accounting and must have 2 decimals only

# Optimize model
m.Params.NonConvex = 2
# m.Params.IntegralityFocus = 1
# m.Params.MIRCuts = -1
m.Params.MIPFocus = 2  # Focus on providing Optimality

# Create variables for category 1
c1q = m.addVars((i for i in range(c1count)), vtype=GRB.INTEGER, name="c1q", lb=0)
# c1p = m.addVars((i for i in range(c1count)), name="c1p", lb=pc1lb, ub=pc1ub)

# Create variables for category 2
c2q = m.addVars((i for i in range(c2count)), vtype=GRB.INTEGER, name="c2q", lb=0)
# c2p = m.addVars((i for i in range(c2count)), name="c2p", lb=pc2lb, ub=pc2ub)

j = 0
for (c1p, c2p) in prices:
    print('%s -> c1p: %s - c2p: %s' % (j, c1p, c2p))
    # m.reset(0)

    # Set objective
    expr = amount - quicksum(c1q[i] * c1p[i] for i in c1q) - quicksum(c2q[i] * c2p[i] for i in c2q)
    m.setObjective(expr, GRB.MINIMIZE)

    # Without this constraint the Model is unbounded
    if j > 0:
        m.remove(m.getConstrs()[0])
        m.remove(m.getConstrs()[1])

    m.addConstr(expr >= 0, "c1")
    m.addConstr(expr <= amountTolerance, "c2")

    try:
        m.update()
        m.optimize()
    except gp.GurobiError as e:
        print('Error code ' + str(e.errno) + ': ' + str(e))
    except AttributeError:
        print('Encountered an attribute error')

    print('Model status: %s' % m.Status)
    if m.Status != GRB.INFEASIBLE and m.Status != GRB.UNBOUNDED and m.Status != GRB.INF_OR_UNBD:
        msg = '%s -> c1p: %s - c2p: %s' % (j, c1p, c2p)
        print(msg)

        solution = Solution(
            # idx=j,
            c1q=[c1q[i].x for i in range(c1count) if c1q[i].x > 0],
            c1p=c1p,
            c2q=[c2q[i].x for i in range(c2count) if c2q[i].x > 0],
            c2p=c2p,
            total=0
        )

        if len(solution.c1q) == 0:
            solution.c1p = [0]

        if len(solution.c2q) == 0:
            solution.c2p = [0]

        i = 0
        for q in solution.c1q:
            solution.total += q * solution.c1p[i]
            i += 1

        i = 0
        for q in solution.c2q:
            solution.total += q * solution.c2p[i]
            i += 1

        solution.total = round(solution.total * 1.2, 2)

        if solution not in solutions:
            solutions.append(solution)

        print('Obj: %g' % m.objVal)
    j += 1

# Display the results
solutions = sorted(solutions, key=lambda s: s.total, reverse=True)
for s in solutions:
    print(s)
# except gp.GurobiError as e:
#     print('Error code ' + str(e.errno) + ': ' + str(e))
#
# except AttributeError:
#     print('Encountered an attribute error')
