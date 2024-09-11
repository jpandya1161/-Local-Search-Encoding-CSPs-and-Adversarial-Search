class CSP:
    def __init__(self, heuristic):
        self.variables = {}
        self.constraints = []
        self.backtracking = (heuristic == 'none')
        self.forward_checking = (heuristic == 'fc')
        self.call_depth = 0
        self.debug_output = True

    def adding_variable(self, variable, domain):
        if variable not in self.variables:
            self.variables[variable] = domain
        else:
            print("Skipping duplicate variable.")

    def adding_constraint(self, operator, variables):
        self.constraints.append((operator, variables))

    def result(self):
        assignments = {}
        printed_assignments = []
        if self.solution(assignments, printed_assignments):
            return assignments
        else:
            return False

    def solution(self, assignments, assignments_to_print):
        if len(assignments) == len(self.variables):
            if self.goalTest(assignments):
                self.print_assignments(assignments_to_print, 'solution')
                return assignments
            else:
                return False

        if self.backtracking:
            return self.backtrack(assignments, assignments_to_print)
        elif self.forward_checking:
            return self.forward_check(assignments, assignments_to_print)

    def forward_check(self, assignments, assignments_to_print):
        var = self.select_unassigned_variable(assignments)
        constraints = self.get_constraints(var)

        for c in constraints:
            if c[1][0] not in assignments or c[1][1] not in assignments:
                continue

            index_of_original = c[1].index(var)
            index_of_other = 0 if index_of_original == 1 else 1
            other_var = c[1][index_of_other]

            original_domain_of_this_variable = self.variables[other_var]
            remaining_domain_for_this_variable = []

            for v in original_domain_of_this_variable:
                to_pass = [0, 0]
                to_pass[index_of_other] = v
                to_pass[index_of_original] = assignments[var]
                if c[0](to_pass):
                    remaining_domain_for_this_variable.append(v)

            if len(remaining_domain_for_this_variable) > 0:
                self.variables[other_var] = remaining_domain_for_this_variable[:]
            else:
                return False

        return True

    def backtrack(self, assignments, assignments_to_print):
        if len(assignments) == len(self.variables):
            if self.goalTest(assignments):
                self.print_assignments(assignments_to_print, 'solution')
                return assignments
            else:
                return False

        var = self.select_unassigned_variable(assignments)
        ordered_values = self.order_domain_values(var, assignments)
        for v in ordered_values:
            value = int(v[0])

            if self.check_consistency(var, value, assignments):
                assignments[var] = value
                assignments_to_print.append((var, value))

                result = self.backtrack(assignments, assignments_to_print)
                if result:
                    return result

                del assignments[var]
                assignments_to_print.pop(-1)

        return False

    def select_unassigned_variable(self, assignments):
        unassigned = self.get_unassigned(assignments)

        to_pick_from = []

        for u in unassigned:
            new_remaining_domain = []
            remaining_domain = self.variables[u]
            for val in remaining_domain:
                val = int(val)
                if self.check_consistency(u, val, assignments):
                    new_remaining_domain.append(val)

            to_pick_from.append([u, remaining_domain, 0])

        to_pick_from.sort(key=lambda t: len(t[1]))

        to_tie_break = []
        min_val = len(to_pick_from[0][1])

        for a in to_pick_from:
            if len(a[1]) == min_val:
                to_tie_break.append(a)

        for var in to_tie_break:
            unassigned_constraints = []
            constraints = self.get_constraints(var[0])

            for c in constraints:
                if c[1][0] not in assignments and c[1][1] not in assignments:
                    unassigned_constraints.append(c)

            var[2] = len(unassigned_constraints)

        to_tie_break.sort(key=lambda t: int(t[2]), reverse=True)

        max_val = to_tie_break[0][2]
        to_alphabetize = []

        for t in to_tie_break:
            if t[2] == max_val:
                to_alphabetize.append(t)

        to_alphabetize.sort(key=lambda t: t[0])

        return to_alphabetize[0][0]

    def order_domain_values(self, var, assignments):
        constraints = self.get_constraints(var)
        domain = self.variables[var]

        unassigned_constraints = []
        for c in constraints:
            if c[1][0] not in assignments and c[1][1] not in assignments:
                unassigned_constraints.append(c)

        test_assignments = assignments.copy()
        to_pick_from = []

        for val in domain:
            test_assignments[var] = val
            sum_for_this_val = 0
            for u in unassigned_constraints:
                index_of_original = u[1].index(var)
                index_of_other = 0 if index_of_original == 1 else 1
                original_domain_of_this_variable = self.variables[u[1][index_of_other]]
                remaining_domain_for_this_variable = []

                for v in original_domain_of_this_variable:
                    to_pass = [0, 0]
                    to_pass[index_of_original] = val
                    to_pass[index_of_other] = v
                    if u[0](to_pass):
                        remaining_domain_for_this_variable.append(v)

                sum_for_this_val += len(remaining_domain_for_this_variable)
            to_pick_from.append((val, sum_for_this_val))

        to_pick_from.sort(key=lambda t: t[1], reverse=True)
        return to_pick_from

    def check_consistency(self, var, value, assignments):
        constraints = self.get_constraints(var)

        for con in constraints:
            index_of_var = con[1].index(var)
            index_of_other_var = 0 if index_of_var == 1 else 1
            other_var = con[1][index_of_other_var]

            if con[1][index_of_other_var] in assignments:
                to_pass = [0, 0]
                to_pass[index_of_var] = value
                to_pass[index_of_other_var] = assignments[other_var]
                if not con[0](to_pass):
                    return False

        return True

    def goalTest(self, assignments):
        for key in self.variables:
            if key not in assignments:
                return False

        for constraint in self.constraints:
            v1 = assignments[constraint[1][0]]
            v2 = assignments[constraint[1][1]]

            if not constraint[0]([v1, v2]):
                return False

        return True

    def get_constraints(self, var):
        constraints = []

        for a in self.constraints:
            if var in a[1]:
                constraints.append(a)

        return constraints

    def get_unassigned(self, assignments):
        unassigned = []
        for a in self.variables:
            if a not in assignments:
                unassigned.append(a)

        return unassigned

    def print_assignments(self, assignments, status):
        print(str(self.call_depth + 1) + '. ', end='')

        string = ""
        for a in assignments:
            string += str(a[0]) + '=' + str(a[1]) + ', '
        string = string[0:-2]

        print(string + " ", end='')
        print(status)
