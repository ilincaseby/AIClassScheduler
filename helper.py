import utils
import re
import random
from copy import deepcopy
import numpy as np
import ast
import statistics

def get_break(constraints):
    key_word = 'Pauza'
    for constraint in constraints:
        if key_word in constraint:
            return constraint
    return ''

def cost_solution(solution, data):
    '''
    Based on solution presented, return an estimated 'cost'
    for having it as a final solution(i.e. soft constraints not respected)
    '''
    days = data[utils.ZILE]
    intervals = data[utils.INTERVALE]
    teachers = data[utils.PROFESORI]
    # the next dict will have the following structure:
    # {teacher_name: [(day1, '8-10'), (day3, '12-14'), ...]}
    teachers_working_plan = {}
    cost_ret = 0
    for day in days:
        for interval in intervals:
            tuple_interval = ast.literal_eval(interval)
            dict_classes = solution[day][interval]
            for _, class_prof in dict_classes.items():
                if class_prof == (0, 0):
                    continue
                teacher_name = class_prof[1]
                if teacher_name not in teachers_working_plan:
                    teachers_working_plan[teacher_name] = []
                teachers_working_plan[teacher_name].append((day,\
                                        str(tuple_interval[0]) + '-' + str(tuple_interval[1])))
    # iterate through the whole program and notice if
    # a constraint is not respected
    for teacher_name, list_plan in teachers_working_plan.items():
        teacher = teachers[teacher_name]
        t_constraints = teacher[utils.CONSTRANGERI]
        break_cond = get_break(t_constraints)
        positive_break = True
        number_hours_break = 0
        # if the break constraint appear
        # parse it
        if break_cond != '':
            if '!' in break_cond:
                positive_break = False
            match = re.search(r'\d+', break_cond)
            number_hours_break = int(match.group())
        # break the intervals un/wanted in intervals
        # with 2 hours appart(e.g. '10-14' -> '10-12', '12-14')
        for i in range(len(list_plan)):
            if '!' + list_plan[i][0] in t_constraints:
                cost_ret += 1
            if '!' + list_plan[i][1] in t_constraints:
                cost_ret += 1
            if break_cond == '' or i == 0:
                continue
            if list_plan[i][0] != list_plan[i - 1][0]:
                continue
            end_past_course = [int(num) for num in list_plan[i - 1][1].split('-')][1]
            start_current_course = [int(num) for num in list_plan[i][1].split('-')][0]
            break_duration = start_current_course - end_past_course
            if positive_break == False and break_duration > number_hours_break:
                cost_ret += 1
            if positive_break == True and break_duration < number_hours_break:
                cost_ret += 1
    return cost_ret

def get_subject_classrooms(data, subject):
    '''
    Return a list of tuples (x, y);
    where x is the name of a classroom where subject can be acquired
    and y are its properties(capacity and subjects possible to be discussed)
    '''
    classrooms = []
    for class_name, properties in data[utils.SALI].items():
        if subject in properties[utils.MATERII]:
            classrooms.append((class_name, properties))
    return classrooms

def get_subject_teachers_available(data, subject, solution, day_interval_class,\
                                   teachers_and_intervals):
    res = []
    # get available teacher that can teach the subject
    for teacher_name, properties in data[utils.PROFESORI].items():
        if subject not in properties['Materii']:
            continue
        ok = 1
        for _, class_ in solution[day_interval_class[0]][day_interval_class[1]].items():
            name = class_[1]
            if name == teacher_name:
                ok = 0
                break
        if ok == 1 and teachers_and_intervals[teacher_name] < 7:
            res.append(teacher_name)
    return res

def get_all_teachers(data):
    # get all teachers from data and put a 0 for each
    # as these will be working times
    res = {}
    for teacher_name, _ in data[utils.PROFESORI].items():
        if teacher_name not in res:
            res[teacher_name] = 0
    return res

def get_teachers_qualified(data, teachers_and_intervals, subject):
    ans = []
    # get teachers licensed for the subject mentioned
    for teacher, interval in list(filter(lambda value: value[1] < 7, teachers_and_intervals.items())):
        if subject in data[utils.PROFESORI][teacher][utils.MATERII]:
            ans.append(teacher)
    return ans

