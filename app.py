from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load credentials from environment variable or file
creds_json = os.environ.get("GOOGLE_SHEETS_CREDENTIALS")
if creds_json:
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
else:
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)

client = gspread.authorize(creds)

# Open the Google Sheet
SHEET_ID = os.environ.get("SHEET_ID", "1S4o_sYw6WQddx9xEYX-UGkiDWT_V1fIsvmYIdRWlxUo")
sheet = client.open_by_key(SHEET_ID).sheet1

# Flask app
app = Flask(__name__)

@app.route("/shopify-webhook", methods=["POST"])
def shopify_webhook():
    data = request.get_json()

    order_id = data.get("id")
    properties = {}

    # Extract line item properties (assumes first line item has your form data)
    if data.get("line_items"):
        for prop in data["line_items"][0].get("properties", []):
            properties[prop.get("name")] = prop.get("value")

    # Prepare row data in same order as your Google Sheet columns
    row = [
        order_id,
        properties.get("Name ( First Middle Last ): ", ""),
        properties.get("Gender?", ""),
        properties.get("Eye Color?", ""),
        properties.get("Hair Color?", ""),
        properties.get("Birthday (Must Be 21+)", ""),
        properties.get("Height", ""),
        properties.get("Weight (lbs)", ""),
        properties.get("Street Address", ""),
        properties.get("Organ Donor?", ""),
        properties.get("Corrective Lenses?", ""),
        properties.get("Photo URL", ""),
        properties.get("Signature URL", "")
    ]

    # Append row to Google Sheet
    sheet.append_row(row)

    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)