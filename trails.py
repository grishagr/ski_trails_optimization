"""
   Ski Trail Optimization Project
   Grisha Hatavets
   June 9, 2023
"""

from gurobipy import *

# Adjacent vertices list
dir = [[1, 3, 8], [0, 2, 6], [1, 3, 19], [0, 2, 4, 5], [3, 5, 9],
              [3, 4, 15], [1, 7, 19], [6], [0, 9, 10], [4, 8, 10, 16],
              [8, 9, 11], [10, 12, 13, 14, 17, 18], [11], [11, 14], [11, 13, 18],
              [5, 16, 19], [9, 15, 17], [11, 16, 18], [11, 14, 17], [2, 6, 15]]

# Distance to each adjacent vertex
dist = [[5, 9, 9],[5, 3, 19],[3, 5, 22],[9, 5, 3, 6],[3, 3, 9],
        [6, 3, 31],[19, 19, 4],[19],[9, 13, 32],[9, 13, 10, 26],
        [32, 10, 5],[5, 8, 13, 18, 24, 20],[8], [13, 11],[18, 11, 11],
        [31, 4, 43],[26, 4, 2],[24, 2, 2],[20, 11, 2],[22, 4, 43]]

triple = {0 : [1, 3], 1 : [2, 6], 2 : [1, 3, 19], 3 : [0, 2], 6: [1, 19], 8 : [10], 10 : [8], 19 : [2, 6]}

edges = {0 : [1, 3, 8], 8 : [9, 10], 9 : [10, 4, 16], 10 : [11], 11 : [12, 13, 14, 18, 17], 14 : [13, 18], 18 : [17], 17 : [16],
         16 : [15], 15 : [5, 19], 5 : [3, 4], 3 : [4, 2], 2 : [1, 19], 19 : [6], 6 : [7, 1], }

# Model
m = Model("Ski trails")

# Variables
M = 150  #range of possible edges in the path

x = {}
y = {}
for i in range(len(dir)):
    for j in dir[i]:
        for k in range(M):
            x[i,j,k] = m.addVar(vtype = GRB.BINARY) # binary decision variable: 1 if path takes edge i -> j at step k

for i in edges.keys():
    for j in edges[i]: 
        y[i,j] = m.addVar(vtype = GRB.BINARY) # binary decision variable for grooming each edge twice in the same direction:
                                              # 1 if grooming is done one way and 0 if the opposite way is taken
m.update()

# Obj function:

# Minimize distance travelled
m.setObjective(quicksum(x[i,j,k] * dist[i][dir[i].index(j)] for i in range(len(dir)) for j in dir[i] for k in range(M)), GRB.MINIMIZE)

# Constraints: 

# start at vertex 0
m.addConstr(1 == quicksum(x[0,j,0] for j in dir[0]), name = "start")

for k in range(M):
    # 1 edge per step
    m.addConstr(quicksum(x[i,j,k] for i in range(len(dir)) for j in dir[i]) <= 1, name = "1_edge_step")

    # Can't take one uphill edge
    m.addConstr(x[11,13,k] == 0, name = "uphill")
    
for i in range(len(dir)):

    # Circuit (flow in = flow out)
    m.addConstr(quicksum(x[j,i,k] for j in dir[i] for k in range (M)) == quicksum(x[i,j,k] for j in dir[i] for k in range(M)), name = "circuit")
    
    for j in dir[i]:
        # Cover every edge on the map
        m.addConstr(quicksum(x[i,j,k] for k in range(M))  + quicksum(x[j,i,k] for k in range(M)) >= 2, name = "cover all edges")
        
        # No U-turns except for certain vertices
        if (i != 6 or j != 7) and (i != 7 or j != 6) and (i != 11 or j != 12)  and (i != 12 or j != 11) and (i != 13 or j != 14) and (i != 14 or j != 13):
            for k in range(1, M):
                m.addConstr(x[i,j,k-1] + x[j,i,k] <= 1, name = "no u-turns")

        # Cover each edge at least twice
        if (i == 14 and j == 11) or (i == 11 and j == 14):
            m.addConstr(quicksum(x[i,j,k] for k in range(M)) + quicksum(x[j,i,k] for k in range(M)) >= 4, name = "double_edges")
        # at least three times
        if (i in triple.keys() and j in triple[i]) or (j in triple.keys() and i in triple[j]):
            m.addConstr(quicksum(x[i,j,k] for k in range(M)) + quicksum(x[j,i,k] for k in range(M)) >= 3, name = "triple_edges")
        # at least six times
        if (i == 13 and j == 14) or (i == 14 and j == 13):
            m.addConstr(quicksum(x[i,j,k] for k in range(M)) + quicksum(x[j,i,k] for k in range(M)) >= 6, name = "triple_loop")
    
    for k in range(1, M):

        # Sequential flow (step-by-step)
        m.addConstr(quicksum(x[j,i,k-1] for j in dir[i]) - quicksum(x[i,j,k] for j in dir[i]) >= 0, name = "sequential cover / flow")

        # Prohibited turns
        if i == 17:
            m.addConstr(x[i,11,k-1] + x[11,18,k] <= 1)
        if i == 18:
            m.addConstr(x[i,11,k-1] + x[11,17,k] <= 1)
        if i == 2:
            m.addConstr(x[i,1,k-1] + x[1,6,k] <= 1)
        if i == 6:
            m.addConstr(x[i,1,k-1] + x[1,2,k] <= 1)
        if i == 8:
            m.addConstr(x[i,9,k-1] + x[9,4,k] <= 1)
        if i == 4:
            m.addConstr(x[i,9,k-1] + x[9,8,k] <= 1)
        if i == 10:
            m.addConstr(x[i,9,k-1] + x[9,16,k] <= 1)
        if i == 16:
            m.addConstr(x[i,9,k-1] + x[9,10,k] <= 1)

for i in edges.keys():
    for j in edges[i]:
        m.addConstr(quicksum(x[i,j,k] for k in range(M)) + M * y[i,j] >= 2)
        m.addConstr(quicksum(x[j,i,k] for k in range(M)) + M * (1 - y[i,j]) >= 2)

m.update()

m.optimize()

# Prints value of the objective function
obj = m.getObjective()
print(obj.getValue())

# Prints step by step the optimized path
e = {}
sum = 0
for k in range(M):
    for i in range(len(dir)):
        for j in dir[i]:
            if x[i,j,k].X == 1:
                print("from:", i, "to:", j,"at step", k)
                c = str(i) + str(j)
                if c in e.keys():
                    e[c] += 1
                else:
                    e[c] = 1
print(e)

