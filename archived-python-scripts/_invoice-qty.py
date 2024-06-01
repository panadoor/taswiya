# Formulate and solve the following a MIP model to find optimal quantities
# and prices to match a given invoice amount. Given 2 product categories: c1 and c2
#  Minimize
#        amount - Sum(c1qi * c1pi) - Sum(c2qi * c2pi)
#        ideally the above should be 0
#  subject to
#        q (quantity) must be positive
#        p (price) must be within a certain range and must have 2 decimals max
#        x, y, z binary
# Gurobi - License Expired
# https://support.gurobi.com/hc/en-us/articles/360038967271-How-do-I-renew-my-free-individual-academic-or-free-trial-license-
#

import gurobipy as gp
from gurobipy import GRB, quicksum

try:
    amountTTC = 25000
    # -(6 * 165 * 1.2)
    print(amountTTC)

    # Multiply by 100 and reduce 20% VAT from the amount
    amount = amountTTC * 100 / 1.2

    # Product Category 1 lower bound price
    pc1lb = 180 * 100
    # Product Category 1 upper bound price
    pc1ub = 180.9 * 100

    # Product Category 2 lower bound price
    pc2lb = 180 * 100
    # Product Category 2 lower bound price
    pc2ub = 181 * 100

    # Number of products in category 1
    c1count = 2
    # Number of products in category 2
    c2count = 2
    # Create a new model
    m = gp.Model("optimize-qty-price")

    # Create variables for category 1
    c1q = m.addVars((i for i in range(c1count)), vtype=GRB.INTEGER, name="c1q", lb=0)
    c1p = m.addVars((i for i in range(c1count)), vtype=GRB.INTEGER, name="c1p", lb=pc1lb, ub=pc1ub)

    # Create variables for category 2
    c2q = m.addVars((i for i in range(c2count)), vtype=GRB.INTEGER, name="c2q", lb=0)
    c2p = m.addVars((i for i in range(c2count)), vtype=GRB.INTEGER, name="c2p", lb=pc2lb, ub=pc2ub)

    # Set objective
    expr = amount - quicksum(c1q[i]*c1p[i] for i in c1q) - quicksum(c2q[i]*c2p[i] for i in c2q)
    m.setObjective(expr, GRB.MINIMIZE)

    # Without this constraint the Model is unbounded
    m.addConstr(expr >= 0, "c1")
    m.addConstr(expr <= 0.9, "c2")

    # Want c1q[i], c2q[j] to be strictly integers
    # Want c1p[i], c2p[j] to only have 2 decimal digits
    # e.g., A value of c1p[0] = 200.124 is NOT allowed 200.12 is ok.
    # These are prices to use in invoices
    # and accounting and must have 2 decimals only

    # Optimize model
    m.Params.NonConvex = 2
    #m.Params.IntegralityFocus = 1
    #m.Params.MIRCuts = -1
    m.Params.MIPFocus = 2  # Focus on providing Optimality
    m.optimize()

    # Display the results
    total = 0
    print('{:<41}{:<36}'.format('Qty', 'Price'))
    for i in range(c1count):
        print('{:<6} = {:<30}  {:<6} = {:<30}'.format(c1q[i].varName, c1q[i].x, c1p[i].varName, c1p[i].x /100))
        total += c1q[i].x * c1p[i].x

    for i in range(c2count):
        print('{:<6} = {:<30}  {:<6} = {:<30}'.format(c2q[i].varName, c2q[i].x, c2p[i].varName, c2p[i].x / 100 ))
        total += c2q[i].x * c2p[i].x

    print('Total: %s' % (total / 100 * 1.2))

    print('Obj: %g' % m.objVal)

except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ': ' + str(e))

except AttributeError:
    print('Encountered an attribute error')