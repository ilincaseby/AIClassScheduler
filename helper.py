import utils
import re
import random
from copy import deepcopy
import ast

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
    res = {}
    for teacher_name, _ in data[utils.PROFESORI].items():
        if teacher_name not in res:
            res[teacher_name] = 0
    return res

def get_random_state(data):
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
    random.shuffle(day_interval_class)
    while len(state_subjects) > 0:
        total = sum(x[1] for x in state_subjects)
        probs = [x[1] / total for x in state_subjects]
        state_subject = random.choices(state_subjects, probs)[0]

        matched_intervals = list(filter(lambda item: state_subject[0] in\
                                        data[utils.SALI][item[2]]['Materii'], day_interval_class))
        
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

def teacher_twice_same_interval(classrooms_and_t_subjects):
    aux_set = set()
    for classroom, t_s in classrooms_and_t_subjects.items():
        if t_s[1] in aux_set:
            return True
        else:
            aux_set.add(t_s[1])
    return False

def compatible_for_switch(state, data, tuple1, tuple2, i, j):
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