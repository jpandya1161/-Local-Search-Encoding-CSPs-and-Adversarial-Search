import sys
from csp import CSP

args = sys.argv[:]

if not len(args) == 4:
    print("Expected 3 arguments: variable file, constraint file, heuristic choice (none/fc)")
    exit(0)

if not (args[3] == 'none' or args[3] == 'fc'):
    print("Expected only none (backtracking) or fc (forward-checking)")
    exit(0)

var_file = args[1]
con_file = args[2]
heuristic = True if args[3] == 'fc' else False

problem = CSP(heuristic)

variableFile = open(var_file, 'r')
for line in variableFile:
    variable = line[0].strip()
    domain = line[3:].strip('\n').split(' ')
    if '' in domain:
        domain.remove('')
    domain = list(map(int, domain))
    problem.adding_variable(variable, domain)

variableFile.close()

def is_equals(arr):
    return arr[0] == arr[1]

def is_greater_than(arr):
    return arr[0] > arr[1]

def is_less_than(arr):
    return arr[0] < arr[1]

def is_not_equals(arr):
    return arr[0] != arr[1]

funcSelector = {
    "=": is_equals,
    ">": is_greater_than,
    "<": is_less_than,
    "!": is_not_equals
}

constraintFile = open(con_file, 'r')
for lines in constraintFile:
    line = lines.strip('\n').split(" ")
    for l in line:
        i = line.index(l)
        line[i] = l.strip()

    constraint_variable = [line[0], line[2]]
    operator = line[1]
    problem.adding_constraint(funcSelector.get(str(operator)), constraint_variable)
constraintFile.close()

problem.result()
