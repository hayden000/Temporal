import gurobipy as gp
from gurobipy import GRB


def solvetempoal():
    nodes = []
    edges = []
    ke = []

    def example1():
        nodes = ['Source', 'A', 'B', 'Sink']
        edges = [('Source', 'A'), ('Source', 'B'), ('A', 'B'), ('B', 'A'), ('A', 'Sink'), ('B', 'Sink')]
        ke = {('Source', 'A'): 1, ('Source', 'B'): 1, ('A', 'B'): 2, ('B', 'A'): 2, ('A', 'Sink'): 1, ('B', 'Sink'): 1}

    def example2():
        nodes = ['Source', 'N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 'Sink']
        edges = [('Source', 'N1'), ('Source', 'N2'), ('N1', 'N3'), ('N1', 'N4'), ('N2', 'N3'), ('N2', 'N5'),
                 ('N3', 'N6'), ('N4', 'N7'), ('N4', 'N6'), ('N5', 'N8'), ('N5', 'N6'), ('N6', 'N7'), ('N6', 'N8'),
                 ('N7', 'Sink'), ('N8', 'Sink')]
        ke = {('Source', 'N1'): 1, ('Source', 'N2'): 1, ('N1', 'N3'): 1, ('N1', 'N4'): 1, ('N2', 'N3'): 1,
              ('N2', 'N5'): 1, ('N3', 'N6'): 3, ('N4', 'N7'): 1, ('N4', 'N6'): 1, ('N5', 'N8'): 1, ('N5', 'N6'): 1,
              ('N6', 'N7'): 2, ('N6', 'N8'): 2, ('N7', 'Sink'): 2, ('N8', 'Sink'): 2}

    def example3():
        nodes = ['Source', 'N1', 'N2', 'Sink', 'N3']
        edges = [('Source', 'N1'), ('N1', 'Source'), ('N1', 'N2'), ('N2', 'N1'), ('N2', 'Sink'), ('Sink', 'N2'),
                 ('Sink', 'N3'), ('N3', 'Sink'), ('N3', 'Source'), ('Source', 'N3')]
        ke = {('Source', 'N1'): 1, ('N1', 'Source'): 1, ('N1', 'N2'): 1, ('N2', 'N1'): 1, ('N2', 'Sink'): 1,
              ('Sink', 'N2'): 1, ('Sink', 'N3'): 1, ('N3', 'Sink'): 1, ('N3', 'Source'): 1, ('Source', 'N3'): 1}

    def example4():
        nodes = ['Source', 'N1', 'N2', 'N3', 'Sink', 'N4', 'N5', 'N6']
        edges = [('Source', 'N1'), ('N1', 'Source'), ('N1', 'N2'), ('N2', 'N1'), ('N2', 'N3'), ('N3', 'N2'),
                 ('N3', 'Sink'), ('Sink', 'N3'), ('Sink', 'N4'), ('N4', 'Sink'), ('N4', 'N5'), ('N5', 'N4'),
                 ('N5', 'N6'), ('N6', 'N5'), ('N6', 'Source'), ('Source', 'N6')]
        ke = {('Source', 'N1'): 2, ('N1', 'Source'): 2, ('N1', 'N2'): 2, ('N2', 'N1'): 2, ('N2', 'N3'): 2,
              ('N3', 'N2'): 2, ('N3', 'Sink'): 2, ('Sink', 'N3'): 2, ('Sink', 'N4'): 2, ('N4', 'Sink'): 2,
              ('N4', 'N5'): 2, ('N5', 'N4'): 2, ('N5', 'N6'): 2, ('N6', 'N5'): 2, ('N6', 'Source'): 2,
              ('Source', 'N6'): 2}


    nodes = ['Source1', 'Source2', 'Sink1', 'Sink2', 'Hub_L', 'Hub_C', 'Hub_R', 'L1', 'L2', 'R1', 'R2']

    connections = [
        ('Source1', 'Hub_L'), ('Source2', 'Hub_R'),
        ('Hub_L', 'Hub_C'), ('Hub_C', 'Hub_R'),
        ('Hub_L', 'Sink1'), ('Hub_R', 'Sink2'),
        ('Sink1', 'L1'), ('L1', 'L2'),
        ('Sink2', 'R1'), ('R1', 'R2')
    ]

    # ke = {
    #     ('Source1', 'Hub_L'): 5, ('Source2', 'Hub_R'): 5,
    #     ('Hub_L', 'Hub_C'): 5, ('Hub_C', 'Hub_R'): 5,
    #     ('Hub_L', 'Sink1'): 5, ('Hub_R', 'Sink2'): 5,
    #     ('Sink1', 'L1'): 5, ('L1', 'L2'): 5,
    #     ('Sink2', 'R1'): 5, ('R1', 'R2'): 5
    # }
    ke = {
        ('Source1', 'Hub_L'): 3, ('Source2', 'Hub_R'): 3,
        ('Hub_L', 'Hub_C'): 3, ('Hub_C', 'Hub_R'): 3,
        ('Hub_L', 'Sink1'): 3, ('Hub_R', 'Sink2'): 3,
        ('Sink1', 'L1'): 3, ('L1', 'L2'): 3,
        ('Sink2', 'R1'): 3, ('R1', 'R2'): 3
    }
    # ke = {
    #     ('Source1', 'Hub_L'): 2, ('Source2', 'Hub_R'): 2,
    #     ('Hub_L', 'Hub_C'): 2, ('Hub_C', 'Hub_R'): 2,
    #     ('Hub_L', 'Sink1'): 2, ('Hub_R', 'Sink2'): 2,
    #     ('Sink1', 'L1'): 2, ('L1', 'L2'): 2,
    #     ('Sink2', 'R1'): 2, ('R1', 'R2'): 2
    # }

    reachability = {}
    source_nodes = ['Source1', 'Source2']
    sink_nodes = ['Sink1', 'Sink2']

    for s in source_nodes:
        for n in nodes:
            if n != s:
                reachability[f'{s} to {n}'] = {'start': s, 'end': n}

    for target_sink in sink_nodes:
        for n in nodes:
            if n != target_sink:
                reachability[f'{n} to {target_sink}'] = {'start': n, 'end': target_sink}

    # def single():
    #     reachability = {}
    #     for n in nodes:
    #         if n != 'Source':
    #             reachability[f'source to {n}'] = {'start': 'Source', 'end': n}
    #     for n in nodes:
    #         if n != 'Sink':
    #             reachability[f'{n} to sink'] = {'start': n, 'end': 'Sink'}

    edges = []
    physical_edge = {}
    ke_shared = {}

    for (u, v), cap in ke.items():
        pu, pv = sorted([u, v])
        ke_shared[(pu, pv)] = cap

    for u, v in connections:
        edges.append((u, v))
        edges.append((v, u))

        pu, pv = sorted([u, v])
        physical_edge[(u, v)] = (pu, pv)
        physical_edge[(v, u)] = (pu, pv)

    m = gp.Model("temporal")
    # m.setParam('OutputFlag', 0)

    T = m.addVars(reachability.keys(), nodes, vtype=GRB.INTEGER, lb=0, name="T")
    T_max = m.addVar(vtype=GRB.INTEGER, lb=0, name="T_max")

    L = {}
    for pu, pv in ke_shared.keys():
        for k in range(1, ke_shared[(pu, pv)] + 1):
            L[pu, pv, k] = m.addVar(vtype=GRB.INTEGER, lb=0, name=f"L_{pu}_{pv}_{k}")

    timeallocations = {}
    for r in reachability:
        for u, v in edges:
            pu, pv = physical_edge[(u, v)]
            for k in range(1, ke_shared[(pu, pv)] + 1):
                timeallocations[r, u, v, k] = m.addVar(vtype=GRB.BINARY, name=f"X_{r}_{u}_{v}_{k}")

    m.setObjective(T_max, GRB.MINIMIZE)
    MaxDeadline = 30
    for r, data in reachability.items():
        src = data['start']
        snk = data['end']
        m.addConstr(T[r, src] >= 0, name="Start time is 0")
        m.addConstr(T_max >= T[r, snk], name=f"Deadline is {r}")
        for n in nodes:
            out_flow = gp.quicksum(
                timeallocations[r, u, v, k] for u, v in edges if u == n for k in
                range(1, ke_shared[physical_edge[(u, v)]] + 1))
            in_flow = gp.quicksum(
                timeallocations[r, u, v, k] for u, v in edges if v == n for k in
                range(1, ke_shared[physical_edge[(u, v)]] + 1))
            if n == src:
                m.addConstr(out_flow - in_flow == 1)
            elif n == snk:
                m.addConstr(out_flow - in_flow == -1)
            else:
                m.addConstr(out_flow - in_flow == 0)
        for u, v in edges:
            pu, pv = physical_edge[(u, v)]
            for k in range(1, ke_shared[(pu, pv)] + 1):
                m.addConstr(T[r, u] <= L[pu, pv, k] + MaxDeadline * (1 - timeallocations[r, u, v, k]))
                m.addConstr(T[r, v] >= L[pu, pv, k] + 1 - MaxDeadline * (1 - timeallocations[r, u, v, k]))

    m.optimize()

    if m.Status == GRB.OPTIMAL:
        print(f"\n Deadline is {int(T_max.X)}")

        for u, v in edges:
            pu, pv = physical_edge[(u, v)]
            labels = []
            for k in range(1, ke_shared[(pu, pv)] + 1):
                if sum(timeallocations[r, u, v, k].X for r in reachability) > 0.5:
                    labels.append(int(L[pu, pv, k].X))

            if labels:
                print(f"{u} , {v} at {set(labels)}")


solvetempoal()

