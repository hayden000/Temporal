import gurobipy as gp
from gurobipy import GRB
import time
import random


def generate_randomized_graph(p_paths, k_length, terminal_config, seed):
    # 1. SET THE RANDOM SEED FOR REPRODUCIBILITY
    random.seed(seed)

    cycle_size = 6
    nodes = set()
    edges = []
    sources = []
    sinks = []

    # 2. GENERATE THE FIXED CYCLE (Size 6)
    cycle_nodes = [f"C{i}" for i in range(cycle_size)]
    for n in cycle_nodes: nodes.add(n)

    for i in range(cycle_size):
        u = cycle_nodes[i]
        v = cycle_nodes[(i + 1) % cycle_size]
        edges.extend([(u, v), (v, u)])

    # 3. DETERMINE TERMINAL TYPES BASED ON CONFIGURATION
    if terminal_config == 'all_sources':
        terminal_assignments = ['source'] * p_paths
    elif terminal_config == 'all_sinks':
        terminal_assignments = ['sink'] * p_paths
    elif terminal_config == '50_50':
        # Exactly half sources (rounded down), rest sinks
        num_sources = p_paths // 2
        terminal_assignments = ['source'] * num_sources + ['sink'] * (p_paths - num_sources)
        random.shuffle(terminal_assignments)  # Shuffle who gets what

    # 4. GENERATE 'p' OUTWARD PATHS OF LENGTH 'k' WITH RANDOM ATTACHMENTS
    for i in range(p_paths):
        attach_node = f"C{random.randint(0, cycle_size - 1)}"
        prev_node = attach_node

        # Build the path of length k
        for step in range(1, k_length + 1):
            curr_node = f"P_{i}_{step}"
            nodes.add(curr_node)
            edges.extend([(prev_node, curr_node), (curr_node, prev_node)])
            prev_node = curr_node

        # Assign the tip of the path based on the shuffled assignments
        tip_node = prev_node
        if terminal_assignments[i] == 'source':
            sources.append(tip_node)
        else:
            sinks.append(tip_node)

    unique_edges = list(set(edges))
    return list(nodes), unique_edges, sources, sinks


def run_massive_grid_search():
    output_filename = "fulldata.csv"

    # 1. INITIALIZE THE CSV FILE WITH HEADERS
    with open(output_filename, "w") as f:
        f.write("Paths_p,Length_k,Config,Seed,Cap_Rule,Actual_Cap,Total_Nodes,Status,Solve_Time_s\n")


    print(
        f"{'p':<4} | {'k':<4} | {'Config':<12} | {'Seed':<4} | {'CapRule':<7} | {'Cap':<3} | {'Nodes':<6} | {'Status':<12} | {'Time (s)'}")


    # 2. define
    p_values = range(4, 16)  # p = 4 to 15
    k_values = range(4, 11)  # k = 4 to 10
    capacity_rules = ['p/3', 'p/2']

    # Configurations: name and random seed
    configurations = [
        ('all_sources', 0),
        ('all_sinks', 0),
        ('50_50', 1),
        ('50_50', 2),
        ('50_50', 3),
        ('50_50', 4),
        ('50_50', 5)
    ]

    # 3. search
    for p in p_values:
        for k in k_values:
            for cap_rule in capacity_rules:
                for config, seed in configurations:

                    # Calculate capacity
                    if cap_rule == 'p/3':
                        label_cap = max(1, p // 3)
                    else:
                        label_cap = max(1, p // 2)

                    # Generate graph
                    nodes, edges, sources, sinks = generate_randomized_graph(p, k, config, seed)

                    # Build Reachability
                    reachability = {}
                    for s in sources:
                        for t in nodes:
                            if s != t: reachability[f'{s} to {t}'] = {'start': s, 'end': t}

                    for s in nodes:
                        for t in sinks:
                            if s != t:
                                route_name = f'{s} to {t}'
                                if route_name not in reachability:
                                    reachability[route_name] = {'start': s, 'end': t}

                    physical_edge = {}
                    ke_shared = {}
                    for (u, v) in edges:
                        pu, pv = tuple(sorted([u, v]))
                        physical_edge[(u, v)] = (pu, pv)
                        ke_shared[(pu, pv)] = label_cap

                    # --- GUROBI MODEL ---
                    m = gp.Model(f"Grid_p{p}_k{k}_{config}_seed{seed}")
                    m.setParam('OutputFlag', 0)
                    m.setParam('TimeLimit', 21600)

                    # Deadline scales with k
                    D = 20 + (2 * k)

                    T = m.addVars(reachability.keys(), nodes, vtype=GRB.INTEGER, lb=0, ub=D)
                    T_max = m.addVar(vtype=GRB.INTEGER, lb=0, ub=D)
                    L = {(pu, pv, cap): m.addVar(vtype=GRB.INTEGER, lb=0, ub=D) for (pu, pv) in ke_shared for cap in
                         range(1, label_cap + 1)}
                    X = {(r, u, v, cap): m.addVar(vtype=GRB.BINARY) for r in reachability for u, v in edges for cap in
                         range(1, label_cap + 1)}

                    m.setObjective(T_max, GRB.MINIMIZE)

                    for r, data in reachability.items():
                        src, snk = data['start'], data['end']
                        m.addConstr(T_max >= T[r, snk])

                        for n in nodes:
                            out_f = gp.quicksum(X[r, u_edge, v_edge, cap]
                                                for u_edge, v_edge in edges if u_edge == n
                                                for cap in range(1, label_cap + 1))
                            in_f = gp.quicksum(X[r, u_edge, v_edge, cap]
                                               for u_edge, v_edge in edges if v_edge == n
                                               for cap in range(1, label_cap + 1))

                            if n == src:
                                m.addConstr(out_f - in_f == 1)
                            elif n == snk:
                                m.addConstr(out_f - in_f == -1)
                            else:
                                m.addConstr(out_f - in_f == 0)

                        for u, v in edges:
                            pu, pv = physical_edge[(u, v)]
                            for cap in range(1, label_cap + 1):
                                m.addConstr(T[r, u] <= L[pu, pv, cap] + (D + 1) * (1 - X[r, u, v, cap]))
                                m.addConstr(T[r, v] >= L[pu, pv, cap] + 1 - (D + 1) * (1 - X[r, u, v, cap]))

                    m.optimize()

                    # Extract results
                    runtime = m.Runtime
                    status = "Unknown"
                    if m.Status == GRB.OPTIMAL:
                        status = "Optimal"
                    elif m.Status == GRB.INFEASIBLE:
                        status = "Infeasible"
                    elif m.Status == GRB.TIME_LIMIT:
                        status = "Timeout(6h)"
                    elif m.SolCount > 0:
                        status = "Sub-Optimal"


                    print(
                        f"{p:<4} | {k:<4} | {config:<12} | {seed:<4} | {cap_rule:<7} | {label_cap:<3} | {len(nodes):<6} | {status:<12} | {runtime:.2f}")


                    csv_row = f"{p},{k},{config},{seed},{cap_rule},{label_cap},{len(nodes)},{status},{runtime:.2f}"
                    with open(output_filename, "a") as f:
                        f.write(csv_row + "\n")


if __name__ == '__main__':
    run_massive_grid_search()
