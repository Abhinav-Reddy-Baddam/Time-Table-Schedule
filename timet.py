import json
import random

# LOAD DATA
with open("data.json", "r") as f:
    data = json.load(f)

classes, rooms = data["classes"], data["rooms"]
days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
time_slots = ["10:00-11:30", "11:30-01:00", "02:00-03:30", "03:30-05:00"]

# BUILD STRUCTURES
subjects, required, faculty_experience = {}, {}, {}
for cls, subs in classes.items():
    subjects[cls], required[cls] = {}, {}
    for sub, details in subs.items():
        fac, exp = details["faculty"], details.get("experience", 0)
        subjects[cls][sub] = (fac, details["type"])
        required[cls][sub] = details["required"]
        faculty_experience[fac] = exp
    subjects[cls]["FREE"] = ("None", "Theory")
    faculty_experience["None"] = -1

# VARIABLE ORDERING: Fill morning slots (10:00) for all classes first
variables = [(cls, d, t) for cls in classes for d in days for t in time_slots]
variables.sort(key=lambda x: time_slots.index(x[2]))

def count_sub(assignment, cls, sub):
    count = sum(1 for (c, _, _), v in assignment.items() if c == cls and v[0] == sub)
    return count // 2 if "Lab" in sub else count

def is_consistent(var, value, assignment):
    cls, day, slot = var
    sub, fac, room = value
    if sub in required[cls] and count_sub(assignment, cls, sub) >= required[cls][sub]: return False
    for (c2, d2, s2), (sub2, fac2, room2) in assignment.items():
        if d2 == day and s2 == slot:
            if fac2 == fac and fac != "None": return False
            if room2 == room: return False
    if subjects[cls][sub][1] == "Theory" and sub != "FREE":
        if any(c2 == cls and d2 == day and sub2 == sub for (c2, d2, s2), (sub2, fac2, room2) in assignment.items()): return False
    if sub == "FREE":
        if time_slots.index(slot) not in (2, 3) or sum(1 for (c, d, s), v in assignment.items() if c == cls and v[0] == "FREE") >= 5: return False
    return True

def order_values(var, assignment):
    cls, _, _ = var
    vals = []
    for sub, (fac, typ) in subjects[cls].items():
        if sub in required[cls] and count_sub(assignment, cls, sub) >= required[cls][sub]: continue
        for r, rtyp in rooms.items():
            if typ == rtyp:
                vals.append(((sub, fac, r), faculty_experience.get(fac, 0)))
    # SORT: Non-FREE first, then Highest Experience first
    vals.sort(key=lambda x: (x[0][0] == "FREE", -x[1]))
    return [v[0] for v in vals]

def backtrack(assignment):
    if len(assignment) == len(variables): return assignment
    var = next((v for v in variables if v not in assignment), None)
    for val in order_values(var, assignment):
        if is_consistent(var, val, assignment):
            assignment[var] = val
            res = backtrack(assignment)
            if res: return res
            del assignment[var]
    return None

print("Generating Strict Seniority Waterfall Timetable...")
solution = backtrack({})

if solution:
    for cls in sorted(classes.keys()):
        print(f"\n===== {cls} =====")
        for d in days:
            line = f"{d:3} | "
            for t in time_slots:
                sub, fac, r = solution.get((cls, d, t), ("-", "-", "-"))
                line += f"[{t}] {sub[:6]}({fac}) | "
            print(line)