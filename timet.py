import json
import random

# -------------------------------
# LOAD DATA
# -------------------------------
with open("data.json", "r") as f:
    data = json.load(f)

classes = data["classes"]
rooms = data["rooms"]

# -------------------------------
# SETUP
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
# BUILD STRUCTURES
# -------------------------------
subjects = {}
required = {}

for cls, subs in classes.items():
    subjects[cls] = {}
    required[cls] = {}

    for sub, details in subs.items():
        subjects[cls][sub] = (details["faculty"], details["type"])
        required[cls][sub] = details["required"]

    subjects[cls]["FREE"] = ("None", "Theory")

# -------------------------------
# VARIABLES
# -------------------------------
variables = [(cls, d, t) for cls in classes for d in days for t in time_slots]
random.shuffle(variables)

# -------------------------------
# COUNT
# -------------------------------
def count_sub(assignment, cls, sub):
    count = sum(1 for (c, _, _), v in assignment.items() if c == cls and v[0] == sub)
    if "Lab" in sub:
        return count // 2
    return count

# -------------------------------
# PREASSIGN LABS
# -------------------------------
def preassign_labs():
    assignment = {}
    
    # Shuffle classes and days so the first class doesn't always get the first day
    shuffled_classes = list(classes.keys())
    random.shuffle(shuffled_classes)
    
    shuffled_days = list(days)
    random.shuffle(shuffled_days)

    for cls in shuffled_classes:
        lab_subjects = [s for s in required[cls] if "Lab" in s]
        random.shuffle(lab_subjects) # Randomize lab order per class

        for sub in lab_subjects:
            placed = False
            for day in shuffled_days:
                # Check if this class already has a lab this day
                if any(v[0] == cls and "Lab" in assignment[v][0] for v in assignment if v[1] == day):
                    continue

                # Shuffle starting slots (10:00 or 02:00)
                starts = ["10:00-11:30", "02:00-03:30"]
                random.shuffle(starts)

                for start in starts:
                    nxt = next_slot(start)
                    v1 = (cls, day, start)
                    v2 = (cls, day, nxt)

                    if v1 in assignment or v2 in assignment:
                        continue

                    fac = subjects[cls][sub][0]
                    
                    # Shuffle rooms so Lab1 isn't always picked first
                    room_list = list(rooms.items())
                    random.shuffle(room_list)

                    for room, typ in room_list:
                        if typ != "Lab":
                            continue
                        
                        # Faculty/Room clash check for labs
                        clash = False
                        for (c2, d2, s2), (sub2, fac2, room2) in assignment.items():
                            if d2 == day and (s2 == start or s2 == nxt):
                                if fac2 == fac or room2 == room:
                                    clash = True
                                    break
                        
                        if not clash:
                            assignment[v1] = (sub, fac, room)
                            assignment[v2] = (sub, fac, room)
                            placed = True
                            break

                    if placed: break
                if placed: break
    return assignment
# -------------------------------
# CONSISTENCY
# -------------------------------
def is_consistent(var, value, assignment):
    cls, day, slot = var
    sub, fac, room = value
    typ = subjects[cls][sub][1]

    # 1. Subject Quantity Rule: Don't assign more than the required count per class
    # Note: Lab sessions are pre-assigned, but this keeps the solver from adding 
    # extra theory or "accidental" lab slots during backtracking.
    if sub in required[cls] and count_sub(assignment, cls, sub) >= required[cls][sub]:
        return False

    # 2. Global Resource Clash Rule: Cross-Class Faculty and Room check
    # Ensures a teacher isn't in two places at once, and a room isn't double-booked.
    for (c2, d2, s2), (sub2, fac2, room2) in assignment.items():
        if d2 == day and s2 == slot:
            # Check if another class is using the same faculty or room at this time
            if fac2 == fac and fac != "None":
                return False
            if room2 == room:
                return False

    # 3. Daily Variety Rule: Theory subjects cannot repeat in the same day for a class
    if typ == "Theory" and sub != "FREE":
        for (c2, d2, s2), (sub2, fac2, room2) in assignment.items():
            if c2 == cls and d2 == day and sub2 == sub:
                return False

    # 4. Soft Constraint "Hardened": FREE slot rules
    if sub == "FREE":
        # Rule A: Position - Only allow FREE in the afternoon (Slots 2 & 3)
        idx = time_slots.index(slot)
        if idx not in (2, 3):
            return False
        
        # Rule B: Quantity - Limit total FREE slots to 5 per class (from your JSON update)
        free_count = sum(1 for (c, d, s), v in assignment.items() 
                         if c == cls and v[0] == "FREE")
        if free_count >= 5:
            return False

    return True
