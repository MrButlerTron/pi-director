from flask import Flask, request, redirect, jsonify, render_template, render_template_string
import json
import os
import re

app = Flask(__name__)

# Path to the JSON configuration file
CONFIG_FILE = "pi.json"

def load_config():
    """
    Load the configuration from the JSON file.
    """
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"Configuration file '{CONFIG_FILE}' not found.")
    
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

@app.route('/', methods=['GET'])
def handle_request():
    # Load configuration dynamically
    try:
        config = load_config()
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 500
    
    # Extract variables from the configuration
    DISPLAY1 = config.get("DISPLAY1", [])
    DISPLAY2 = config.get("DISPLAY2", [])
    DISPLAY3 = config.get("DISPLAY3", [])
    BOARD1 = config.get("BOARD1", [])
    BOARD2 = config.get("BOARD2", [])
    BOARD3 = config.get("BOARD3", [])
    MEETURL = config.get("MEETURL", "")
    PLATFORM1 = config.get("PLATFORM1", "")
    PLATFORM2 = config.get("PLATFORM2", "")
    PLATFORM3 = config.get("PLATFORM3", "")
    DISPLAYARGS = config.get("DISPLAYARGS", "")
    STREAM = config.get("STREAM", [])

    # URLs for redirection
    urls = []
    host = request.args.get('host')

    if host in DISPLAY1:
        urls.append(f"{MEETURL}/platforms/{PLATFORM1}/display{DISPLAYARGS}")
    if host in DISPLAY2:
        urls.append(f"{MEETURL}/platforms/{PLATFORM2}/display{DISPLAYARGS}")
    if host in DISPLAY3:
        urls.append(f"{MEETURL}/platforms/{PLATFORM3}/display{DISPLAYARGS}")
    if host in BOARD1:
        urls.append(f"{MEETURL}/platforms/{PLATFORM1}/board?scroll=true")
    if host in BOARD2:
        urls.append(f"{MEETURL}/platforms/{PLATFORM2}/board?scroll=true")
    if host in BOARD3:
        urls.append(f"{MEETURL}/platforms/{PLATFORM3}/board?scroll=true")
    if host in STREAM:
        urls.append(f"{MEETURL}/liveFeed/version1")

    # Redirect to a single URL if only one is found
    if len(urls) == 1:
        return redirect(urls[0], code=302)
    
    # Return a dynamic split-screen page if multiple URLs are found
    if len(urls) > 1:
        split_screen_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Split Screen</title>
            <style>
                body {
                    margin: 0;
                    display: flex;
                    flex-wrap: wrap;
                    height: 100vh;
                }
                iframe {
                    flex: 1 1 50%; /* Adjust this to change split ratio */
                    border: none;
                }
            </style>
        </head>
        <body>
            {% for url in urls %}
            <iframe src="{{ url }}"></iframe>
            {% endfor %}
        </body>
        </html>
        """
        return render_template_string(split_screen_template, urls=urls)
    
    # Return error if 'host' is missing or no match is found
    if host is None:
        return "Missing 'host' parameter in the request URL.", 400
    else:
        return f"No matching configuration found for host '{host}'.", 404

# Route to load the HTML interface
@app.route("/edit/")
def index():
    return render_template("index.html")

# API to get JSON data
@app.route("/edit/get_json", methods=["GET"])
def get_json():
    if not os.path.exists(CONFIG_FILE):
        return jsonify({"error": "JSON file not found"}), 404
    with open(CONFIG_FILE, "r") as file:
        data = json.load(file)
    return jsonify(data)

# API to update JSON data
@app.route("/edit/update_json", methods=["POST"])
def update_json():
    try:
        # Parse incoming JSON data
        new_data = request.json

        # Validate MEETURL
        #if not isinstance(new_data.get("MEETURL"), str) or not new_data["MEETURL"].startswith("https://liftingcast.usaplma.com/meets/"):
            #return jsonify({"error": "Invalid MEETURL format. It must end with the meet ID."}), 400
        
        # Validate MEETURL
        if not isinstance(new_data.get("MEETURL"), str):
            return jsonify({"error": "MEETURL must be a string."}), 400

        # Define a regular expression for the allowed domains and format
        meeturl_pattern = re.compile(r"^(http|https)://(backup\.liftingcast\.com|liftingcast\.com|liftingcast\.usaplma\.com|vpn\.liftingcast\.usaplma\.com|relay\.usaplma\.com)/meets/[\w-]+$")

        if not meeturl_pattern.match(new_data["MEETURL"]):
            return jsonify({
                 "error": "Invalid MEETURL format. Must use http or https and end with '/meets/{meetID}'. "
                     "Allowed domains: backup.liftingcast.com, liftingcast.com, liftingcast.usaplma.com, vpn.liftingcast.usaplma.com, relay.usaplma.com."
            }), 400

        # Validate hostnames
        for key, value in new_data.items():
            if key.startswith(("BOARD")):
                if not isinstance(value, list) or not all(isinstance(host, str) and host.isalnum() or '-' in host for host in value):
                    return jsonify({"error": f"Invalid hostname in {key}. Only letters, numbers, and dashes are allowed."}), 400

         # Validate DISPLAY1, DISPLAY2, DISPLAY3
        for key in ["DISPLAY1", "DISPLAY2", "DISPLAY3"]:
            if key in new_data:
                value = new_data[key]
                if not isinstance(value, list) or not all(isinstance(host, str) and host.isalnum() or '-' in host for host in value):
                    return jsonify({"error": f"Invalid hostname in {key}. Only letters, numbers, and dashes are allowed."}), 400

        # Save the updated JSON to file
        with open(CONFIG_FILE, "w") as file:
            json.dump(new_data, file, indent=4)

        return jsonify({"message": "JSON updated successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the server on port 5000
    app.run(host='0.0.0.0', port=5000)