def get_many_constraints(day_interval_class, teacher, data):
    # tell for an interval and a teacher, how many soft constraints are breached
    constraints_number = 0
    tuple_interval = ast.literal_eval(day_interval_class[1])
    check_hour = str(tuple_interval[0]) + '-' + str(tuple_interval[1])
    if ('!' + day_interval_class[0]) in data[utils.PROFESORI][teacher]['Constrangeri']:
        constraints_number += 1
    if ('!' + check_hour) in data[utils.PROFESORI][teacher]['Constrangeri']:
        constraints_number += 1
    return constraints_number

def get_many_constraints_break(day_interval_class, teacher, data, state):
    # tell for an interval and a teacher, how many soft constraints are breached
    # break is included
    constraints_number = 0
    tuple_interval = ast.literal_eval(day_interval_class[1])
    check_hour = str(tuple_interval[0]) + '-' + str(tuple_interval[1])
    if ('!' + day_interval_class[0]) in data[utils.PROFESORI][teacher]['Constrangeri']:
        constraints_number += 1
    if ('!' + check_hour) in data[utils.PROFESORI][teacher]['Constrangeri']:
        constraints_number += 1
    break_cond = get_break(data[utils.PROFESORI][teacher]['Constrangeri'])
    if break_cond == '':
        return constraints_number
    intervals_teaching = []
    for interval, aux_dict in state[day_interval_class[0]].items():
        if interval == day_interval_class[1]:
            continue
        for _, subject_teacher in aux_dict.items():
            if subject_teacher[1] == teacher:
                intervals_teaching.append(interval)
    positive_break = True
    if break_cond != '':
        if '!' in break_cond:
            positive_break = False
        match = re.search(r'\d+', break_cond)
        number_hours_break = int(match.group())
    current_interval_start = int(tuple_interval[0])
    current_interval_stop = int(tuple_interval[1])
    for interval in intervals_teaching:
        tuple_interval_aux = ast.literal_eval(interval)
        start_this_interval = int(tuple_interval_aux[0])
        stop_this_interval = int(tuple_interval_aux[1])
        break_duration = 0
        if stop_this_interval <= current_interval_start:
            break_duration = current_interval_start - stop_this_interval
        else:
            break_duration = start_this_interval - current_interval_stop
        if positive_break == False and break_duration > number_hours_break:
            constraints_number += 1
            return constraints_number
        if positive_break == True and break_duration < number_hours_break:
            constraints_number += 1
            return constraints_number
        
    return constraints_number

def available_interval(state, teacher, subject, data, day_interval_class):
    '''
    Return intervals that can be used for this subject and teacher.
    Return type: [((day, interval, classroom), value)], where value is
    100 -> if teacher would want to teach in this interval
    5 -> if teacher does not want either day or interval
    1 -> if teacher does not want the day and interval
    '''
    intervals_for_subject = list(filter(lambda x: subject in data[utils.SALI][x[2]][utils.MATERII], day_interval_class))
    intervals_hard_ok = []
    for interval_for_subject in intervals_for_subject:
        ok = 1
        for classroom, subject_teacher in state[interval_for_subject[0]][interval_for_subject[1]].items():
            if subject_teacher[1] == teacher:
                ok = 0
                break
        if ok == 1:
            intervals_hard_ok.append(interval_for_subject)
    ans  = []
    for aux in intervals_hard_ok:
        if get_many_constraints(aux, teacher, data) == 2:
            ans.append((aux, 1))
        elif get_many_constraints(aux, teacher, data) == 1:
            ans.append((aux, 3))
        elif get_many_constraints(aux, teacher, data) == 0:
            ans.append((aux, 100))
    return ans

def available_interval_break(state, teacher, subject, data, day_interval_class):
    '''
    Return intervals that can be used for this subject and teacher.
    Return type: [((day, interval, classroom), value)]
    '''
    intervals_for_subject = list(filter(lambda x: subject in data[utils.SALI][x[2]][utils.MATERII], day_interval_class))
    intervals_hard_ok = []
    for interval_for_subject in intervals_for_subject:
        ok = 1
        for classroom, subject_teacher in state[interval_for_subject[0]][interval_for_subject[1]].items():
            if subject_teacher[1] == teacher:
                ok = 0
                break
        if ok == 1:
            intervals_hard_ok.append(interval_for_subject)
    ans  = []
    for aux in intervals_hard_ok:
        if get_many_constraints_break(aux, teacher, data, state) == 3:
            ans.append((aux, 1))
        if get_many_constraints_break(aux, teacher, data, state) == 2:
            ans.append((aux, 3))
        elif get_many_constraints_break(aux, teacher, data, state) == 1:
            ans.append((aux, 5))
        elif get_many_constraints_break(aux, teacher, data, state) == 0:
            ans.append((aux, 150))
    return ans

