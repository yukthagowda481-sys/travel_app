from flask import Flask, render_template, request, redirect, url_for
import math
import os
import matplotlib.pyplot as plt
import requests

app = Flask(__name__)

# ---------------- PACKING LIST ----------------
packing_list = [
    "Toothpaste", "Toothbrush", "Soap", "Shampoo", "Hair oil",
    "Comb", "Facewash", "Pants", "Shirts", "Sarees", "Kurtis",
    "Innerwear", "Sandals", "Shoes", "Perfume", "Wallet",
    "Phone", "Charger", "Tickets", "ID Proof"
]

# ---------------- CITY COORDINATES ----------------
cities = {
    "Bangalore": (12.9716, 77.5946),
    "Mumbai": (19.0760, 72.8777),
    "Delhi": (28.7041, 77.1025),
    "Chennai": (13.0827, 80.2707),
    "Hyderabad": (17.3850, 78.4867),
    "Kolkata": (22.5726, 88.3639)
}

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------- BUDGET TRACKER ----------------
@app.route("/budget", methods=["GET", "POST"])
def budget():
    result = None

    if request.method == "POST":
        try:
            hotel = float(request.form["hotel"])
            food = float(request.form["food"])
            transport = float(request.form["transport"])
            shopping = float(request.form["shopping"])

            result = hotel + food + transport + shopping

            labels = ['Hotel', 'Food', 'Transport', 'Shopping']
            values = [hotel, food, transport, shopping]

            plt.clf()
            plt.figure(figsize=(5, 5))
            plt.pie(values, labels=labels, autopct='%1.1f%%')
            plt.title("Expense Distribution")

            if not os.path.exists("static"):
                os.makedirs("static")

            plt.savefig("static/budget_chart.png")
            plt.close()

        except:
            result = "Please enter valid numbers."

    return render_template("budget.html", result=result)

# ---------------- ROUTE (REAL DISTANCE) ----------------
@app.route("/route", methods=["GET", "POST"])
def route():
    distance = None
    duration = None
    city1 = None
    city2 = None
    error = None

    if request.method == "POST":
        city1 = request.form["city1"]
        city2 = request.form["city2"]

        if city1 == city2:
            error = "⚠️ Please select different cities."
        else:
            try:
                lat1, lon1 = cities[city1]
                lat2, lon2 = cities[city2]

                url = "https://api.openrouteservice.org/v2/directions/driving-car"

                headers = {
                    "Authorization": "5b3ce3597851110001cf6248abcd1234xyz",
                    "Content-Type": "application/json"
                }

                body = {
                    "coordinates": [
                        [lon1, lat1],
                        [lon2, lat2]
                    ]
                }

                response = requests.post(url, json=body, headers=headers, timeout=10)
                data = response.json()

                distance = data["routes"][0]["summary"]["distance"] / 1000  # km
                duration = data["routes"][0]["summary"]["duration"] / 60  # minutes

                distance = round(distance, 2)
                duration = round(duration, 2)

            except:
                error = "❌ Error fetching route. Check API or internet."

    return render_template("route.html",
                           cities=cities.keys(),
                           distance=distance,
                           duration=duration,
                           city1=city1,
                           city2=city2,
                           error=error)

# ---------------- PACKING CHECKLIST ----------------
@app.route("/packing", methods=["GET", "POST"])
def packing():
    message = ""

    if request.method == "POST":
        item = request.form["item"]

        if item.lower() == "gold jewellery":
            message = "⚠️ Gold jewellery is not recommended for travel."
        else:
            packing_list.append(item)
            message = "Item added successfully!"

    return render_template("packing.html",
                           items=packing_list,
                           message=message)

@app.route("/delete/<item>")
def delete(item):
    if item in packing_list:
        packing_list.remove(item)
    return redirect(url_for("packing"))

# ---------------- WEATHER ----------------
@app.route("/weather", methods=["GET", "POST"])
def weather():
    result = None

    if request.method == "POST":
        city = request.form["city"]

        try:
            url = f"https://wttr.in/{city}?format=j1"
            response = requests.get(url, timeout=5)
            data = response.json()

            temp = data["current_condition"][0]["temp_C"]
            desc = data["current_condition"][0]["weatherDesc"][0]["value"]
            humidity = data["current_condition"][0]["humidity"]

            result = f"Weather in {city.title()}: {temp}°C, {desc}, Humidity: {humidity}%"

        except:
            result = "City not found or network error. Try again!"

    return render_template("weather.html", result=result)

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)