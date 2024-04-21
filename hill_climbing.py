from helper import get_random_state
from helper import get_next_states, get_next_states_as_tuples
from helper import cost_solution
from copy import deepcopy
import numpy as np

def hill_climbing(state, cost, data, max_iters):
    if cost == 0:
        return state, 0, True
    best = state
    best_cost = cost
    ok = True
    iters = 0
    while ok is True and max_iters > iters:
        next_states = get_next_states(state, data)
        for possible_next_state in next_states:
            possible_next_cost = cost_solution(possible_next_state, data)
            if cost > possible_next_cost:
                state = possible_next_state
                cost = possible_next_cost
        if best_cost > cost:
            best_cost = cost
            best = state
        else:
            ok = False
        iters += 1
        if best_cost == 0:
            ok = False
    return best, best_cost, best_cost == 0

def hill_climbing_with_tuples(state, cost, data, max_iters):
    if cost == 0:
        return state, 0, True
    best = state
    best_cost = cost
    ok = True
    iters = 0
    while ok is True and max_iters > iters:
        next_states = get_next_states_as_tuples(state, data)
        for possible_next_state_tuples in next_states:
            tuple1 = possible_next_state_tuples[0]
            tuple2 = possible_next_state_tuples[1]
            new_state = deepcopy(state)
            aux = new_state[tuple1[0]][tuple1[1]][tuple1[2]]
            new_state[tuple1[0]][tuple1[1]][tuple1[2]] =\
                new_state[tuple2[0]][tuple2[1]][tuple2[2]]
            new_state[tuple2[0]][tuple2[1]][tuple2[2]] = aux
            possible_next_cost = cost_solution(new_state, data)
            if cost > possible_next_cost + 2:
                state = new_state
                cost = possible_next_cost
                break
            if cost > possible_next_cost:
                state = new_state
                cost = possible_next_cost
        if best_cost > cost:
            best_cost = cost
            best = state
        else:
            ok = False
        iters += 1
        if best_cost == 0:
            ok = False
    return best, best_cost, best_cost == 0

def softmax(x: np.array) -> float:
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()

def simmulated_annealing(initial_state, t_init, t_final, cooling, alpha, max_iters, data):
    state = initial_state
    cost_state = cost_solution(state, data)
    t = t_init
    iters = 0

    while t > t_final and iters < max_iters:
        print(cost_state)
        if cost_state == 0:
            return state, cost_state, True
        next_states = get_next_states(state, data)
        scores = [cost_solution(st, data) for st in next_states]
        softmax_scores = softmax(-np.array(scores))
        next_state_index = np.random.choice(len(next_states), p=softmax_scores)
        next_state = next_states[next_state_index]
        next_cost = cost_solution(next_state, data)
        if next_cost < cost_state:
            state = next_state
            cost_state = next_cost
        else:
            delta = cost_state - next_cost
            if np.random.rand() < np.exp(delta / (t * alpha)):
                state = next_state
                cost_state = next_cost
        t = t * cooling
    
    return state, cost_state, cost_state == 0

def random_restart_hill_climbing(data, max_restarts):
    is_final = False
    state = {}
    cost = 9999999
    # a counter that retain the number
    # of times the computation of a initial state
    # fails
    failed_count = 0
    already_used_states = set()
    while max_restarts:
        if failed_count == 300:
            break
        initial_state = get_random_state(data)
        if initial_state == {}:
            failed_count += 1
            continue
        cost_initial_state = cost_solution(initial_state, data)
        if cost_initial_state >= 40:
            #print(f'Costul care nu mi convine este {cost_initial_state}')
            continue
        state_aux, cost_aux, is_final = hill_climbing_with_tuples(initial_state,\
                                cost_initial_state,\
                                data, 3000)
        #state_aux, cost_aux, is_final = simmulated_annealing(initial_state, 1000., 1., 0.995, 0.02, 150, data)
        if cost_aux < cost:
            cost = cost_aux
            state = state_aux
        if is_final is True:
            return state, cost, is_final
        max_restarts -= 1
    return state, cost, is_final