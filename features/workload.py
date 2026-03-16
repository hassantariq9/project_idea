
import itertools

def assign_faculty(ideas, faculty):
    cycle = itertools.cycle(faculty)
    assignments = {}
    for idea in ideas:
        assignments[idea] = next(cycle)
    return assignments