def get_random_state_based_intervals(data):
    '''
    Get a random state as initial state, prioritizing intervals with capacity available.
    Example {Luni: {8-10: {EG202: (IOCLA, RD)}}}
    '''
    state = {}
    state_subjects = [(key, value) for key, value in data[utils.MATERII].items()]
    day_interval_class = []
    for day in data[utils.ZILE]:
        state[day] = {}
        for interval in data[utils.INTERVALE]:
            state[day][interval] = {}
            for classroom, _ in data[utils.SALI].items():
                state[day][interval][classroom] = (0, 0)
                day_interval_class.append((day, interval, classroom))
    teachers_and_intervals = get_all_teachers(data)
    while len(state_subjects) > 0:
        total = sum(x[1] for x in state_subjects)
        state_subject = random.choices(state_subjects, [x[1] / total for x in state_subjects])[0]
        matched_intervals = list(filter(lambda item: state_subject[0] in\
                                        data[utils.SALI][item[2]]['Materii'], day_interval_class))
        if len(matched_intervals) == 0:
            return {}
        
        students_no = state_subject[1]
        total_c = sum(data[utils.SALI][x[2]]['Capacitate'] for x in matched_intervals)
        probs_c = [data[utils.SALI][x[2]]['Capacitate'] / total_c for x in matched_intervals]
        item = random.choices(matched_intervals, probs_c)[0]
        available_teachers = get_subject_teachers_available(data,\
                                                            state_subject[0], state, item,\
                                                            teachers_and_intervals)
        if len(matched_intervals) == 0 or len(available_teachers) == 0:
            return {}
        students_no -= data[utils.SALI][item[2]]['Capacitate']
        teacher_chosen = random.choice(available_teachers)
        teachers_and_intervals[teacher_chosen] += 1
        state[item[0]][item[1]][item[2]] = (state_subject[0], teacher_chosen)
        day_interval_class.remove(item)
        matched_intervals.remove(item)
        if students_no <= 0:
            state_subjects.remove(state_subject)
        else:
            state_subjects.remove(state_subject)
            aux = (state_subject[0], students_no)
            state_subjects.append(aux)
    if len(state_subjects) > 0:
        return {} # no solution(hard constraints not respected)
    return state

def get_teacher_and_interval_break(qualified_teachers, subject, data, state, day_interval_class):
    # choose a teacher that is available with a higher probability
    # for the teacher that wants to work in that interval
    best_interval = None
    best_teacher = None
    soft_constraints_inverted = -100
    pool_intervals_teachers = []
    random.shuffle(qualified_teachers)
    for teacher in qualified_teachers:
        intervals_available = available_interval_break(state, teacher, subject, data, day_interval_class)
        if len(intervals_available) == 0:
            continue
        total_int = sum(x[1] for x in intervals_available)
        chosen_interval = random.choices(intervals_available, [x[1] / total_int for x in intervals_available])[0]
        pool_intervals_teachers.append((chosen_interval, teacher))
        if chosen_interval[1] >= soft_constraints_inverted:
            soft_constraints_inverted = chosen_interval[1]
            best_interval = chosen_interval[0]
            best_teacher = teacher
    if len(pool_intervals_teachers) == 0:
        return None, None
    total_int = sum(x[0][1] for x in pool_intervals_teachers)
    chosen_interval, teacher = random.choices(pool_intervals_teachers, [x[0][1] / total_int for x in pool_intervals_teachers])[0]
    return chosen_interval[0], teacher

