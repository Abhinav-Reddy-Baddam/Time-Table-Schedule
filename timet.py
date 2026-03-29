import json
import random

# -------------------------------
# LOAD DATA
# -------------------------------
# Assuming the JSON block you provided is saved as data.json
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

morning_slots = ["10:00-11:30", "11:30-01:00"]

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
        # Store (faculty, type, experience)
        subjects[cls][sub] = (details["faculty"], details["type"], details.get("experience", 0))
        required[cls][sub] = details["required"]
    subjects[cls]["FREE"] = ("None", "Theory", 0)

variables = [(cls, d, t) for cls in classes for d in days for t in time_slots]
random.shuffle(variables)

# -------------------------------
# HELPER FUNCTIONS
# -------------------------------
def count_sub(assignment, cls, sub):
    count = sum(1 for (c, _, _), v in assignment.items() if c == cls and v[0] == sub)
    if "Lab" in sub:
        return count // 2
    return count

def is_consistent(var, value, assignment):
    cls, day, slot = var
    sub, fac, room = value
    typ = subjects[cls][sub][1]

    if var in assignment: return False
    if sub in required[cls] and count_sub(assignment, cls, sub) >= required[cls][sub]:
        return False

    for (c2, d2, s2), (sub2, fac2, room2) in assignment.items():
        if d2 == day and s2 == slot:
            if fac2 == fac and fac != "None": return False
            if room2 == room: return False

    if typ == "Theory" and sub != "FREE":
        for (c2, d2, s2), (sub2, fac2, room2) in assignment.items():
            if c2 == cls and d2 == day and sub2 == sub: return False

    if "Lab" in sub:
        if any("Lab" in v[0] for (c, d, s), v in assignment.items() if c == cls and d == day):
            return False

    if sub == "FREE":
        free_count = sum(1 for (c, d, s), v in assignment.items() if c == cls and v[0] == "FREE")
        if free_count >= 5: return False

    return True

# -------------------------------
# ENHANCED VALUE ORDERING (Experience-Based)
# -------------------------------
def order_values(var, assignment):
    cls, day, slot = var
    vals = []
    
    room_items = list(rooms.items())
    random.shuffle(room_items)

    for sub, (fac, typ, exp) in subjects[cls].items():
        if sub in required[cls] and count_sub(assignment, cls, sub) >= required[cls][sub]:
            continue
        for room, rtype in room_items:
            if typ == rtype:
                vals.append((sub, fac, room, exp))

    def combined_score(val):
        sub_name, _, _, exp = val
        if sub_name == "FREE": return 1000  # Always last
        
        # Determine if it's morning
        is_morning = slot in morning_slots
        
        # If morning, high experience gets a LOW score (to be sorted first)
        # If evening, we don't strictly penalize, but morning is priority for high exp.
        seniority_priority = -exp if is_morning else exp 
        
        # Clustering logic (keep classes together)
        idx = time_slots.index(slot)
        has_neighbor = False
        for neighbor_idx in [idx - 1, idx + 1]:
            if 0 <= neighbor_idx < len(time_slots):
                if (cls, day, time_slots[neighbor_idx]) in assignment:
                    has_neighbor = True
        
        neighbor_bonus = 0 if has_neighbor else 100
        
        return seniority_priority + neighbor_bonus

    vals.sort(key=combined_score)
    # Strip the experience from the tuple before returning to match expected assignment format
    return [(v[0], v[1], v[2]) for v in vals]

# -------------------------------
# BACKTRACKING & PREASSIGN (Standard)
# -------------------------------
def preassign_labs():
    assignment = {}
    shuffled_classes = list(classes.keys())
    random.shuffle(shuffled_classes)
    for cls in shuffled_classes:
        lab_subjects = [s for s in required[cls] if "Lab" in s]
        for sub in lab_subjects:
            placed = False
            for day in sorted(days, key=lambda x: random.random()):
                if any(v[0] == cls and "Lab" in assignment[v][0] for v in assignment if v[1] == day): continue
                starts = ["10:00-11:30", "02:00-03:30"]
                random.shuffle(starts)
                for start in starts:
                    nxt = next_slot(start)
                    v1, v2 = (cls, day, start), (cls, day, nxt)
                    if v1 in assignment or v2 in assignment: continue
                    fac, _, _ = subjects[cls][sub]
                    for room, typ in rooms.items():
                        if typ != "Lab": continue
                        clash = any(d2 == day and (s2 == start or s2 == nxt) and (fac2 == fac or room2 == room) 
                                    for (c2, d2, s2), (sub2, fac2, room2) in assignment.items())
                        if not clash:
                            assignment[v1] = assignment[v2] = (sub, fac, room)
                            placed = True; break
                    if placed: break
                if placed: break
    return assignment

def select_var(assignment):
    best = None
    min_options = float('inf')
    for v in variables:
        if v in assignment: continue
        cls, day, slot = v
        options = sum(1 for sub, (fac, typ, exp) in subjects[cls].items() 
                     for room, rtype in rooms.items() 
                     if typ == rtype and is_consistent(v, (sub, fac, room), assignment))
        if options == 0: return v
        if options < min_options:
            min_options, best = options, v
    return best

def forward_check(assignment):
    needed = sum(max(0, required[cls][sub] - count_sub(assignment, cls, sub))
                 for cls in required for sub in required[cls] if "Lab" not in sub)
    return (len(variables) - len(assignment)) >= needed

def backtrack(assignment):
    if len(assignment) == len(variables): return assignment
    if not forward_check(assignment): return None
    var = select_var(assignment)
    if var is None: return None
    for val in order_values(var, assignment):
        if is_consistent(var, val, assignment):
            assignment[var] = val
            result = backtrack(assignment)
            if result: return result
            del assignment[var]
    return None

# -------------------------------
# EXECUTION
# -------------------------------
print("Solving with Seniority Priority (Experienced faculty in morning)...")
sol = backtrack(preassign_labs())

if sol:
    # ... [Insert your HTML generation code here from the previous snippet] ...
    print("✅ Success! index.html generated.")