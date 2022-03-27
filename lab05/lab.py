#!/usr/bin/env python3
"""6.009 Lab 5 -- Boolean satisfiability solving"""

import sys
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS
 

def update_formula(formula, variables):
    """
    Updates and simplified formula
    """

    def update_clause(clause, variables):
        """
        Updates clause after passing in variables
        Inputs: clause (a list containing the values), variables (a dictionary containing assignments)
        Output: an updated clause(list)
        """
        updated_clause = []
        for value in set(clause):
            if value[0] in variables:
                if variables[value[0]] == value[1]:
                    #if the value matches the assignment then skip clause
                    return True
                elif len(clause) == 1:
                    #if it doesn't match it and its the only value in the clause the clause is false
                    return None
            else:
                #if the value doesn't have an assignemnt then append to be solved later
                updated_clause.append(value)
        return updated_clause

    new_formula = []
    check = False
    for clause in formula:
        #updates clause
        updated_clause = update_clause(clause, variables)
        if updated_clause is True:
            # do not need to consider True clauses
            continue
        elif updated_clause is None or len(updated_clause) == 0:
            # if the clause is unsolvable it will return None
            return None
        elif len(clause) == 1 and clause[0][0] not in variables:
            # if the clause has caused an update in variables flag check as True
            check = True
            variables[clause[0][0]] = clause[0][1]
        #append updated clause
        new_formula.append(updated_clause)
    return (check, new_formula)




def check_satisfaction(formula, variables):
    """
    Checks if the puzzle can be solved with the current variables
    """
    check = True
    while check:
        try:
            #while the dictionary is being updated keep updating the formula
            check, formula = update_formula(formula, variables)
        except:
            #if any of the previous functions return None it will throw an error and return None
            return None
    #tries to satisfy the current formula
    variables = satisfying_assignment(formula)
    if variables is None:
        return None
    return variables
    


def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    #if its an empty formula return empty dic
    if len(formula) == 0:
        return {}
    #try the True value
    variables = {formula[0][0][0]: True}
    temp = check_satisfaction(formula, variables)
    if temp is None:
        #try the False value
        variables = {formula[0][0][0]: False}         
        temp = check_satisfaction(formula, variables)
    if temp is not None:
        #if the formula is still satisfiable update current dictionary
        variables.update(temp)
        return variables
    # return None if the formula is not satisfiable
    return None


def boolify_scheduling_problem(student_preferences, room_capacities):
    """
    Convert a quiz room scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a list
                         of room names (strings) that work for that student

    room_capacities: a dictionary mapping each room name to a positive integer
                     for how many students can fit in that room

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up

    We assume no student or room names contain underscores.
    """

    def desired_sections(student_preferences):
        """
        Creates a CNF formula checking that students are only in their prefered rooms
        """
        output_cnf = []
        for student in student_preferences:
            student_cnf = []
            for room in student_preferences[student]:
                #makes clause satisfiable if the student is in one of their preferred rooms
                student_cnf.append((student + '_' + room, True))
            output_cnf.append(student_cnf)
        return output_cnf

    def only_one_session(student_preferences, room_capacities):
        """
        Creates a CNF formula checking that students are only in one place
        """
        students = [student for student in student_preferences]
        rooms = [room for room in room_capacities]
        def iterate_rooms(students, rooms, toReturn = []):
            """
            Iterates through rooms to check that a student is only in one maximum
            """
            if len(rooms) == 1:
                #return value once done traversing through rooms
                return toReturn
            for student in students:
                for i in range(1, len(rooms)):
                    #checks that a student is not in two rooms at once
                    toReturn.append([(student + '_' + rooms[0], False), (student + '_' + rooms[i], False)])
            #reduces number of rooms and repeats process
            return iterate_rooms(students, rooms[1:], toReturn)
        return iterate_rooms(students, rooms)
    
    def not_oversubscribed(student_preferences, room_capacities):
        """
        Creates a CNF formula that checks that a rooms is not overly full
        """
        result = []
        students = [student for student in student_preferences]
        def iterate_students(students, room, capacity, toReturn = [], checker = set()):
            """
            Iterates through students to check that no more than the capacty are in a room at once
            """
            for j in range(len(students)):
                #assigns current students to room as False
                new_assign = [(students[0] + '_' + room, False)]
                for i in range(1, capacity+1):
                    try:
                        #if there are still students to check 
                        new_assign += [(students[i+j] + '_' + room, False)]
                    except:
                        continue
                if tuple(new_assign) in checker:
                    #if there are no new assignments return values
                    return toReturn
                elif len(new_assign) == capacity+1:   
                    #if the assignments are the correct capacity add and append them        
                    toReturn.append(new_assign)
                    checker.add(tuple(new_assign))
            #check students by adding those at the end of the list to the front
            return iterate_students(students[1:]+[students[0]], room, capacity, toReturn)

        for key, value in room_capacities.items():
            if value >= len(students):
                #if the room has a bigger capacity than there are students ignore it
                break
            elif value == 0:
                #if the room has no capacity make sure no one is there
                for student in students:
                    result += [[(student + '_' + key, False)]]
            else:
                #check that the rooms are not overly full
                iteration = iterate_students(students, key, value)
        result += iteration
        return result


    #combine all the conditions
    cnf_formula = not_oversubscribed(student_preferences, room_capacities) + only_one_session(student_preferences, room_capacities) + desired_sections(student_preferences)

    return cnf_formula

        








