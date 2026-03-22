from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# In-memory data stores
members = {}
classes = {}
_member_id_counter = 1
_class_id_counter = 1


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


# ---------- HEALTH ----------

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "ACEest Fitness & Gym"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
