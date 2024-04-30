from helper import initial_state_a_star, h_a_star, generate_next_states_a_star, cost_solution, try_make_it_work
import utils

def a_star(data):
    # tuple with vars for state, subjects and students unallocated and how busy the teachers are
    initial_state, sub_stud_unallocated, teacher_xbusy = initial_state_a_star(data)
    # tuple showing the h cost and also how many soft constraints are breached
    soft_not_respected, cost_initial_state = h_a_star(initial_state, sub_stud_unallocated, teacher_xbusy, data)
    # open and closed sets presented in the original algorithm
    open_nodes = []
    closed_nodes = []
    first_iter = True
    sum_f_lambda = lambda x: x[3]
    # retain best_state to know what to return if found
    # a timetable respecting all hard constraints but not soft ones
    best_state = None
    cost_best_state = 99999999999
    generated_states_ret = 0
    open_nodes.append((initial_state, sub_stud_unallocated, teacher_xbusy, cost_initial_state, 0))
    max_iters = 20000
    # vars to help algorithm in such a way that will try to find
    # a valid timetable at all costs after iterations will exceed
    best_state_hard_not_good = None
    cost_best_state_hard_not_good = 99999
    stud_not_allocated = 999999
    hard_sub_stud_remained = None
    hard_teacher_work_volume = None
    while len(open_nodes) != 0 and max_iters > 0:
        max_iters -= 1
        state, sub_stud_remained, teacher_work_volume, h, g = min(open_nodes, key=sum_f_lambda)
        open_nodes.remove((state, sub_stud_remained, teacher_work_volume, h, g))
        closed_nodes.append((state, sub_stud_remained, teacher_work_volume, h, g))
        # decide if the state is worth it and has a little chance of
        # resulting into a valid state
        subject_available_space = {x[0]: 0 for x in sub_stud_remained}
        total_available = 0
        for day in data[utils.ZILE]:
            for interval in data[utils.INTERVALE]:
                for classroom, _ in data[utils.SALI].items():
                    if state[day][interval][classroom] != (0, 0):
                        continue
                    total_available += data[utils.SALI][classroom]['Capacitate']
                    for subject in data[utils.SALI][classroom]['Materii']:
                        if subject not in subject_available_space:
                            continue
                        subject_available_space[subject] += data[utils.SALI][classroom]['Capacitate']
        total_wanted = 0
        move_on = 0
        for subj, stud in sub_stud_remained:
            total_wanted += stud
            if subject_available_space[subj] < stud:
                move_on = 1
                break
        if total_wanted > total_available:
            move_on = 1
        if move_on == 1:
            continue
        # when I could not find a solution, it may be students unallocated
        # and this is a hard constraint, so I memorise the best solution
        # with least soft constraints not respecteds
        if len(sub_stud_remained) == 0 and h < cost_best_state:
            best_state = state
            cost_best_state = h
        # if I have no other choice, or is a final state, or it is not worth as this
        # abuse the memory, return what I have best
        if (len(open_nodes) == 0 and first_iter == False) or h == 0 or len(open_nodes) > 10000000:
            if len(sub_stud_remained) != 0:
                cost_ret = cost_solution(best_state, data)
                return best_state, cost_ret, cost_ret == 0, generated_states_ret
            return state, h, h == 0, generated_states_ret
        # if found a good state without all the hard constraints respected, memorise it
        if h < cost_best_state_hard_not_good and stud_not_allocated > sum(x[1] for x in sub_stud_remained):
            best_state_hard_not_good = state
            cost_best_state_hard_not_good = h
            stud_not_allocated = sum(x[1] for x in sub_stud_remained)
            hard_sub_stud_remained = sub_stud_remained
            hard_teacher_work_volume = teacher_work_volume
        first_iter = False
        successors = generate_next_states_a_star(state, sub_stud_remained, teacher_work_volume, data)
        generated_states_ret += len(successors)
        # help algorithm decide wether to put in list some next states or not
        # if there is at least one respecting all the soft constraints
        # until now, those breaching them will not be added to the list
        ok = 0
        for succ_state, succ_sub_stud_remained, succ_teacher_work_volume in successors:
            soft_not_respected, succ_h = h_a_star(succ_state, succ_sub_stud_remained, succ_teacher_work_volume, data)
            if soft_not_respected == 0:
                ok = 1
        max_n = 10
        for succ_state, succ_sub_stud_remained, succ_teacher_work_volume in successors:
            soft_not_respected, succ_h = h_a_star(succ_state, succ_sub_stud_remained, succ_teacher_work_volume, data)
            # if found a state that only breaches soft constraints, retain it
            # it may be the best one
            if soft_not_respected == succ_h:
                if cost_best_state > succ_h:
                    best_state = succ_state
                    cost_best_state = succ_h
                    continue
            # found a valid state with all constraints good, return state
            if soft_not_respected == succ_h and succ_h == 0:
                return succ_state, succ_h, succ_h == 0, generated_states_ret
            if max_n < 0:
                continue
            if soft_not_respected > 0 and ok == 1:
                continue
            succ_g = g + 1
            ok = 1
            for aux in open_nodes:
                if aux[0] == succ_state:
                    ok = 0
                    if aux[3] > succ_h:
                        open_nodes.remove(aux)
                        open_nodes.append((succ_state, succ_sub_stud_remained, succ_teacher_work_volume, succ_h, succ_g))
            if ok == 0:
                continue
            # for aux in closed_nodes:
            #     if aux[0] == succ_state:
            #         ok = 0
            # if ok == 0:
            #     continue
            open_nodes.append((succ_state, succ_sub_stud_remained, succ_teacher_work_volume, succ_h, succ_g))
            max_n -= 1
    # if no state with hard respected, try to make it follow them regardless of the number
    # of soft constraints breached
    if best_state is None:
        if best_state_hard_not_good is None:
            return {}, 9999, False, generated_states_ret
        else:
            res_trying = try_make_it_work(best_state_hard_not_good, hard_sub_stud_remained, hard_teacher_work_volume, data)
            if res_trying is not None:
                return res_trying, cost_solution(res_trying, data), cost_solution(res_trying, data) == 0, generated_states_ret
            return best_state_hard_not_good, cost_best_state_hard_not_good, False, generated_states_ret
    # return what I found best
    return best_state, cost_best_state, cost_best_state == 0, generated_states_ret