import math
from collections import defaultdict

def distribute(
    random_state, capacity, remaining_quantity
):
    """A method to distribute the remaining arcs across the nodes. It is intended to have
    an alternative ways to distribute the arcs."""
    allocation = defaultdict(int)
    for k, v in list(capacity.items()):
        if v == 0:
            capacity.pop(k)
    for _ in range(remaining_quantity):
        select_node = random_state.choice(list(capacity.keys()))
        allocation[select_node] += 1
        capacity[select_node] -= 1
        if capacity[select_node] == 0:
            capacity.pop(select_node)
    return allocation

def determine_order(distances):
    return [], {}

def left_arc_vacancies(graph, order, ):
    position_in_order = {i: pos for pos, i in enumerate(order)}
    return {v: graph.number_of_nodes() - 1 - pos - sum(1 for u in graph.predecessors(v) if position_in_order[v] > position_in_order[u]) 
    for pos, v in enumerate(order)}
    
def right_arc_vacancies(graph, order):
    position_in_order = {i: pos for pos, i in enumerate(order)}
    return {v: graph.number_of_nodes() - 1 - pos - sum(1 for u in graph.predecessors(v) if position_in_order[v] < position_in_order[u]) 
    for pos, v in enumerate(order)}

def determine_arc_vacancies(graph,order):
    return {
        "left": left_arc_vacancies(graph, order),
        "right": right_arc_vacancies(graph, order)
    }

def determine_arcs_to_add(total, r, arc_vacancies):
    arcs_to_add = {"negative" : min(
        math.floor(r*(total)), 
        sum(arc_vacancies["left"].values())
    )}
    arcs_to_add["positive"] = arcs_to_add["total"] - arcs_to_add["negative"]
    return arcs_to_add


def allocate_predecessors_to_nodes(random_state, graph, arc_vacancies, arcs_to_add):
    allocation = {
        "negative": distribute(
        random_state,
        arc_vacancies["left"],
        arcs_to_add["negative"]
    )}
    allocation["positive"] = distribute(
        random_state,
        {i: sum(arc_vacancies[d].get(i, 0) for d in ["left", "right"]) for i in graph.nodes()},
        arcs_to_add["positive"]
    )
    return allocation


def gen_remaining_arcs(
    random_state,
    graph,
    distances,
    n,
    m,
    r,
):
    """With respect to the ordering, negative arcs can only be added from right to left otherwise will
    definitely update the tree

    position      0           1          2          3           4           5            6
    node_id       5           1          4          0           6           2            3
    distance     -20         -12        -8          0           3           3            10
                                <---------(-12)------
                                --------------------15---------------------->
                                                                            -------7----->
                                          <-------------------------(-18)------------------                                                             
                 <-----------(-12)------------
                 ------------------------23----------------------->

    a negative arc must be left (←)
    a positive arc can be left or right (← or →) 
    a right arc must be positive
    """
    order = determine_order(distances)
    arc_vacancies = determine_arc_vacancies(graph, order)
    arcs_to_add = determine_arcs_to_add(m - graph.number_of_arcs(), r, arc_vacancies)
    allocation = allocate_predecessors_to_nodes(random_state, graph, arc_vacancies, arcs_to_add)
    # Generate predecessors
    for pos, v in enumerate(order):
        nb_neg = allocation["negative"].get(v, 0)
        nb_pos = allocation["positive"].get(v, 0)
        nb_pos_to_the_left = random_state.randint(
            allocation["positive"][v] - arc_vacancies["right"][v], # The minimum that ensures the right does not overflow
            arc_vacancies["left"][v]                              # The nb_neg has already been subtracted
            )
        nb_to_the_left = nb_neg + nb_pos_to_the_left
        nb_to_the_right = nb_pos - nb_pos_to_the_left
        # Generate to the left
        if nb_to_the_left > 0:
            samples = random_state.sample(range(pos+1, n), min(n-1-pos,nb_to_the_right+2))
            count = 0
            random_state.shuffle(samples)   # NOTE: Required for completeness
            for s in samples:
                u = order[s][0]
                if u not in graph.predecessors[v]:
                    is_negative = count < nb_neg
                    count += 1
                    yield (u, v, is_negative)
                if count == nb_to_the_left:
                    break
        # Generate to the left
        if nb_to_the_right > 0:
            samples = random_state.sample(range(pos), min(pos, nb_to_the_left+2))
            count = 0
            for s in samples:
                u = order[s][0]
                if u not in graph.predecessors[v]:
                    count += 1
                    yield u, v, False           
                if count == nb_to_the_right:
                    break