if __name__ == '__main__':
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)
    # test_formula = [[('a', True), ('b', False), ('c', True)], [('d', False), ('g', False)], [('e', False), ('a', False)]]
    # test = create_dict(test_formula)
    # test['a'] = True
    # #print(update_formula(test_formula, ('a', True)))
    # # delete_vars(test_formula, update_formula(test_formula, ('a', True)))
    # # print(test_formula)
    #     # print(iterate_formula(test_formula, i))
    # print(test_formula)

    # while len(test_formula) > 0:
    #     listidx = update_formula(test_formula, next(iterate_formula(test_formula[0])))
    #     print(listidx)
    #     delete_vars(test_formula, listidx)

    # x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    # # print(x)
    # cnf = [[("a",True), ("b",True)], [("a",False), ("b",False), ("c",True)],
    #            [("b",True),("c",True)], [("b",True),("c",False)]]
    # print(satisfying_assignment(cnf))
    # cnf = [[('a', True), ('a', False)], [('b', True), ('a', True)], [('b', True)], [('b', False), ('b', False), ('a', False)], [('c', True), ('d', True)], [('c', True), ('d', True)]]
    # print(satisfying_assignment(cnf))
    # test = [[('a', True), ('a', False)], [('b', True), ('a', True)], [('b', True)], [('b', False), ('b', False), ('a', False)], [('c', True), ('d', True)], [('c', True), ('d', True)]]
    # print(satisfying_assignment(test))
    student_preferences = {'Alice': ['basement', 'penthouse'],
                            'Bob': ['kitchen'],
                            'Charles': ['basement', 'kitchen'],
                            'Dana': ['kitchen', 'penthouse', 'basement']}
    room_capacities = {'basement': 1,
                            'kitchen': 2,
                            'penthouse': 4, 'classroom':0}
    #print(boolify_scheduling_problem(student_preferences, room_capacities))
    #print(no_oversubscribed_sections(student_preferences, room_capacities))
    # [[('Dana_basement', False), ('Charles_basement', False)], [('Dana_basement', False), ('Bob_basement', False)], [('Charles_basement', False), ('Bob_basement', False)], [('Dana_basement', False), ('Alice_basement', False)], [('Charles_basement', False), ('Alice_basement', False)], [('Bob_basement', False), ('Alice_basement', False)], [('Dana_kitchen', False), ('Charles_kitchen', False), ('Bob_kitchen', False)], [('Dana_kitchen', False), ('Charles_kitchen', False), ('Alice_kitchen', False)], [('Dana_kitchen', False), ('Bob_kitchen', False), ('Alice_kitchen', False)], [('Charles_kitchen', False), ('Bob_kitchen', False), ('Alice_kitchen', False)]]
    # [[('Bob_kitchen', True), ('Bob_basement', True)],[('Bob_kitchen', False), ('Bob_basement', False)]]\


    # print(boolify_scheduling_problem(student_preferences, room_capacities))
    result = [[('Alice_basement', True), ('Alice_penthouse', True)], [('Bob_kitchen', True)], [('Charles_basement', True), ('Charles_kitchen', True)], [('Dana_kitchen', True), ('Dana_penthouse', True), ('Dana_basement', True)]]
    test1 = {'student0': ['session0', 'session3', 'session4', 'session6', 'session8'], 'student1': ['session4', 'session5', 'session6'], 'student7': ['session0', 'session2', 'session3', 'session4', 'session5', 'session6', 'session8'], 'student4': ['session2', 'session3', 'session4', 'session6', 'session7'], 'student3': ['session0', 'session1', 'session2', 'session3', 'session4', 'session8', 'session9'], 'student2': ['session1', 'session2', 'session3', 'session4', 'session5', 'session7', 'session8'], 'student9': ['session0', 'session1', 'session4', 'session5', 'session6'], 'student6': ['session2', 'session7'], 'student8': ['session0', 'session1', 'session2', 'session5', 'session6', 'session8', 'session9'], 'student5': ['session2', 'session3', 'session6', 'session7', 'session8', 'session9']} 
    test2 = {'session6': 6, 'session8': 5, 'session1': 8, 'session2': 8, 'session9': 5, 'session7': 6, 'session0': 1, 'session5': 5, 'session3': 6, 'session4': 4}
    # set1 = boolify_scheduling_problem(test1, test2)
    #set2 = exactly_one_session(test1, test2)
    # print(set1-set2)
    # print(only_in_desired_rooms(test1))
    answer = [[('Dana_basement', False), ('Bob_basement', False)], [('Dana_basement', False), ('Charles_basement', False)], [('Charles_basement', False), ('Bob_basement', False)], [('Dana_basement', False), ('Alice_basement', False)], [('Charles_basement', False), ('Alice_basement', False)], [('Bob_basement', False), ('Alice_basement', False)], [('Dana_kitchen', False), ('Charles_kitchen', False), ('Bob_kitchen', False)], [('Dana_kitchen', False), ('Charles_kitchen', False), ('Alice_kitchen', False)], [('Dana_kitchen', False), ('Bob_kitchen', False), ('Alice_kitchen', False)], [('Charles_kitchen', False), ('Bob_kitchen', False), ('Alice_kitchen', False)]]