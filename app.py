from flask import Flask, jsonify, request, abort, render_template_string

app = Flask(__name__)

# In-memory data stores
members = {}
classes = {}
_member_id_counter = 1
_class_id_counter = 1

# ---------- PROGRAM DATA (from ACEest baseline scripts) ----------
PROGRAMS = {
    "Fat Loss (FL)": {
        "code": "FL",
        "workout": "Mon: 5x5 Back Squat + AMRAP | Tue: EMOM 20min Assault Bike | Wed: Bench Press + 21-15-9 | Thu: 10RFT Deadlifts/Box Jumps | Fri: 30min Active Recovery",
        "diet": "Breakfast: 3 Egg Whites + Oats Idli | Lunch: Grilled Chicken + Brown Rice | Dinner: Fish Curry + Millet Roti | Target: 2,000 kcal",
        "color": "#e74c3c"
    },
    "Muscle Gain (MG)": {
        "code": "MG",
        "workout": "Mon: Squat 5x5 | Tue: Bench 5x5 | Wed: Deadlift 4x6 | Thu: Front Squat 4x8 | Fri: Incline Press 4x10 | Sat: Barbell Rows 4x10",
        "diet": "Breakfast: 4 Eggs + PB Oats | Lunch: Chicken Biryani (250g Chicken) | Dinner: Mutton Curry + Jeera Rice | Target: 3,200 kcal",
        "color": "#2ecc71"
    },
    "Beginner (BG)": {
        "code": "BG",
        "workout": "Circuit Training: Air Squats, Ring Rows, Push-ups | Focus: Technique Mastery & Form (90% Threshold)",
        "diet": "Balanced Meals: Idli-Sambar, Rice-Dal, Chapati | Protein: 120g/day",
        "color": "#3498db"
    }
}


# ---------- HOME UI ----------

