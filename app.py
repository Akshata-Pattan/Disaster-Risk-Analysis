import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-secret-key")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL or SUPABASE_KEY is missing in .env")


def get_supabase():
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    access_token = session.get("access_token")
    refresh_token = session.get("refresh_token")
    if access_token and refresh_token:
        try:
            client.auth.set_session(access_token, refresh_token)
        except Exception:
            pass
    return client


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please login to continue.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def calculate_risk(data):
    disaster = data.get("disaster_type", "Flood").lower()

    rainfall = float(data.get("rainfall") or 0)
    temperature = float(data.get("temperature") or 0)
    wind = float(data.get("wind_speed") or 0)
    humidity = float(data.get("humidity") or 0)
    elevation = float(data.get("elevation") or 0)
    population = float(data.get("population_density") or 0)
    previous = int(float(data.get("previous_disasters") or 0))

    # Lightweight rule-based risk engine.
    # Scores are normalized to 0-100 and are intended for academic/demo risk assessment.
    if disaster == "flood":
        rainfall_score = min(rainfall / 300 * 100, 100)
        humidity_score = min(humidity / 100 * 100, 100)
        elevation_score = max(0, 100 - min(elevation / 1000 * 100, 100))
        population_score = min(population / 5000 * 100, 100)
        history_score = min(previous / 5 * 100, 100)
        score = (
            rainfall_score * .30 +
            humidity_score * .15 +
            elevation_score * .20 +
            population_score * .15 +
            history_score * .20
        )
        factors = [
            ("Rainfall", rainfall_score),
            ("Humidity", humidity_score),
            ("Low elevation exposure", elevation_score),
            ("Population density", population_score),
            ("Previous disasters", history_score),
        ]
        recommendations = [
            "Monitor rainfall and local flood alerts.",
            "Keep emergency documents, medicines and water ready.",
            "Avoid low-lying roads and waterlogged areas.",
            "Follow local authority evacuation instructions if issued."
        ]

    elif disaster == "cyclone":
        wind_score = min(wind / 180 * 100, 100)
        rainfall_score = min(rainfall / 300 * 100, 100)
        humidity_score = min(humidity / 100 * 100, 100)
        population_score = min(population / 5000 * 100, 100)
        history_score = min(previous / 5 * 100, 100)
        score = (
            wind_score * .35 +
            rainfall_score * .20 +
            humidity_score * .10 +
            population_score * .15 +
            history_score * .20
        )
        factors = [
            ("Wind speed", wind_score),
            ("Rainfall", rainfall_score),
            ("Humidity", humidity_score),
            ("Population density", population_score),
            ("Previous cyclones", history_score),
        ]
        recommendations = [
            "Secure loose outdoor objects and stay indoors during warnings.",
            "Keep a charged phone, torch, water and emergency kit ready.",
            "Avoid coastal and flooded areas during severe conditions.",
            "Follow official cyclone warnings and evacuation orders."
        ]

    elif disaster == "landslide":
        rainfall_score = min(rainfall / 250 * 100, 100)
        elevation_score = min(elevation / 1500 * 100, 100)
        humidity_score = min(humidity / 100 * 100, 100)
        population_score = min(population / 5000 * 100, 100)
        history_score = min(previous / 5 * 100, 100)
        score = (
            rainfall_score * .30 +
            elevation_score * .20 +
            humidity_score * .15 +
            population_score * .15 +
            history_score * .20
        )
        factors = [
            ("Rainfall", rainfall_score),
            ("Terrain/elevation", elevation_score),
            ("Humidity", humidity_score),
            ("Population density", population_score),
            ("Previous landslides", history_score),
        ]
        recommendations = [
            "Watch for cracks, unusual ground movement and falling rocks.",
            "Avoid steep slopes during prolonged or intense rainfall.",
            "Keep emergency communication and evacuation routes ready.",
            "Follow local warnings in hilly or unstable areas."
        ]

    elif disaster == "wildfire":
        temperature_score = min(max(temperature - 15, 0) / 35 * 100, 100)
        humidity_score = max(0, 100 - humidity)
        wind_score = min(wind / 100 * 100, 100)
        population_score = min(population / 5000 * 100, 100)
        history_score = min(previous / 5 * 100, 100)
        score = (
            temperature_score * .25 +
            humidity_score * .25 +
            wind_score * .20 +
            population_score * .10 +
            history_score * .20
        )
        factors = [
            ("Temperature", temperature_score),
            ("Low humidity", humidity_score),
            ("Wind speed", wind_score),
            ("Population density", population_score),
            ("Previous wildfires", history_score),
        ]
        recommendations = [
            "Avoid open burning and report smoke or fire early.",
            "Keep windows closed if smoke levels become high.",
            "Prepare an evacuation bag and identify safe routes.",
            "Follow local fire-service and authority instructions."
        ]

    elif disaster == "earthquake":
        elevation_score = min(elevation / 2000 * 100, 100)
        population_score = min(population / 5000 * 100, 100)
        history_score = min(previous / 5 * 100, 100)
        score = population_score * .35 + history_score * .45 + elevation_score * .20
        factors = [
            ("Population density", population_score),
            ("Previous earthquakes", history_score),
            ("Terrain/elevation", elevation_score),
        ]
        recommendations = [
            "Identify safe indoor areas away from windows and heavy objects.",
            "Secure shelves and other items that can fall.",
            "During shaking, Drop, Cover and Hold On.",
            "After an earthquake, check for hazards and follow official advice."
        ]

    else:  # tsunami
        wind_score = min(wind / 180 * 100, 100)
        elevation_score = max(0, 100 - min(elevation / 500 * 100, 100))
        population_score = min(population / 5000 * 100, 100)
        history_score = min(previous / 5 * 100, 100)
        score = (
            wind_score * .10 +
            elevation_score * .35 +
            population_score * .20 +
            history_score * .35
        )
        factors = [
            ("Coastal/low elevation exposure", elevation_score),
            ("Population density", population_score),
            ("Previous tsunami events", history_score),
            ("Wind/environmental factor", wind_score),
        ]
        recommendations = [
            "If an official tsunami warning is issued, move inland or to higher ground.",
            "Do not go to the coast to watch unusual waves.",
            "Know your local evacuation route before an emergency.",
            "Follow official warnings until the all-clear is issued."
        ]

    score = round(max(0, min(score, 100)), 2)

    if score < 30:
        level = "Low"
        color = "green"
    elif score < 60:
        level = "Moderate"
        color = "yellow"
    elif score < 80:
        level = "High"
        color = "orange"
    else:
        level = "Extreme"
        color = "red"

    factors.sort(key=lambda x: x[1], reverse=True)
    return score, level, color, factors, recommendations


