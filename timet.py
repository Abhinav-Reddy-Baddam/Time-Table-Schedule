import json
import random
import statistics
import datetime


try:
    with open("data.json", "r") as f:
        data = json.load(f)
except FileNotFoundError:
    print("❌ Error: data.json not found in this folder!")
    exit()

classes = data["classes"]
rooms = data["rooms"]


days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
time_slots = ["10:00-11:30", "11:30-01:00", "02:00-03:30", "03:30-05:00"]
priority_slots = ["10:00-11:30", "11:30-01:00", "02:00-03:30"]

all_exp = [d.get("experience", 0) for c in classes.values() for d in c.values()]
SENIOR_THRESHOLD = statistics.median(all_exp) if all_exp else 0

def next_slot(slot):
    i = time_slots.index(slot)
    return time_slots[i + 1] if i < len(time_slots) - 1 else None


subjects = {}
required = {}
for cls, subs in classes.items():
    subjects[cls] = {s: (d["faculty"], d["type"], d.get("experience", 0)) for s, d in subs.items()}
    subjects[cls]["FREE"] = ("None", "Theory", 0)
    required[cls] = {s: d["required"] for s, d in subs.items()}


def count_sub(assignment, cls, sub):
    count = sum(1 for (c, _, _), v in assignment.items() if c == cls and v[0] == sub)
    return count // 2 if "Lab" in sub else count

def is_consistent(var, value, assignment):
    cls, day, slot = var
    sub, fac, room = value
    _, typ, exp = subjects[cls][sub]

    if var in assignment: return False

    # Juniors (F4) can't take Slot 1 or 2 for Labs
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
                
                # Push Junior Labs to afternoon
                starts = ["02:00-03:30", "10:00-11:30"] if exp < SENIOR_THRESHOLD else ["10:00-11:30", "02:00-03:30"]
                
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
        if slot in priority_slots:
            return -1000 - exp
        return exp

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


print("🚀 Optimizing Senior Faculty Placement...")
vars_list = [(cls, d, t) for cls in classes for d in days for t in time_slots]
vars_list.sort(key=lambda x: priority_slots.index(x[2]) if x[2] in priority_slots else 99)

solution = backtrack(preassign_labs(), vars_list)

if solution:
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>College Timetable</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #f0f2f5; padding: 20px; }}
            .nav {{ position: sticky; top: 0; background: white; padding: 15px; display: flex; gap: 10px; justify-content: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); border-radius: 8px; margin-bottom: 20px; z-index: 1000; }}
            input {{ padding: 10px; width: 300px; border: 1px solid #ddd; border-radius: 4px; }}
            button {{ padding: 10px 20px; background: #2e7d32; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }}
            .class-card {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid #eee; padding: 12px; text-align: center; }}
            th {{ background: #2e7d32; color: white; }}
            .highlight {{ background: #fff3cd !important; border: 2px solid #ffc107 !important; font-weight: bold; }}
            .fade {{ opacity: 0.1; }}
            .lab {{ background: #e8f5e9; font-weight: bold; border-left: 5px solid #2e7d32; }}
            .free {{ color: #ccc; font-style: italic; }}
            @media print {{ .nav {{ display: none; }} }}
        </style>
    </head>
    <body>
        <div class="nav">
            <input type="text" id="q" placeholder="Search Faculty (Exact)..." onkeyup="search()">
            <button onclick="window.print()">Print Schedule</button>
        </div>
        <h1 style="text-align:center">University Master Timetable</h1>
    """
    for cls in sorted(classes.keys()):
        html_content += f"<div class='class-card'><h2>Class: {cls}</h2><table><tr><th>Day</th>"
        for t in time_slots: html_content += f"<th>{t}</th>"
        html_content += "</tr>"
        for d in days:
            html_content += f"<tr><td><strong>{d}</strong></td>"
            for t in time_slots:
                res = solution.get((cls, d, t))
                sub, fac, room = res if res else ("FREE", "None", "-")
                c_name = "lab" if "Lab" in sub else ("free" if sub == "FREE" else "")
                html_content += f"<td class='{c_name}' data-f='{fac}'>{sub}<br><small>{fac} ({room})</small></td>"
            html_content += "</tr>"
        html_content += "</table></div>"
    
    html_content += f"<p style='text-align:center; color:gray;'>Last Updated: {current_time}</p>"
    html_content += """
    <script>
    function search() {
        let q = document.getElementById('q').value.trim().toUpperCase();
        
        document.querySelectorAll('td[data-f]').forEach(td => {
            if (!q) { 
                td.classList.remove('highlight', 'fade'); 
                return; 
            }

            
            let facAttr = td.getAttribute('data-f').toUpperCase();
            
           
            let cellText = td.innerText.toUpperCase();

            
            if (facAttr === q || (cellText.includes(q) && facAttr !== "NONE")) {
                td.classList.add('highlight'); 
                td.classList.remove('fade');
            } else {
                td.classList.add('fade'); 
                td.classList.remove('highlight');
            }
        });
    }
    </script></body></html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("✅ Success! index.html has been generated.")
else:
    print("❌ Error: No solution found. The constraints (Seniors in morning) might be too strict for the rooms available.")