HOME_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>ACEest Fitness & Gym</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet"/>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css" rel="stylesheet"/>
  <style>
    body { background: #0f0f0f; color: #f0f0f0; font-family: 'Segoe UI', sans-serif; }
    .navbar { background: linear-gradient(90deg, #ff6a00, #ee0979); }
    .navbar-brand { font-weight: 800; font-size: 1.5rem; letter-spacing: 1px; }
    .stat-card { background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 16px; padding: 24px; text-align: center; }
    .stat-card .number { font-size: 3rem; font-weight: 800; color: #ff6a00; }
    .stat-card .label { color: #aaa; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; }
    .section-card { background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 16px; padding: 24px; margin-bottom: 24px; }
    .section-card h5 { color: #ff6a00; font-weight: 700; margin-bottom: 16px; }
    .form-control, .form-select { background: #111; border: 1px solid #333; color: #f0f0f0; }
    .form-control:focus, .form-select:focus { background: #111; color: #f0f0f0; border-color: #ff6a00; box-shadow: 0 0 0 0.2rem rgba(255,106,0,0.25); }
    .form-control::placeholder { color: #888; opacity: 1; }
    .form-select option { background: #1a1a1a; color: #f0f0f0; }
    .btn-primary { background: linear-gradient(90deg, #ff6a00, #ee0979); border: none; font-weight: 600; }
    .btn-primary:hover { opacity: 0.85; background: linear-gradient(90deg, #ff6a00, #ee0979); }
    .btn-danger { background: #c0392b; border: none; }
    .table { color: #f0f0f0; }
    .table thead th { color: #ff6a00; border-color: #2a2a2a; font-weight: 700; }
    .table td, .table th { border-color: #2a2a2a; vertical-align: middle; }
    .badge-basic { background: #2d6a4f; }
    .badge-premium { background: #9b2226; }
    .badge-vip { background: #7b2d8b; }
    .status-dot { width: 10px; height: 10px; background: #2ecc71; border-radius: 50%; display: inline-block; margin-right: 6px; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
    .hero { background: linear-gradient(135deg, #1a1a1a, #0f0f0f); border-radius: 16px; padding: 48px 32px; text-align: center; margin-bottom: 32px; border: 1px solid #2a2a2a; }
    .hero h1 { font-size: 2.8rem; font-weight: 900; background: linear-gradient(90deg, #ff6a00, #ee0979); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .hero p { color: #aaa; font-size: 1.1rem; }
    .empty-state { color: #555; text-align: center; padding: 24px; }
  </style>
</head>
<body>

<nav class="navbar navbar-dark px-4 py-3 mb-4">
  <span class="navbar-brand"><i class="bi bi-lightning-charge-fill me-2"></i>ACEest Fitness & Gym</span>
  <span class="text-white-50 small"><span class="status-dot"></span>System Online</span>
</nav>

<div class="container pb-5">

  <!-- Hero -->
  <div class="hero">
    <h1>Welcome to ACEest Gym</h1>
    <p>Manage members, classes, and keep your gym running at peak performance.</p>
  </div>

  <!-- Programs -->
  <div class="row g-4 mb-4" id="programsRow"></div>

  <!-- Stats -->
  <div class="row g-4 mb-4" id="stats">
    <div class="col-md-4">
      <div class="stat-card">
        <div class="number" id="memberCount">—</div>
        <div class="label"><i class="bi bi-people-fill me-1"></i>Total Members</div>
      </div>
    </div>
    <div class="col-md-4">
      <div class="stat-card">
        <div class="number" id="classCount">—</div>
        <div class="label"><i class="bi bi-calendar-event-fill me-1"></i>Active Classes</div>
      </div>
    </div>
    <div class="col-md-4">
      <div class="stat-card">
        <div class="number" style="color:#2ecc71; font-size:2rem;">HEALTHY</div>
        <div class="label"><i class="bi bi-heart-pulse-fill me-1"></i>System Status</div>
      </div>
    </div>
  </div>

  <div class="row g-4">

    <!-- LEFT: Members -->
    <div class="col-lg-6">

      <!-- Add Member Form -->
      <div class="section-card">
        <h5><i class="bi bi-person-plus-fill me-2"></i>Register New Member</h5>
        <div class="mb-3">
          <input type="text" id="mName" class="form-control" placeholder="Full Name" />
        </div>
        <div class="mb-3">
          <input type="email" id="mEmail" class="form-control" placeholder="Email Address" />
        </div>
        <div class="mb-3">
          <select id="mType" class="form-select">
            <option value="basic">Basic</option>
            <option value="premium">Premium</option>
            <option value="vip">VIP</option>
          </select>
        </div>
        <button class="btn btn-primary w-100" onclick="addMember()">
          <i class="bi bi-plus-circle me-1"></i>Add Member
        </button>
        <div id="mMsg" class="mt-2 small"></div>
      </div>

      <!-- Members List -->
      <div class="section-card">
        <h5><i class="bi bi-people-fill me-2"></i>Members</h5>
        <div id="membersList"></div>
      </div>
    </div>

    <!-- RIGHT: Classes -->
    <div class="col-lg-6">

      <!-- Add Class Form -->
      <div class="section-card">
        <h5><i class="bi bi-calendar-plus-fill me-2"></i>Add New Class</h5>
        <div class="mb-3">
          <input type="text" id="cName" class="form-control" placeholder="Class Name (e.g. Yoga)" />
        </div>
        <div class="mb-3">
          <input type="text" id="cInstructor" class="form-control" placeholder="Instructor Name" />
        </div>
        <div class="mb-3">
          <input type="text" id="cSchedule" class="form-control" placeholder="Schedule (e.g. Mon 9am)" />
        </div>
        <div class="mb-3">
          <input type="number" id="cCapacity" class="form-control" placeholder="Capacity (default 20)" />
        </div>
        <button class="btn btn-primary w-100" onclick="addClass()">
          <i class="bi bi-plus-circle me-1"></i>Add Class
        </button>
        <div id="cMsg" class="mt-2 small"></div>
      </div>

      <!-- Classes List -->
      <div class="section-card">
        <h5><i class="bi bi-calendar-event-fill me-2"></i>Classes</h5>
        <div id="classesList"></div>
      </div>
    </div>

  </div>
</div>

<script>
  const badgeClass = t => t === 'premium' ? 'badge-premium' : t === 'vip' ? 'badge-vip' : 'badge-basic';

  async function loadMembers() {
    const res = await fetch('/members');
    const data = await res.json();
    document.getElementById('memberCount').textContent = data.length;
    const el = document.getElementById('membersList');
    if (!data.length) { el.innerHTML = '<div class="empty-state"><i class="bi bi-inbox fs-3 d-block mb-2"></i>No members yet</div>'; return; }
    el.innerHTML = `<table class="table table-sm"><thead><tr><th>Name</th><th>Email</th><th>Type</th><th></th></tr></thead><tbody>` +
      data.map(m => `<tr>
        <td><i class="bi bi-person-circle me-1 text-warning"></i>${m.name}</td>
        <td class="text-light small">${m.email}</td>
        <td><span class="badge ${badgeClass(m.membership_type)}">${m.membership_type}</span></td>
        <td><button class="btn btn-danger btn-sm py-0" onclick="deleteMember(${m.id})"><i class="bi bi-trash"></i></button></td>
      </tr>`).join('') + `</tbody></table>`;
  }

  async function loadClasses() {
    const res = await fetch('/classes');
    const data = await res.json();
    document.getElementById('classCount').textContent = data.length;
    const el = document.getElementById('classesList');
    if (!data.length) { el.innerHTML = '<div class="empty-state"><i class="bi bi-inbox fs-3 d-block mb-2"></i>No classes yet</div>'; return; }
    el.innerHTML = `<table class="table table-sm"><thead><tr><th>Class</th><th>Instructor</th><th>Schedule</th><th>Cap</th></tr></thead><tbody>` +
      data.map(c => `<tr>
        <td><i class="bi bi-activity me-1 text-danger"></i>${c.name}</td>
        <td class="text-light small">${c.instructor}</td>
        <td class="text-light small">${c.schedule}</td>
        <td><span class="badge bg-secondary">${c.capacity}</span></td>
      </tr>`).join('') + `</tbody></table>`;
  }

  async function addMember() {
    const name = document.getElementById('mName').value.trim();
    const email = document.getElementById('mEmail').value.trim();
    const membership_type = document.getElementById('mType').value;
    const msg = document.getElementById('mMsg');
    if (!name || !email) { msg.innerHTML = '<span class="text-danger">Name and email are required.</span>'; return; }
    const res = await fetch('/members', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({name, email, membership_type}) });
    if (res.ok) {
      msg.innerHTML = '<span class="text-success"><i class="bi bi-check-circle me-1"></i>Member added!</span>';
      document.getElementById('mName').value = '';
      document.getElementById('mEmail').value = '';
      loadMembers();
    } else {
      msg.innerHTML = '<span class="text-danger">Failed to add member.</span>';
    }
  }

  async function deleteMember(id) {
    await fetch('/members/' + id, { method: 'DELETE' });
    loadMembers();
  }

  async function addClass() {
    const name = document.getElementById('cName').value.trim();
    const instructor = document.getElementById('cInstructor').value.trim();
    const schedule = document.getElementById('cSchedule').value.trim() || 'TBD';
    const capacity = parseInt(document.getElementById('cCapacity').value) || 20;
    const msg = document.getElementById('cMsg');
    if (!name || !instructor) { msg.innerHTML = '<span class="text-danger">Name and instructor are required.</span>'; return; }
    const res = await fetch('/classes', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({name, instructor, schedule, capacity}) });
    if (res.ok) {
      msg.innerHTML = '<span class="text-success"><i class="bi bi-check-circle me-1"></i>Class added!</span>';
      document.getElementById('cName').value = '';
      document.getElementById('cInstructor').value = '';
      document.getElementById('cSchedule').value = '';
      document.getElementById('cCapacity').value = '';
      loadClasses();
    } else {
      msg.innerHTML = '<span class="text-danger">Failed to add class.</span>';
    }
  }

  async function loadPrograms() {
    const res = await fetch('/programs');
    const data = await res.json();
    const el = document.getElementById('programsRow');
    el.innerHTML = data.map(p => `
      <div class="col-md-4">
        <div class="section-card h-100" style="border-left: 4px solid ${p.color}">
          <h5 style="color:${p.color}"><i class="bi bi-trophy-fill me-2"></i>${p.code} Program</h5>
          <p class="small text-light mb-2"><strong style="color:#ddd">Workout:</strong><br>${p.workout.replace(/\|/g,'<br>')}</p>
          <p class="small text-light mb-0"><strong style="color:#ddd">Diet:</strong><br>${p.diet.replace(/\|/g,'<br>')}</p>
        </div>
      </div>`).join('');
  }

  loadPrograms();
  loadMembers();
  loadClasses();
</script>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def home():
    return render_template_string(HOME_HTML)


# ---------- MEMBERS ----------

@app.route("/members", methods=["GET"])
def get_members():
    return jsonify(list(members.values())), 200


@app.route("/members/<int:member_id>", methods=["GET"])
def get_member(member_id):
    member = members.get(member_id)
    if not member:
        abort(404)
    return jsonify(member), 200


@app.route("/members", methods=["POST"])
def add_member():
    global _member_id_counter
    data = request.get_json()
    if not data or not data.get("name") or not data.get("email"):
        abort(400)
    member = {
        "id": _member_id_counter,
        "name": data["name"],
        "email": data["email"],
        "membership_type": data.get("membership_type", "basic"),
    }
    members[_member_id_counter] = member
    _member_id_counter += 1
    return jsonify(member), 201


@app.route("/members/<int:member_id>", methods=["DELETE"])
def delete_member(member_id):
    if member_id not in members:
        abort(404)
    deleted = members.pop(member_id)
    return jsonify(deleted), 200


# ---------- CLASSES ----------

@app.route("/classes", methods=["GET"])
def get_classes():
    return jsonify(list(classes.values())), 200


@app.route("/classes/<int:class_id>", methods=["GET"])
def get_class(class_id):
    gym_class = classes.get(class_id)
    if not gym_class:
        abort(404)
    return jsonify(gym_class), 200


@app.route("/classes", methods=["POST"])
def add_class():
    global _class_id_counter
    data = request.get_json()
    if not data or not data.get("name") or not data.get("instructor"):
        abort(400)
    gym_class = {
        "id": _class_id_counter,
        "name": data["name"],
        "instructor": data["instructor"],
        "schedule": data.get("schedule", "TBD"),
        "capacity": data.get("capacity", 20),
    }
    classes[_class_id_counter] = gym_class
    _class_id_counter += 1
    return jsonify(gym_class), 201


# ---------- PROGRAMS ----------

@app.route("/programs", methods=["GET"])
def get_programs():
    return jsonify(list(PROGRAMS.values())), 200


@app.route("/programs/<code>", methods=["GET"])
def get_program(code):
    for prog in PROGRAMS.values():
        if prog["code"] == code.upper():
            return jsonify(prog), 200
    abort(404)


# ---------- HEALTH ----------

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "ACEest Fitness & Gym"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