def get_teacher_and_interval(qualified_teachers, subject, data, state, day_interval_class):
    # choose a teacher that is available with a higher probability
    # for the teacher that wants to work in that interval
    best_interval = None
    best_teacher = None
    soft_constraints_inverted = -100
    pool_intervals_teachers = []
    random.shuffle(qualified_teachers)
    for teacher in qualified_teachers:
        intervals_available = available_interval(state, teacher, subject, data, day_interval_class)
        if len(intervals_available) == 0:
            continue
        total_int = sum(x[1] for x in intervals_available)
        chosen_interval = random.choices(intervals_available, [x[1] / total_int for x in intervals_available])[0]
        pool_intervals_teachers.append((chosen_interval, teacher))
        if chosen_interval[1] > soft_constraints_inverted:
            soft_constraints_inverted = chosen_interval[1]
            best_interval = chosen_interval[0]
    if len(pool_intervals_teachers) == 0:
        return None, None
    total_int = sum(x[0][1] for x in pool_intervals_teachers)
    chosen_interval, teacher = random.choices(pool_intervals_teachers, [x[0][1] / total_int for x in pool_intervals_teachers])[0]
    return chosen_interval[0], teacher

def get_random_state_based_teachers(data):
    '''
    Get a random state as initial state.
    Example {Luni: {8-10: {EG202: (IOCLA, RD)}}}
    '''
    state = {}
    state_subjects = [(key, value) for key, value in data[utils.MATERII].items()]
    day_interval_class = []
    for day in data[utils.ZILE]:
        state[day] = {}
        for interval in data[utils.INTERVALE]:
            state[day][interval] = {}
            for classroom, _ in data[utils.SALI].items():
                state[day][interval][classroom] = (0, 0)
                day_interval_class.append((day, interval, classroom))
    teachers_and_intervals = get_all_teachers(data)
    while len(state_subjects) > 0:
        total = sum(x[1] for x in state_subjects)
        state_subject = random.choices(state_subjects, [x[1] / total for x in state_subjects])[0]
        teachers_qualified = get_teachers_qualified(data, teachers_and_intervals, state_subject[0])
        interval, teacher = get_teacher_and_interval(teachers_qualified, state_subject[0], data, state, day_interval_class)
        if interval == None:
            return {}
        state[interval[0]][interval[1]][interval[2]] = (state_subject[0], teacher)
        day_interval_class.remove(interval)
        students_no = state_subject[1] - data[utils.SALI][interval[2]]['Capacitate']
        teachers_and_intervals[teacher] += 1
        state_subjects.remove(state_subject)
        if students_no > 0:
            state_subjects.append((state_subject[0], students_no))
    if len(state_subjects) > 0:
        return {} # no solution(hard constraints not respected)
    return state

def get_random_state_based_teachers_with_break(data):
    '''
    Get a random state as initial state.
    Example {Luni: {8-10: {EG202: (IOCLA, RD)}}}
    '''
    state = {}
    state_subjects = [(key, value) for key, value in data[utils.MATERII].items()]
    day_interval_class = []
    for day in data[utils.ZILE]:
        state[day] = {}
        for interval in data[utils.INTERVALE]:
            state[day][interval] = {}
            for classroom, _ in data[utils.SALI].items():
                state[day][interval][classroom] = (0, 0)
                day_interval_class.append((day, interval, classroom))
    teachers_and_intervals = get_all_teachers(data)
    while len(state_subjects) > 0:
        total = sum(x[1] for x in state_subjects)
        state_subject = random.choices(state_subjects, [x[1] / total for x in state_subjects])[0]
        teachers_qualified = get_teachers_qualified(data, teachers_and_intervals, state_subject[0])
        interval, teacher = get_teacher_and_interval_break(teachers_qualified, state_subject[0], data, state, day_interval_class)
        if interval == None:
            return {}
        state[interval[0]][interval[1]][interval[2]] = (state_subject[0], teacher)
        day_interval_class.remove(interval)
        students_no = state_subject[1] - data[utils.SALI][interval[2]]['Capacitate']
        teachers_and_intervals[teacher] += 1
        state_subjects.remove(state_subject)
        if students_no > 0:
            state_subjects.append((state_subject[0], students_no))
    if len(state_subjects) > 0:
        return {} # no solution(hard constraints not respected)
    return state

