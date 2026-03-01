import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from .db import get_connection

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==============================
# Knowledge Base (Fixed Dataset)
# ==============================

PRINTER_KNOWLEDGE_BASE = {
    "Canon Pixma G3411": """
    Ink tank printer with WiFi capability.
    Requires manual ink filling.
    Supports wireless printing.
    CMYK refillable tanks.
    """,

    "Epson EcoTank L3250": """
    EcoTank ink bottle system.
    Requires ink charging process.
    Supports Epson Smart Panel app.
    Wireless configuration supported.
    """,

    "HP DeskJet 2720": """
    Cartridge-based inkjet printer.
    Uses HP Smart App for setup.
    Wireless configuration required.
    Supports alignment process.
    """,

    "HP LaserJet Pro M404dn": """
    Laser printer using toner cartridge.
    Supports wired Ethernet connection.
    Business-class printer.
    Web interface configuration available.
    """
}

# ==============================
# Hybrid Professional Prompt
# ==============================

HYBRID_PROMPT = """
You are a professional printer technical documentation generator.

Using the provided technical description, generate:

- Accurate setup guide
- Realistic components list
- Detailed ordered steps
- Minimum 10 steps
- Professional engineering tone

Return ONLY valid JSON:

{
  "device_name": "",
  "device_type": "Printer",
  "components": [
    {"name": "", "description": ""}
  ],
  "guide": {
    "title": "",
    "steps": [
      {"step_number": 1, "description": ""}
    ]
  }
}
"""

# ==============================
# AI Generator
# ==============================

def generate_professional_guide(printer_name):
    raw_data = PRINTER_KNOWLEDGE_BASE[printer_name]

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": HYBRID_PROMPT},
            {
                "role": "user",
                "content": f"""
                Printer Model: {printer_name}
                Technical Information:
                {raw_data}
                """
            }
        ],
        temperature=0.3
    )

    content = response.choices[0].message.content

    print("\n========= RAW AI RESPONSE =========")
    print(content)
    print("===================================\n")

    if not content:
        raise Exception("❌ AI returned empty response.")

    content = content.strip()

    try:
        return json.loads(content)

    except json.JSONDecodeError:
        print("⚠ Attempting JSON cleanup...")

        start = content.find("{")
        end = content.rfind("}") + 1

        if start != -1 and end != -1:
            cleaned = content[start:end]
            return json.loads(cleaned)

        raise Exception("❌ Could not parse AI response as JSON.")
# ==============================
# Database Helpers
# ==============================

def device_exists(device_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT DeviceID FROM Devices WHERE DeviceName = %s",
        (device_name,)
    )

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result is not None


def insert_into_database(data):
    conn = get_connection()
    cursor = conn.cursor()

    # Insert Device
    cursor.execute("""
        INSERT INTO Devices (DeviceName, DeviceType)
        VALUES (%s, %s)
        RETURNING DeviceID
    """, (data["device_name"], data["device_type"]))

    device_id = cursor.fetchone()[0]

    # Insert Guide
    cursor.execute("""
        INSERT INTO Guides (DeviceID, Title, DateCreated)
        VALUES (%s, %s, CURRENT_DATE)
        RETURNING GuideID
    """, (device_id, data["guide"]["title"]))

    guide_id = cursor.fetchone()[0]

    # Insert Steps
    for step in data["guide"]["steps"]:
        cursor.execute("""
            INSERT INTO Steps (GuideID, StepNumber, Description)
            VALUES (%s, %s, %s)
        """, (guide_id, step["step_number"], step["description"]))

    # Insert Components
    for comp in data["components"]:
        cursor.execute("""
            INSERT INTO Components (DeviceID, ComponentName, Description)
            VALUES (%s, %s, %s)
        """, (device_id, comp["name"], comp["description"]))

    conn.commit()
    cursor.close()
    conn.close()

    print(f"✅ Inserted: {data['device_name']}")

# ==============================
# Initial Seed Runner
# ==============================

def run_initial_seed():
    printers = [
        "Canon Pixma G3411",
        "Epson EcoTank L3250",
        "HP DeskJet 2720",
        "HP LaserJet Pro M404dn"
    ]

    for printer in printers:

        if device_exists(printer):
            print(f"⏭ {printer} already exists. Skipping...")
            continue

        print(f"🚀 Generating guide for {printer}...")

        structured_data = generate_professional_guide(printer)
        insert_into_database(structured_data)

    print("✅ Initial Seed Completed Safely.")


# ==============================
# Main Entry Point
# ==============================

if __name__ == "__main__":
    run_initial_seed()