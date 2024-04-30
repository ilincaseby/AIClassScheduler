from helper import get_random_state
from helper import get_next_states, get_next_states_as_tuples
from helper import cost_solution
from copy import deepcopy
import numpy as np
import random

# An alternative for hill_climbing_with_tuples
# NOT RECOMMENDED AS IT'S VERY SLOW COMPARED TO
# THE MENTIONED FUNCTION
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

# Efficient function that tries to find
# next states better than the actual.
def hill_climbing_with_tuples(state, cost, data, max_iters):
    generated_states = 0
    if cost == 0:
        return state, 0, True, 0
    best = state
    best_cost = cost
    ok = True
    iters = 0
    while ok is True and max_iters > iters:
        # generate pairs that can be used for switch
        next_states = get_next_states_as_tuples(state, data)
        random.shuffle(next_states)
        first_cost = cost
        for possible_next_state_tuples in next_states:
            # create state from a pair
            tuple1 = possible_next_state_tuples[0]
            tuple2 = possible_next_state_tuples[1]
            new_state = deepcopy(state)
            aux = new_state[tuple1[0]][tuple1[1]][tuple1[2]]
            new_state[tuple1[0]][tuple1[1]][tuple1[2]] =\
                new_state[tuple2[0]][tuple2[1]][tuple2[2]]
            new_state[tuple2[0]][tuple2[1]][tuple2[2]] = aux
            possible_next_cost = cost_solution(new_state, data)
            generated_states += 1
            # if cost is reduced by a sufficient amount, do not lose
            # time trying to find soemthing even better, very low chances
            if first_cost >= possible_next_cost + 2:
                state = new_state
                cost = possible_next_cost
                break
            # find something better, retain it
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
    # return best I could find
    return best, best_cost, best_cost == 0, generated_states

def random_restart_hill_climbing(data, max_restarts):
    is_final = False
    state = {}
    cost = 9999999
    # a counter that retain the number
    # of times the computation of a initial state
    # fails
    failed_count = 0
    generated_states = 0
    already_used_states = set()
    while max_restarts:
        if failed_count == 300:
            break
        initial_state = get_random_state(data)
        generated_states += 1
        if initial_state == {}:
            failed_count += 1
            continue
        cost_initial_state = cost_solution(initial_state, data)
        # if cost is very high, very low chances to obtain something good
        if cost_initial_state >= 45:
            continue
        state_aux, cost_aux, is_final, aux_states_generated = hill_climbing_with_tuples(initial_state,\
                                cost_initial_state,\
                                data, 3000)
        generated_states += aux_states_generated
        if cost_aux < cost:
            cost = cost_aux
            state = state_aux
        if is_final is True:
            return state, cost, is_final, generated_states
        max_restarts -= 1
    return state, cost, is_final, generated_states