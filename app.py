from flask import Flask, flash, redirect, render_template, request, url_for


app = Flask(__name__)
app.secret_key = "khet2market-demo-secret-key"


# Prototype-only values. These are not live market prices.
MARKET_PRICES = [
    {"crop": "Onion", "price": 2450, "change": 8.4},
    {"crop": "Tomato", "price": 1850, "change": 3.2},
    {"crop": "Soybean", "price": 4720, "change": 5.1},
    {"crop": "Cotton", "price": 6800, "change": -1.4},
]

FARMER_DEMO_DATA = {
    "is_demo": True,
    "market_prices": MARKET_PRICES,
    "produce_lots": [
        {"produce": "Onion", "quantity": "40 Qtl", "status": "Active"},
        {"produce": "Soybean", "quantity": "25 Qtl", "status": "Matched"},
    ],
    "buyer_matches": 6,
    "pending_offers": 2,
}

BUYER_DEMO_DATA = {
    "is_demo": True,
    "market_prices": MARKET_PRICES,
    "recommended_lots": [
        {"produce": "Onion", "quantity": "40 Qtl", "location": "Nashik"},
        {"produce": "Soybean", "quantity": "25 Qtl", "location": "Indore"},
    ],
}

FPO_DEMO_DATA = {
    "is_demo": True,
    "market_prices": MARKET_PRICES,
    "farmer_count": 125,
    "aggregated_quantity": "480 Qtl",
}


def render_farmer(template_name, **context):
    """Render a farmer view with shared prototype data."""
    return render_template(template_name, **FARMER_DEMO_DATA, **context)


def render_buyer(template_name, **context):
    """Render a buyer view with shared prototype data."""
    return render_template(template_name, **BUYER_DEMO_DATA, **context)


def render_fpo(template_name, **context):
    """Render an FPO view with shared prototype data."""
    return render_template(template_name, **FPO_DEMO_DATA, **context)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Authentication will be connected to the backend in a later phase.
        dashboards = {
            "farmer": ("farmer_dashboard", "Farmer"),
            "buyer": ("buyer_dashboard", "Buyer"),
            "fpo": ("fpo_dashboard", "FPO"),
        }
        dashboard_name, role_name = dashboards.get(
            request.form.get("role"), dashboards["farmer"]
        )
        flash(f"Demo {role_name} login received. Welcome back!")
        return redirect(url_for(dashboard_name))
    return render_template("login.html")


@app.route("/register")
def register():
    """Show the three registration options."""
    return render_template("register.html")


@app.route("/register/<role>", methods=["GET", "POST"])
def register_role(role):
    """Show and process the registration form for one platform role."""
    roles = {
        "farmer": ("register_farmer.html", "farmer_dashboard", "Farmer"),
        "buyer": ("register_buyer.html", "buyer_dashboard", "Buyer"),
        "fpo": ("register_fpo.html", "fpo_dashboard", "FPO"),
    }
    registration = roles.get(role)
    if registration is None:
        return redirect(url_for("register"))

    template_name, dashboard_name, role_name = registration
    if request.method == "POST":
        # Registration data is intentionally not persisted until database support is added.
        flash(f"{role_name} registration received. Welcome to Khet2Market!")
        return redirect(url_for(dashboard_name))
    return render_template(template_name)


@app.route("/role-selection")
def role_selection():
    return render_template("role_selection.html")


@app.route("/farmer/dashboard")
def farmer_dashboard():
    return render_farmer("farmer/dashboard.html")


@app.route("/farmer/market-intelligence")
def farmer_market_intelligence():
    return render_farmer("farmer/market_prices.html")


@app.route("/farmer/my-produce", methods=["GET", "POST"])
def farmer_my_produce():
    if request.method == "POST":
        flash("Produce deletion will be available when listings are connected to the database.")
    return render_farmer("farmer/my_produce.html")


