import sys
import utils

def start():
    if len(sys.argv) < 3:
        print('Not enough arguments, specify desired algorithm and input file!')
        sys.exit(1)
    algorithm_desired = sys.argv[1]
    file_path = sys.argv[2]
    parsed_data = utils.read_yaml_file(file_path=file_path)
    # TODO: update data for each teacher so that intervals are on just 2 hours
    pass

if __name__ == '__main__':
    start()