def get_random_state(data):
    for teacher, dict_teacher in data[utils.PROFESORI].items():
        for item in dict_teacher['Constrangeri']:
            if 'Pauza' in item:
                return random.choice([get_random_state_based_teachers_with_break,\
                                        get_random_state_based_teachers_with_break,\
                                            get_random_state_based_teachers])(data)
    return random.choice([get_random_state_based_teachers, get_random_state_based_intervals, get_random_state_based_teachers])(data)

def teacher_twice_same_interval(classrooms_and_t_subjects):
    # tell if teacher appears twice
    aux_set = set()
    for classroom, t_s in classrooms_and_t_subjects.items():
        if t_s[1] in aux_set:
            return True
        else:
            aux_set.add(t_s[1])
    return False

def compatible_for_switch(state, data, tuple1, tuple2, i, j):
    # check if two pairs can be switched
    if i == j:
        return False
    if tuple1[0] == tuple2[0] and tuple1[1] == tuple2[1]:
        return False
    if tuple1[3] == (0, 0) and tuple2[3] == (0, 0):
        return False
    if tuple1[3][1] == tuple2[3][1]:
        return False
    classrooms_properties = data[utils.SALI]
    if tuple2[3][0] not in classrooms_properties[tuple1[2]][utils.MATERII] or tuple1[3][0]\
        not in classrooms_properties[tuple2[2]][utils.MATERII]:
        return False
    if classrooms_properties[tuple1[2]]['Capacitate'] != classrooms_properties[tuple2[2]]['Capacitate']:
        return False
    return True

def get_next_states(state, data):
    # generate all possible next states
    # as switches transform state
    tuples = []
    states = []
    for day, intervals_dict in state.items():
        for interval, classroom_dict in intervals_dict.items():
            for classroom, subject_teacher in classroom_dict.items():
                tuples.append((day, interval, classroom, subject_teacher))
    tuples_used = set()
    for i in range(len(tuples)):
        for j in range(len(tuples)):
            if (i, j) in tuples_used:
                continue
            tuples_used.add((i, j))
            if compatible_for_switch(state, data, tuples[i], tuples[j], i, j) is False:
                continue
            new_state = deepcopy(state)
            aux = new_state[tuples[i][0]][tuples[i][1]][tuples[i][2]]
            new_state[tuples[i][0]][tuples[i][1]][tuples[i][2]] =\
                new_state[tuples[j][0]][tuples[j][1]][tuples[j][2]]
            new_state[tuples[j][0]][tuples[j][1]][tuples[j][2]] = aux
            if teacher_twice_same_interval(new_state[tuples[i][0]][tuples[i][1]]) is True or\
                teacher_twice_same_interval(new_state[tuples[j][0]][tuples[j][1]]) is True:
                continue
            states.append(new_state)
    return states

def would_be_teacher_twice(state, tuple1, tuple2):
    list_teacher1 = set()
    list_teacher2 = set()
    for _, subject_teacher in state[tuple1[0]][tuple1[1]].items():
        list_teacher1.add(subject_teacher[1])
    for _, subject_teacher in state[tuple2[0]][tuple2[1]].items():
        list_teacher2.add(subject_teacher[1])
    if tuple1[3][1] in list_teacher2 or tuple2[3][1] in list_teacher1:
        return True
    return False

def get_next_states_as_tuples(state, data):
    # generate all possible next states(tuples only)
    # as switches transform state
    tuples = []
    states_tuples = []
    for day, intervals_dict in state.items():
        for interval, classroom_dict in intervals_dict.items():
            for classroom, subject_teacher in classroom_dict.items():
                tuples.append((day, interval, classroom, subject_teacher))
    tuples_used = set()
    for i in range(len(tuples)):
        for j in range(len(tuples)):
            if (i, j) in tuples_used:
                continue
            tuples_used.add((i, j))
            if compatible_for_switch(state, data, tuples[i], tuples[j], i, j) is False:
                continue
            if would_be_teacher_twice(state, tuples[i], tuples[j]) is True:
                continue
            states_tuples.append((tuples[i], tuples[j]))
    return states_tuples

def get_all_intervals(data):
    ans = []
    days = data[utils.ZILE]
    intervals = data[utils.INTERVALE]
    classrooms = [x for x, _ in data[utils.SALI].items()]
    for day in days:
        for interval in intervals:
            for classroom in classrooms:
                ans.append((day, interval, classroom))
    return ans

