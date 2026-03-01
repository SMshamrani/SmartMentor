import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from .db import get_connection  


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

STRUCTURE_PROMPT = """
Return ONLY valid JSON in this format:

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

Do not add explanations.
"""

def structure_manual(raw_text):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": STRUCTURE_PROMPT},
            {"role": "user", "content": raw_text}
        ],
        temperature=0
    )

    return json.loads(response.choices[0].message.content)


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

    print("✅ Data inserted successfully!")


if __name__ == "__main__":
    raw_manual = """
    HP DeskJet 2720 Setup Guide:
    1. Remove packaging.
    2. Plug in the power cable.
    3. Install ink cartridges.
    4. Connect to WiFi.
    """

    structured_data = structure_manual(raw_manual)
    print(structured_data)

    insert_into_database(structured_data)
