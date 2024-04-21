from hill_climbing import random_restart_hill_climbing
from astar import a_star_beam_search
import sys
import utils
import re

def start():
    if len(sys.argv) < 3:
        print('Not enough arguments, specify desired algorithm and input file!')
        sys.exit(1)
    algorithm_desired = sys.argv[1]
    file_path = sys.argv[2]
    parsed_data = utils.read_yaml_file(file_path=file_path)
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
    #print(parsed_data)
    if algorithm_desired == 'hc':
        state, cost, is_final = random_restart_hill_climbing(parsed_data, 1500)
        print(is_final)
        print(state)
    else:
        state, cost, is_final = a_star_beam_search(parsed_data)
    pass

if __name__ == '__main__':
    start()