def initial_state_a_star(data):
    timetable = {}
    classrooms = [x for x, _, in data[utils.SALI].items()]
    for day in data[utils.ZILE]:
        timetable[day] = {}
        for interval in data[utils.INTERVALE]:
            timetable[day][interval] = {}
            for classroom in classrooms:
                timetable[day][interval][classroom] = (0, 0)
    list_subjects_students = sorted([(key, value) for key, value in data[utils.MATERII].items()],\
                                    key=lambda x: x[1])
    list_teacher_number_intervals = {name: 0 for name, _ in data[utils.PROFESORI].items()}
    return timetable, list_subjects_students, list_teacher_number_intervals

def breaks_not_respected(solution, data):
    '''
    Based on solution presented, return an estimated 'cost'
    for having it as a final solution(i.e. soft constraints not respected)
    '''
    days = data[utils.ZILE]
    intervals = data[utils.INTERVALE]
    teachers = data[utils.PROFESORI]
    # the next dict will have the following structure:
    # {teacher_name: [(day1, '8-10'), (day3, '12-14'), ...]}
    teachers_working_plan = {}
    cost_ret = 0
    for day in days:
        for interval in intervals:
            tuple_interval = ast.literal_eval(interval)
            dict_classes = solution[day][interval]
            for _, class_prof in dict_classes.items():
                if class_prof == (0, 0):
                    continue
                teacher_name = class_prof[1]
                if teacher_name not in teachers_working_plan:
                    teachers_working_plan[teacher_name] = []
                teachers_working_plan[teacher_name].append((day,\
                                        str(tuple_interval[0]) + '-' + str(tuple_interval[1])))
    # iterate through the whole program and notice if
    # a constraint is not respected
    for teacher_name, list_plan in teachers_working_plan.items():
        teacher = teachers[teacher_name]
        t_constraints = teacher[utils.CONSTRANGERI]
        break_cond = get_break(t_constraints)
        positive_break = True
        number_hours_break = 0
        # if the break constraint appear
        # parse it
        if break_cond != '':
            if '!' in break_cond:
                positive_break = False
            match = re.search(r'\d+', break_cond)
            number_hours_break = int(match.group())
        # break the intervals un/wanted in intervals
        # with 2 hours appart(e.g. '10-14' -> '10-12', '12-14')
        for i in range(len(list_plan)):
            if break_cond == '' or i == 0:
                continue
            if list_plan[i][0] != list_plan[i - 1][0]:
                continue
            end_past_course = [int(num) for num in list_plan[i - 1][1].split('-')][1]
            start_current_course = [int(num) for num in list_plan[i][1].split('-')][0]
            break_duration = start_current_course - end_past_course
            if positive_break == False and break_duration > number_hours_break:
                cost_ret += 1
            if positive_break == True and break_duration < number_hours_break:
                cost_ret += 1
    return cost_ret

def h_a_star(state, list_students_unallocated, list_teachers, data):
    soft_constraints = cost_solution(state, data)
    if len(list_students_unallocated) == 0:
        return soft_constraints, soft_constraints
    x = sum(a[1] for a in list_students_unallocated)
    intervals_busy = 0
    fav_int = 0
    total_capacity = 0
    total_classrooms = 0
    for day in data[utils.ZILE]:
        for interval in data[utils.INTERVALE]:
            tupp = ast.literal_eval(interval)
            interval_for_data = str(tupp[0]) + '-' + str(tupp[1])
            for classroom, _ in data[utils.SALI].items():
                if state[day][interval][classroom] != (0, 0):
                    intervals_busy += 1
                else:
                    total_capacity += data[utils.SALI][classroom]['Capacitate']
                    total_classrooms += 1
                    for teacher, _ in list_teachers.items():
                        if interval_for_data in data[utils.PROFESORI][teacher]['Constrangeri']:
                            fav_int += 1
                        if day in data[utils.PROFESORI][teacher]['Constrangeri']:
                            fav_int += 1

    breaks_not_respected_factor = breaks_not_respected(state, data)
    # standard_deviation = np.std([a for _, a in list_teachers.items()])
    return soft_constraints, 10000000 * (soft_constraints - breaks_not_respected_factor) + x + 0.1 * (4000 - fav_int) + 0.000001 * (500 - (total_capacity / total_classrooms))