# -------------------------------
# MRV
# -------------------------------
def select_var(assignment):
    best = None
    min_options = float('inf')

    for v in variables:
        if v in assignment:
            continue

        cls, day, slot = v
        options = 0

        for sub, (fac, typ) in subjects[cls].items():
            for room, rtype in rooms.items():
                if typ == rtype:
                    if is_consistent(v, (sub, fac, room), assignment):
                        options += 1

        if options == 0:
            return v

        if options < min_options:
            min_options = options
            best = v

    return best

# -------------------------------
# VALUE ORDER (SMART)
# -------------------------------
def order_values(var, assignment):
    cls, _, _ = var
    vals = []
    
    # Shuffle rooms and subjects to ensure variety in theory slots
    room_items = list(rooms.items())
    random.shuffle(room_items)

    for sub, (fac, typ) in subjects[cls].items():
        if sub in required[cls] and count_sub(assignment, cls, sub) >= required[cls][sub]:
            continue

        for room, rtype in room_items:
            if typ == rtype:
                vals.append((sub, fac, room))

    # Always keep FREE as the last resort, but shuffle the rest
    random.shuffle(vals)
    vals.sort(key=lambda v: 1 if v[0] == "FREE" else 0)
    return vals

# -------------------------------
# FORWARD CHECK
# -------------------------------
def forward_check(assignment):
    remaining_slots = len(variables) - len(assignment)

    needed = 0
    for cls in required:
        for sub in required[cls]:
            if "Lab" in sub:
                continue
            needed += max(0, required[cls][sub] - count_sub(assignment, cls, sub))

    return remaining_slots >= needed

# -------------------------------
# BACKTRACK
# -------------------------------
def backtrack(assignment):
    if len(assignment) == len(variables):
        return assignment

    if not forward_check(assignment):
        return None

    var = select_var(assignment)

    if var is None:
        return None

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
print("Solving multi-class timetable...")

initial = preassign_labs()
solution = backtrack(initial)

# -------------------------------
# PRINT
# -------------------------------
# -------------------------------
# PRINT (TABLE FORMAT)
# -------------------------------
# -------------------------------
# GENERATE HTML FILE
# -------------------------------
if solution:
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>College Timetable</title>
        <style>
            body { font-family: sans-serif; background: #f4f4f9; padding: 20px; }
            h1 { text-align: center; color: #333; }
            .class-section { background: white; margin-bottom: 40px; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { border: 1px solid #ddd; padding: 12px; text-align: center; }
            th { background-color: #4CAF50; color: white; }
            tr:nth-child(even) { background-color: #f2f2f2; }
            .lab { background-color: #e8f5e9; font-weight: bold; color: #2e7d32; }
            .free { color: #999; font-style: italic; }
        </style>
    </head>
    <body>
        <h1>University Master Timetable</h1>
    """

    for cls in classes:
        html_content += f"<div class='class-section'><h2>Class: {cls}</h2>"
        html_content += "<table><tr><th>Day</th>"
        for t in time_slots:
            html_content += f"<th>{t}</th>"
        html_content += "</tr>"

        for d in days:
            html_content += f"<tr><td><strong>{d}</strong></td>"
            for t in time_slots:
                res = solution.get((cls, d, t))
                if res:
                    sub, fac, room = res
                    # Add specific CSS classes for styling
                    css_class = "lab" if "Lab" in sub else ("free" if sub == "FREE" else "")
                    html_content += f"<td class='{css_class}'>{sub}<br><small>{fac} ({room})</small></td>"
                else:
                    html_content += "<td>-</td>"
            html_content += "</tr>"
        html_content += "</table></div>"

    html_content += "</body></html>"

    with open("index.html", "w") as f:
        f.write(html_content)
    print("✅ Success! index.html has been generated.")