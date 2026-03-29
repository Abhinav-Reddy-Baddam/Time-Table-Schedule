import json
import random
import statistics

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
time_slots = ["10:00-11:30", "11:30-01:00", "02:00-03:30", "03:30-05:00"]
# Updated morning priority to include the 3rd slot as requested
priority_slots = ["10:00-11:30", "11:30-01:00", "02:00-03:30"]

all_exp = [d.get("experience", 0) for c in classes.values() for d in c.values()]
SENIOR_THRESHOLD = statistics.median(all_exp) if all_exp else 0

def next_slot(slot):
    i = time_slots.index(slot)
    return time_slots[i + 1] if i < len(time_slots) - 1 else None

# -------------------------------
# BUILD STRUCTURES
# -------------------------------
subjects = {}
required = {}
for cls, subs in classes.items():
    subjects[cls] = {s: (d["faculty"], d["type"], d.get("experience", 0)) for s, d in subs.items()}
    subjects[cls]["FREE"] = ("None", "Theory", 0)
    required[cls] = {s: d["required"] for s, d in subs.items()}

# -------------------------------
# LOGIC
# -------------------------------
def count_sub(assignment, cls, sub):
    count = sum(1 for (c, _, _), v in assignment.items() if c == cls and v[0] == sub)
    return count // 2 if "Lab" in sub else count

def is_consistent(var, value, assignment):
    cls, day, slot = var
    sub, fac, room = value
    _, typ, exp = subjects[cls][sub]

    if var in assignment: return False

    # Hard Constraint: Only allow Labs in morning if Faculty is Senior
    if "Lab" in sub and exp < SENIOR_THRESHOLD:
        if slot in ["10:00-11:30", "11:30-01:00"]:
            return False

    if sub in required[cls] and count_sub(assignment, cls, sub) >= required[cls][sub]:
        return False

    for (c2, d2, s2), (sub2, fac2, room2) in assignment.items():
        if d2 == day and s2 == slot:
            if (fac2 == fac and fac != "None") or room2 == room:
                return False

    if typ == "Theory" and sub != "FREE":
        if any(c2 == cls and d2 == day and sub2 == sub for (c2, d2, s2), (sub2, fac2, room2) in assignment.items()):
            return False

    return True

def preassign_labs():
    assignment = {}
    cls_list = list(classes.keys())
    random.shuffle(cls_list)
    for cls in cls_list:
        labs = [s for s in required[cls] if "Lab" in s]
        for sub in labs:
            placed = False
            for day in sorted(days, key=lambda k: random.random()):
                if any(v[0] == cls and "Lab" in assignment[v][0] for v in assignment if v[1] == day): continue
                fac, _, exp = subjects[cls][sub]
                
                # JUNIOR LABS (F4) MUST GO TO AFTERNOON
                if exp < SENIOR_THRESHOLD:
                    starts = ["02:00-03:30"]
                else:
                    starts = ["10:00-11:30", "02:00-03:30"]
                
                for start in starts:
                    nxt = next_slot(start)
                    if not nxt: continue
                    v1, v2 = (cls, day, start), (cls, day, nxt)
                    if v1 in assignment or v2 in assignment: continue
                    for room, rtyp in rooms.items():
                        if rtyp != "Lab": continue
                        clash = any(d2 == day and (s2 == start or s2 == nxt) and (f2 == fac or r2 == room) 
                                    for (c2, d2, s2), (sub2, f2, r2) in assignment.items())
                        if not clash:
                            assignment[v1] = assignment[v2] = (sub, fac, room)
                            placed = True; break
                    if placed: break
                if placed: break
    return assignment

def order_values(var, assignment):
    cls, _, slot = var
    vals = []
    for sub, (fac, typ, exp) in subjects[cls].items():
        if sub in required[cls] and count_sub(assignment, cls, sub) >= required[cls][sub]: continue
        for r, rt in rooms.items():
            if typ == rt: vals.append((sub, fac, r, exp))
    
    def score(v):
        sub_name, _, _, exp = v
        if sub_name == "FREE": return 5000 
        
        # Priority for slots 1, 2, and 3
        if slot in priority_slots:
            return -1000 - exp # Higher experience = lower score = tried first
        else:
            return exp # Juniors fill the end of the day

    vals.sort(key=score)
    return [(v[0], v[1], v[2]) for v in vals]

def backtrack(assignment, variables):
    if len(assignment) == len(variables): return assignment
    var = next((v for v in variables if v not in assignment), None)
    if not var: return None
    for val in order_values(var, assignment):
        if is_consistent(var, val, assignment):
            assignment[var] = val
            res = backtrack(assignment, variables)
            if res: return res
            del assignment[var]
    return None

# -------------------------------
# RUN
# -------------------------------
print("Optimizing Senior Faculty Placement...")
vars_list = [(cls, d, t) for cls in classes for d in days for t in time_slots]
# Sort to fill priority slots first
vars_list.sort(key=lambda x: priority_slots.index(x[2]) if x[2] in priority_slots else 99)

solution = backtrack(preassign_labs(), vars_list)

if solution:
    # (HTML generation code same as previous, including the exact-match search bar)
    print("✅ Success! Senior faculty prioritized in slots 1, 2, and 3.")
    # ... [Same HTML block as before] ...