@app.route("/farmer/create-lot", methods=["GET", "POST"])
def farmer_create_lot():
    if request.method == "POST":
        lot = {
            "produce": request.form.get("produce", "").strip(),
            "category": request.form.get("category", "").strip(),
            "variety": request.form.get("variety", "").strip(),
            "quantity": request.form.get("quantity", "").strip(),
            "unit": request.form.get("unit", "").strip(),
            "expected_price": request.form.get("expected_price", "").strip(),
            "minimum_price": request.form.get("minimum_price", "").strip(),
            "quality": request.form.get("quality", "").strip(),
            "harvest_date": request.form.get("harvest_date", "").strip(),
            "available_from": request.form.get("available_from", "").strip(),
            "available_until": request.form.get("available_until", "").strip(),
            "village": request.form.get("village", "").strip(),
            "district": request.form.get("district", "").strip(),
            "state": request.form.get("state", "").strip(),
            "location": request.form.get("location", "").strip(),
            "farming_method": request.form.get("farming_method", "").strip(),
            "description": request.form.get("description", "").strip(),
        }
        required_fields = {
            "produce": "Enter the product or crop name.",
            "quantity": "Enter the available quantity.",
            "unit": "Select a unit.",
            "expected_price": "Enter the expected price.",
            "quality": "Select a quality grade.",
            "harvest_date": "Select the harvest date.",
            "location": "Enter the market or collection location.",
        }
        errors = {
            field: message for field, message in required_fields.items() if not lot[field]
        }
        if errors:
            flash("Please complete every produce-lot field.")
            return render_farmer("farmer/add_produce.html", lot=lot, errors=errors)
        flash("Demo produce lot received. Database saving can be connected next.")
        return redirect(url_for("farmer_my_produce"))
    return render_farmer("farmer/add_produce.html")


@app.route("/farmer/buyer-matches")
def farmer_buyer_matches():
    return render_farmer("farmer/buyer_matches.html")


@app.route("/farmer/offers")
def farmer_offers():
    return render_farmer("farmer/offers.html")


@app.route("/farmer/orders")
def farmer_orders():
    return render_farmer("farmer/orders.html")


@app.route("/farmer/logistics")
def farmer_logistics():
    return render_farmer("farmer/logistics.html")


@app.route("/farmer/payments")
def farmer_payments():
    return render_farmer("farmer/payments.html")


@app.route("/farmer/grievances")
def farmer_grievances():
    return render_farmer("farmer/grievances.html")


@app.route("/farmer/profile")
def farmer_profile():
    return render_farmer("farmer/profile.html")


@app.route("/buyer/dashboard")
def buyer_dashboard():
    return render_buyer("buyer/dashboard.html")


@app.route("/buyer/market-intelligence")
def buyer_market_intelligence():
    return render_buyer("buyer/market_intelligence.html")


@app.route("/buyer/find-produce")
def buyer_find_produce():
    return render_buyer("buyer/find_produce.html")


@app.route("/buyer/requirements")
def buyer_requirements():
    return render_buyer("buyer/requirements.html")


@app.route("/buyer/recommended-lots")
def buyer_recommended_lots():
    return render_buyer("buyer/recommended_lots.html")


@app.route("/buyer/offers")
def buyer_offers():
    return render_buyer("buyer/offers.html")


@app.route("/buyer/orders")
def buyer_orders():
    return render_buyer("buyer/orders.html")


@app.route("/buyer/profile")
def buyer_profile():
    return render_buyer("buyer/profile.html")


@app.route("/fpo/dashboard")
def fpo_dashboard():
    return render_fpo("fpo/dashboard.html")


@app.route("/fpo/farmers")
def fpo_farmers():
    return render_fpo("fpo/farmers.html")


@app.route("/fpo/aggregation")
def fpo_aggregation():
    return render_fpo("fpo/aggregation.html")


@app.route("/fpo/lots")
def fpo_lots():
    return render_fpo("fpo/lots.html")


@app.route("/fpo/profile")
def fpo_profile():
    return render_fpo("fpo/profile.html")


if __name__ == "__main__":
    app.run(debug=True)
