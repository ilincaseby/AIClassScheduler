import utils
import re
import random

def get_break(constraints):
    key_word = 'Pauza'
    for constraint in constraints:
        if key_word in constraint:
            return constraint
    return ''

def cost_solution_soft_constraints(solution, data):
    '''
    Based on solution presented, return an estimated 'cost'
    for having it as a final solution(i.e. soft constraints not respected)
    '''
    days = data[utils.ZILE]
    intervals = data[utils.INTERVALE]
    teachers = data[utils.PROFESORI]
    teachers_working_plan = {}
    cost_ret = 0
    for day in days:
        for interval in intervals:
            dict_classes = solution[day][interval]
            for _, class_prof in dict_classes.items():
                if class_prof == (0, 0):
                    continue
                teacher_name = class_prof[1]
                if class_prof[1] not in teachers_working_plan:
                    teachers_working_plan[teacher_name] = []
                teachers_working_plan[teacher_name].append((day,\
                                        str(interval[0]) + '-' + interval[1]))
    for teacher_name, list_plan in teachers_working_plan.items():
        teacher = teachers[teacher_name]
        t_constraints = teacher[utils.CONSTRANGERI]
        break_cond = get_break(t_constraints)
        positive_break = True
        number_hours_break = 0
        if break_cond != '':
            if '!' in break_cond:
                positive_break = False
            match = re.search(r'>(\d+)', break_cond)
            number_hours_break = int(match.group(1))
        for i in range(len(list_plan)):
            if '!' + list_plan[i][0] not in t_constraints and\
                list_plan[i][0] not in t_constraints:
                cost_ret += 1
            if '!' + list_plan[i][0] in t_constraints:
                cost_ret += 2
            if '!' + list_plan[i][1] not in t_constraints and\
                list_plan[i][1] not in t_constraints:
                cost_ret += 1
            if '!' + list_plan[i][1] in t_constraints:
                cost_ret += 2
            if break_cond == '' or i == 0:
                continue
            if list_plan[i][0] != list_plan[i - 1][0]:
                continue
            end_past_course = [int(num) for num in list_plan[i - 1][1].split('-')][1]
            start_current_course = [int(num) for num in list_plan[i][1].split('-')][0]
            break_duration = start_current_course - end_past_course
            if positive_break == False and break_duration > number_hours_break:
                cost_ret += 2
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

def get_subject_teachers_available(data, subject, solution, day_interval_class):
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
        if ok == 1:
            res.append(teacher_name)
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
    random.shuffle(day_interval_class)
    while len(state_subjects) > 0:
        total = sum(x[1] for x in state_subjects)
        probs = [x[1] / total for x in state_subjects]
        state_subject = random.choices(state_subjects, probs)[0]
        added_class = 0
        for item in day_interval_class:
            if state_subject[0] in data[utils.SALI][item[2]]['Materii']:
                available_teachers = get_subject_teachers_available(data,
                                                                state_subject[0], state, item)
                remained = state_subject[1] - data[utils.SALI][item[2]]['Capacitate']
                teacher_chosen = random.choice(available_teachers)
                state[item[0]][item[1]][item[2]] = (state_subject[0], teacher_chosen)
                new_tup = (state_subject[0], remained)
                state_subjects.remove(state_subject)
                if new_tup[1] > 0:
                    state_subjects.append(new_tup)
                added_class = 1
                day_interval_class.remove(item)
                break
        if added_class == 0:
            return {} # no solution(hard constraints not respected)
    if len(state_subjects) > 0:
        return {} # no solution(hard constraints not respected)
    return state