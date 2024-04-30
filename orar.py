from hill_climbing import random_restart_hill_climbing
from helper import cost_solution
from astar import a_star
import sys
import utils
import re
import ast
import os
import time

def start():
    if len(sys.argv) < 3:
        print('Not enough arguments, specify desired algorithm and input file!')
        sys.exit(1)
    algorithm_desired = sys.argv[1]
    file_path = sys.argv[2]
    parsed_data = utils.read_yaml_file(file_path=file_path)
    # parse the dictionary so that intervals present
    # for teachers will appear 2 hours appart
    for _, teacher in parsed_data[utils.PROFESORI].items():
        constraints = teacher[utils.CONSTRANGERI]
        new_constraints = []
        for constraint in constraints:
            c = constraint
            neg = False
            if c[0] == '!':
                neg = True
                c = c[1:]
            pattern = r'^\d+-\d+$'
            if re.match(pattern, c):
                numbers = [int(num) for num in c.split('-')]
                if numbers[1] - numbers[0] <= 2:
                    continue
                for i in range(numbers[0], numbers[1], 2):
                    new_c = ''
                    if neg is True:
                        new_c += '!'
                    new_c += str(i) + '-' + str(i + 2)
                    new_constraints.append(new_c)
        teacher[utils.CONSTRANGERI] += new_constraints
    # establish the future followed algorithm
    state = None
    if algorithm_desired == 'hc':
        start_timer = time.time()
        state_result, cost, is_final, generated_states = random_restart_hill_climbing(parsed_data, 1000)
        stop_timer = time.time()
        print(f'Timp {stop_timer - start_timer}, stari generate {generated_states}')
        state = state_result
    else:
        start_timer = time.time()
        state_result, cost, is_final, generated_states = a_star(parsed_data)
        stop_timer = time.time()
        state = state_result
        print(f'Timp {stop_timer - start_timer}, stari generate {generated_states}')
    # 'translate' to the needed timetable by auxiliar function
    pretty_print_dict = {}
    for day in parsed_data[utils.ZILE]:
        pretty_print_dict[day] = {}
        for interval in parsed_data[utils.INTERVALE]:
            tuple_interval = ast.literal_eval(interval)
            hour1 = int(tuple_interval[0])
            hour2 = int(tuple_interval[1])
            pretty_print_dict[day][(hour1, hour2)] = {}
            for classroom in parsed_data[utils.SALI]:
                if state[day][interval][classroom] == (0, 0):
                    pretty_print_dict[day][(hour1, hour2)][classroom] = None
                    continue
                pretty_print_dict[day][(hour1, hour2)][classroom] = (state[day][interval][classroom][1], state[day][interval][classroom][0])
    # obtain string for displaying timetable and print it into the desired file
    pretty_printed = utils.pretty_print_timetable(pretty_print_dict, file_path)
    new_file_path = os.path.splitext(file_path.replace('inputs', 'outputs'))[0] + '.txt'
    with open(new_file_path, 'w') as file_write:
        file_write.write(pretty_printed)
    pass

if __name__ == '__main__':
    start()