@app.route("/")
def index():
    return render_template("index.html", user_id=session.get("user_id"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if len(password) < 6:
            flash("Password must contain at least 6 characters.", "danger")
            return redirect(url_for("register"))

        try:
            sb = get_supabase()
            result = sb.auth.sign_up({
                "email": email,
                "password": password,
                "options": {"data": {"full_name": name}}
            })

            if result.user:
                try:
                    sb.table("profiles").upsert({
                        "id": str(result.user.id),
                        "full_name": name,
                        "email": email,
                        "role": "user"
                    }).execute()
                except Exception:
                    pass

            if result.session:
                session["user_id"] = str(result.user.id)
                session["email"] = email
                session["full_name"] = name
                session["access_token"] = result.session.access_token
                session["refresh_token"] = result.session.refresh_token
                flash("Account created successfully!", "success")
                return redirect(url_for("dashboard"))

            flash("Account created. Check your email to confirm your account, then login.", "success")
            return redirect(url_for("login"))

        except Exception as e:
            flash(f"Registration failed: {e}", "danger")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        try:
            sb = get_supabase()
            result = sb.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            session["user_id"] = str(result.user.id)
            session["email"] = email
            session["full_name"] = (result.user.user_metadata or {}).get("full_name", "User")
            session["access_token"] = result.session.access_token
            session["refresh_token"] = result.session.refresh_token

            flash("Welcome back!", "success")
            return redirect(url_for("dashboard"))

        except Exception as e:
            flash("Login failed. Check your email, password, and email confirmation.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    try:
        sb = get_supabase()
        result = (
            sb.table("disaster_analyses")
            .select("*")
            .eq("user_id", session["user_id"])
            .order("created_at", desc=True)
            .execute()
        )
        analyses = result.data or []
    except Exception:
        analyses = []

    total = len(analyses)
    high = sum(1 for x in analyses if x.get("risk_level") in ("High", "Extreme"))
    average = round(sum(float(x.get("risk_score", 0)) for x in analyses) / total, 1) if total else 0

    return render_template(
        "dashboard.html",
        analyses=analyses[:5],
        total=total,
        high=high,
        average=average,
        name=session.get("full_name", "User")
    )


@app.route("/analysis", methods=["GET", "POST"])
@login_required
def analysis():
    if request.method == "POST":
        data = request.form.to_dict()
        score, level, color, factors, recommendations = calculate_risk(data)

        record = {
            "user_id": session["user_id"],
            "location": data.get("location", "Unknown"),
            "disaster_type": data.get("disaster_type", "Flood"),
            "rainfall": float(data.get("rainfall") or 0),
            "temperature": float(data.get("temperature") or 0),
            "wind_speed": float(data.get("wind_speed") or 0),
            "humidity": float(data.get("humidity") or 0),
            "elevation": float(data.get("elevation") or 0),
            "population_density": float(data.get("population_density") or 0),
            "previous_disasters": int(float(data.get("previous_disasters") or 0)),
            "risk_score": score,
            "risk_level": level,
            "recommendations": "\n".join(recommendations)
        }

        try:
            sb = get_supabase()
            sb.table("disaster_analyses").insert(record).execute()
        except Exception as e:
            flash(f"Analysis calculated, but saving failed: {e}", "warning")

        return render_template(
            "result.html",
            score=score,
            level=level,
            color=color,
            factors=factors,
            recommendations=recommendations,
            location=data.get("location"),
            disaster=data.get("disaster_type")
        )

    return render_template("analysis.html")


@app.route("/history")
@login_required
def history():
    try:
        sb = get_supabase()
        result = (
            sb.table("disaster_analyses")
            .select("*")
            .eq("user_id", session["user_id"])
            .order("created_at", desc=True)
            .execute()
        )
        analyses = result.data or []
    except Exception as e:
        analyses = []
        flash(f"Could not load history: {e}", "danger")

    return render_template("history.html", analyses=analyses)


if __name__ == "__main__":
    app.run(debug=True)
