import utils
import re

def get_break(constraints):
    key_word = 'Pauza'
    for constraint in constraints:
        if key_word in constraint:
            return constraint
    return ''

def cost_solution_soft_constraints(solution, data):
    days = data[utils.ZILE]
    intervals = data[utils.INTERVALE]
    teachers = data[utils.PROFESORI]
    teachers_working_plan = {}
    cost_ret = 0
    for day in days:
        for interval in intervals:
            dict_classes = solution[day][interval]
            for _, class_prof in dict_classes.items():
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

def number_conflicts(solution, data):
    pass