def get_available_teachers(list_teacher_work_volume, data, subject):
    return [teacher_name for teacher_name, work_volume in list_teacher_work_volume.items()\
            if work_volume < 7 and subject in data[utils.PROFESORI][teacher_name][utils.MATERII]]

def generate_next_states_a_star(state, list_students_unallocated, list_teacher_work_volume, data):
    ans = []
    used_teacher_same_interval = set()
    used_interval_subject_good = set()
    if len(list_students_unallocated) == 0:
        return ans
    subject, students = list_students_unallocated[0]
    list_students_unallocated.pop(0)
    teachers = get_available_teachers(list_teacher_work_volume, data, subject)
    # for every teacher, try to find what they can teach, where and when
    # then consider that move a possible state
    for teacher in teachers:
        for day, dict_intervals in state.items():
            if day not in data[utils.PROFESORI][teacher]['Constrangeri']:
                continue
            for interval, dict_classrooms in dict_intervals.items():
                ok = 1
                for _, tuple_teached in dict_classrooms.items():
                    if teacher == tuple_teached[1]:
                        ok = 0
                        break
                if ok == 0:
                    continue
                for classroom, tuple_teached in dict_classrooms.items():
                    if subject not in data[utils.SALI][classroom][utils.MATERII]:
                        continue
                    if tuple_teached == (0, 0):
                        new_state = deepcopy(state)
                        new_state[day][interval][classroom] = (subject, teacher)
                        students_would_remain = students - data[utils.SALI][classroom]['Capacitate']
                        list_students = deepcopy(list_students_unallocated)
                        if students_would_remain > 0:
                            list_students.insert(0, (subject, students_would_remain))
                        new_teacher_work_volume = deepcopy(list_teacher_work_volume)
                        new_teacher_work_volume[teacher] += 1
                        ans.append((new_state, list_students, new_teacher_work_volume))
                        tupp = ast.literal_eval(interval)
                        interval_for_data = str(tupp[0]) + '-' + str(tupp[1])
                        if interval_for_data in data[utils.PROFESORI][teacher]['Constrangeri'] and new_teacher_work_volume[teacher] < 4:
                            used_interval_subject_good.add((day, interval))

    return ans

def try_make_it_work(state, sub_stub, t_work, data):
    # try to fit the remaining student in empty slots as last resort for A*
    # as using random, more than one try is recommended
    res = None
    for _ in range(10):
        aux_s = deepcopy(state)
        aux_sub_stud = deepcopy(sub_stub)
        aux_t_work = deepcopy(t_work)
        for subject, students in aux_sub_stud:
            options = []
            for day in data[utils.ZILE]:
                for interval in data[utils.INTERVALE]:
                    set_teachers_already_present = set()
                    for classroom, _ in data[utils.SALI].items():
                        set_teachers_already_present.add(aux_s[day][interval][classroom][1])
                    for classroom, prop in data[utils.SALI].items():
                        if aux_s[day][interval][classroom] != (0, 0):
                            continue
                        if subject not in prop['Materii']:
                            continue
                        for teacher, w in aux_t_work:
                            if w >= 7:
                                continue
                            if subject not in data[utils.PROFESORI][teacher]['Materii']:
                                continue
                            if teacher in set_teachers_already_present:
                                continue
                            options.append((day, interval, classroom, teacher))
            ok = 1
            while students > 0:
                if len(options) == 0:
                    ok = 0
                    break
                total_probs = sum(data[utils.SALI][x[2]]['Capacitate'] for x in options)
                probs = [data[utils.SALI][x[2]]['Capacitate'] / total_probs for x in options]
                day, interval, classroom, teacher = random.choices(options, probs)[0]
                options.remove((day, interval, classroom, teacher))
                options = list(filter(lambda x: x[0] != day or x[1] != interval or x[3] != teacher, options))
                aux_s[day][interval][classroom] = (subject, teacher)
                students -= data[utils.SALI][classroom]['Capacitate']
            if ok == 0:
                aux_s = None
                break
        if aux_s is not None:
            res = aux_s
            break
    return res
