from flask import Flask, render_template_string, redirect, request
import requests
import random
import time

app = Flask(__name__)

# Replace with your actual deployed URL
TARGET_URL = "http://localhost:5000/data"

CUSTOMERS = ["Factory A", "Plant B", "Warehouse C", "Remote Site D"]
HW_VERSIONS = ["v1.0", "v1.1", "v2.0", "v2.1"]
SW_VERSIONS = ["1.0.0", "1.2.3", "2.0.1", "3.1.4"]

template = """
<!DOCTYPE html>
<html>
<head><title>ESP Simulator</title></head>
<body style="font-family: sans-serif; padding: 2rem;">
    <h2>ESP Device Simulator</h2>
    <form method="POST">
        <label>Number of Devices:</label>
        <input type="number" name="count" value="5" min="1" max="100">
        <button type="submit">Simulate!</button>
    </form>
    {% if result %}
        <p style="color:green;">✅ {{ result }}</p>
    {% endif %}
</body>
</html>
"""

def generate_device_data(index):
    return {
        "serial": f"ESP{1000 + index}",
        "customer": random.choice(CUSTOMERS),
        "sw_version": random.choice(SW_VERSIONS),
        "hw_version": random.choice(HW_VERSIONS)
    }

@app.route("/", methods=["GET", "POST"])
def simulate():
    result = None
    if request.method == "POST":
        count = int(request.form.get("count", 5))
        success = 0
        for i in range(count):
            data = generate_device_data(i)
            try:
                r = requests.post(TARGET_URL, json=data, timeout=5)
                if r.ok:
                    success += 1
            except Exception as e:
                print(f"Error sending data for ESP{i}: {e}")
            time.sleep(0.2)  # simulate slight delay
        result = f"{success}/{count} devices reported successfully."
    return render_template_string(template, result=result)

if __name__ == "__main__":
    app.run(debug=True,  host="0.0.0.0",port=8000)
