from flask import Flask, render_template, redirect, url_for
import requests

app = Flask(__name__)

ALLOWED_POKEMON_IDS = [1, 4, 7, 25, 39, 52, 54, 94, 95, 143]
ALLOWED_POKEMON_ID_SET = set(ALLOWED_POKEMON_IDS)


def get_pokeapi_payload(identifier):
    endpoint = f"https://pokeapi.co/api/v2/pokemon/{identifier}"
    try:
        resp = requests.get(endpoint, timeout=8)
    except requests.RequestException:
        return None
    if resp.status_code != 200:
        return None
    return resp.json()


def to_view_model(payload):
    return {
        "id": payload["id"],
        "nombre": payload["name"].capitalize(),
        "tipo": [entry["type"]["name"].capitalize() for entry in payload["types"]],
        "imagen": payload["sprites"]["front_default"],
        "altura": f"{payload['height'] / 10} m",
        "peso": f"{payload['weight'] / 10} kg",
        "habilidades": [a["ability"]["name"].capitalize() for a in payload["abilities"]],
        "estadisticas": {s["stat"]["name"]: s["base_stat"] for s in payload["stats"]},
    }


def fetch_one(identifier):
    data = get_pokeapi_payload(identifier)
    if data is None:
        return None
    return to_view_model(data)


@app.route("/")
def route_root():
    return redirect(url_for("route_first_ten"))


@app.route("/pokemon")
def route_first_ten():

    items = []
    for pid in ALLOWED_POKEMON_IDS:
        vm = fetch_one(pid)
        if vm is not None:
            items.append(vm)
    return render_template("pokemon.html", pokemones=items)


@app.route("/pokemon/primeros5")
def route_first_five():
    
    selected_ids = ALLOWED_POKEMON_IDS[:5]
    items = []
    for pid in selected_ids:
        vm = fetch_one(pid)
        if vm is not None:
            items.append(vm)
    return render_template("pokemon.html", pokemones=items)


@app.route("/pokemon/todos")
def route_all_allowed():
    
    items = []
    for pid in ALLOWED_POKEMON_IDS:
        vm = fetch_one(pid)
        if vm is not None:
            items.append(vm)
    return render_template("pokemon.html", pokemones=items)


@app.route("/pokemon/<identifier>")
def route_single(identifier):
    if identifier.startswith("cantidad"):
        return render_template("404.html"), 404
    vm = fetch_one(identifier.lower())
    if vm is None:
        return render_template("404.html"), 404
  
    if vm["id"] not in ALLOWED_POKEMON_ID_SET:
        return render_template("404.html"), 404
    return render_template("pokemon.html", pokemones=[vm])


@app.route("/pokemon/cantidad/<int:amount>")
def route_amount(amount):
  
    safe_amount = min(max(amount, 0), len(ALLOWED_POKEMON_IDS))
    selected_ids = ALLOWED_POKEMON_IDS[:safe_amount]
    items = []
    for pid in selected_ids:
        vm = fetch_one(pid)
        if vm is not None:
            items.append(vm)
    return render_template("pokemon.html", pokemones=items)


@app.errorhandler(404)
def route_404(_):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
