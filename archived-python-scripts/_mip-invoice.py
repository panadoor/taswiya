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
import pandas as pd

# try:
amount = 26500
# Reduce 20% VAT from the amount
amount /= 1.2

amountTolerance = 0.01

# Product Category 1 lower bound price
pc1lb = 180
# Product Category 1 upper bound price
pc1ub = 180.3

# Product Category 2 lower bound price
pc2lb = 200
# Product Category 2 lower bound price
pc2ub = 200.3

@dataclass
class Solution:
    # idx: int
    c1q: int
    c1p: float
    c2q: int
    c2p: float
    total: float


def getPrices(lb, ub):
    i = lb
    prices = []
    while (i <= ub):
        prices.append(i)
        i = round(i + 0.01, 2)
    return prices

solutions = []

pc1prices = getPrices(pc1lb, pc1ub)
pc2prices = getPrices(pc2lb, pc2ub)
# print(pc2prices)

prices = [(c1p, c2p) for c1p in pc1prices for c2p in pc2prices]  # The cartesian product
print('Prices cartesian product - length:', len(prices))

# Number of products in category 1
c1count = 3
# Number of products in category 2
c2count = 3
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

# Create variable for category 1 product quantity
c1q = m.addVar(vtype=GRB.INTEGER, name="c1q", lb=0)

# Create variable for category 2 product quantity
c2q = m.addVar(vtype=GRB.INTEGER, name="c2q", lb=0)

j = 0
for (c1p, c2p) in prices:
    print('%s -> c1p: %s - c2p: %s' % (j, c1p, c2p))
    # m.reset(0)

    # Set objective
    expr = amount - c1q * c1p - c2q * c2p
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
            c1q=c1q.x,
            c1p=c1p,
            c2q=c2q.x,
            c2p=c2p,
            total=0
        )

        if solution.c1q == 0:
            solution.c1p = 0

        if solution.c2q == 0:
            solution.c2p = 0

        solution.total += (solution.c1q * solution.c1p) + (solution.c2q * solution.c2p)
        solution.total = round(solution.total * 1.2, 2)

        if solution not in solutions:
            solutions.append(solution)

        print('Obj: %g' % m.objVal)
    j += 1

# Display the results
solutions = sorted(solutions, key=lambda s: s.total, reverse=True)
for s in solutions:
    print(s)

df = pd.DataFrame(solutions)
print(df)

df.to_excel(r'results.xlsx', index=False)

# except gp.GurobiError as e:
#     print('Error code ' + str(e.errno) + ': ' + str(e))
#
# except AttributeError:
#     print('Encountered an attribute error')
