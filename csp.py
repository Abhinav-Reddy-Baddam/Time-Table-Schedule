import random

# -------------------------------
# BASIC SETUP
# -------------------------------
days = ["Mon", "Tue", "Wed", "Thu", "Fri"]

time_slots = [
    "10:00-11:30",
    "11:30-01:00",
    "02:00-03:30",
    "03:30-05:00"
]

def next_slot(slot):
    i = time_slots.index(slot)
    return time_slots[i + 1] if i < len(time_slots) - 1 else None

# -------------------------------
# SUBJECTS
# -------------------------------
subjects = {
    "AI": ("F1", "Theory"),
    "ML": ("F2", "Theory"),
    "FLAT": ("F3", "Theory"),
    "PE3": ("F4", "Theory"),
    "OE": ("F5", "Theory"),

    "AI Lab": ("F1", "Lab"),
    "ML Lab": ("F2", "Lab"),
    "PE3 Lab": ("F4", "Lab"),

    "FREE": ("None", "Theory")
}

required = {
    "AI": 2, "ML": 2, "FLAT": 2,
    "PE3": 2, "OE": 2,
    "AI Lab": 1, "ML Lab": 1, "PE3 Lab": 1
}

rooms = {
    "G401": "Theory",
    "G402": "Theory",
    "Lab1": "Lab",
    "Lab2": "Lab"
}

variables = [(d, t) for d in days for t in time_slots]

# -------------------------------
# PRE-ASSIGN LABS
# -------------------------------
def preassign_labs():
    assignment = {}

    lab_subjects = [s for s in required if "Lab" in s]
    random.shuffle(lab_subjects)

    for sub in lab_subjects:
        placed = False

        for day in days:
            # ensure only one lab per day
            if any("Lab" in assignment[v][0] for v in assignment if v[0] == day):
                continue

            for start_slot in ["10:00-11:30", "02:00-03:30"]:
                next_s = next_slot(start_slot)

                var1 = (day, start_slot)
                var2 = (day, next_s)

                if var1 in assignment or var2 in assignment:
                    continue

                fac, _ = subjects[sub]

                for room, rtype in rooms.items():
                    if rtype != "Lab":
                        continue

                    assignment[var1] = (sub, fac, room)
                    assignment[var2] = (sub, fac, room)
                    placed = True
                    break

                if placed:
                    break
            if placed:
                break

    return assignment

# -------------------------------
# COUNT FIX (IMPORTANT)
# -------------------------------
def count_sub(assignment, sub):
    count = sum(1 for v in assignment.values() if v[0] == sub)
    if "Lab" in sub:
        return count // 2   # 2 slots = 1 lab
    return count

def remaining_need(assignment):
    return {
        s: required[s] - count_sub(assignment, s)
        for s in required
    }

def all_done(assignment):
    return all(count_sub(assignment, s) == required[s] for s in required)

# -------------------------------
# CONSISTENCY
# -------------------------------
def is_consistent(var, value, assignment):
    day, slot = var
    sub, fac, room = value
    typ = subjects[sub][1]

    # ❌ prevent assigning labs again
    if "Lab" in sub:
        return False

    # limit
    if sub in required and count_sub(assignment, sub) >= required[sub]:
        return False

    # clash (room/faculty)
    for (d2, s2), (sub2, fac2, room2) in assignment.items():
        if d2 == day and s2 == slot:
            if room2 == room or fac2 == fac:
                return False

    # no same theory twice in a day
    if typ == "Theory" and sub != "FREE":
        for (d2, _), (sub2, _, _) in assignment.items():
            if d2 == day and sub2 == sub:
                return False

    # FREE only afternoon
    if sub == "FREE":
        idx = time_slots.index(slot)
        if idx not in (2, 3):
            return False

    return True

# -------------------------------
# FORWARD CHECK (FIXED)
# -------------------------------
def forward_check(assignment):
    rem = remaining_need(assignment)

    needed = 0
    for s, k in rem.items():
        if "Lab" in s:
            continue  # labs already placed
        needed += max(0, k)

    return (len(variables) - len(assignment)) >= needed

# -------------------------------
# MRV
# -------------------------------
def select_var(assignment):
    best = None
    min_options = float('inf')

    for v in variables:
        if v in assignment:
            continue

        options = 0
        for sub, (fac, typ) in subjects.items():
            if "Lab" in sub:
                continue
            for room, rtype in rooms.items():
                if typ == rtype:
                    if is_consistent(v, (sub, fac, room), assignment):
                        options += 1

        # immediate failure
        if options == 0:
            return v

        if options < min_options:
            min_options = options
            best = v

    return best

# -------------------------------
# VALUE ORDER
# -------------------------------
def order_values(var, assignment):
    vals = []

    for sub, (fac, typ) in subjects.items():
        if "Lab" in sub:
            continue
        for room, rtype in rooms.items():
            if typ == rtype:
                vals.append((sub, fac, room))

    # prioritize: Theory → FREE
    vals.sort(key=lambda v: 1 if v[0] == "FREE" else 0)
    random.shuffle(vals)

    return vals

# -------------------------------
# BACKTRACK
# -------------------------------
def backtrack(assignment):
    if len(assignment) == len(variables):
        if all_done(assignment):
            return assignment
        return None

    if not forward_check(assignment):
        return None

    var = select_var(assignment)

    for val in order_values(var, assignment):
        if is_consistent(var, val, assignment):
            assignment[var] = val

            result = backtrack(assignment)
            if result:
                return result

            del assignment[var]

    return None

# -------------------------------
# RUN
# -------------------------------
print("Solving timetable...")

initial = preassign_labs()
solution = backtrack(initial)

# -------------------------------
# PRINT
# -------------------------------
if solution is None:
    print("❌ No solution found")
else:
    print("\n===== FINAL TIMETABLE =====\n")

    for d in days:
        print(f"\n{d}")
        for t in time_slots:
            sub, fac, room = solution[(d, t)]
            print(f"{t} → {sub} ({fac}) [{room}]")