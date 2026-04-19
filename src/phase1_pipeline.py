import os
import json
import time
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

import pandas as pd
import requests
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm

from src.db import get_connection

# ==============================
# SETUP
# ==============================
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DATASET_PATH = r"C:\Users\sarah\SmartMentor-1\data\printers_dataset(Sheet).csv"
MAX_WORKERS = 6
REQUEST_TIMEOUT = 6
MAX_VLM_IMAGES = 2
ENABLE_VLM_CHECK = False  # خليها False للسرعة، True إذا تبين فحص بصري إضافي
OPENAI_MAX_RETRIES = 3
OPENAI_RETRY_DELAY = 2
SUMMARY_OUTPUT_PATH = r"C:\Users\sarah\SmartMentor-1\data\pipeline_run_summary.csv"

DB_BATCH_LOCK = threading.Lock()

# requests session for faster connection reuse
http = requests.Session()
http.headers.update({"User-Agent": "SmartMentor/1.0"})

# in-memory caches
_url_alive_cache: dict[str, bool] = {}
_guide_cache: dict[str, dict[str, Any]] = {}

# logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("phase1_pipeline")


# ==============================
# PROMPT
# ==============================
HYBRID_PROMPT = """
You are a professional printer technical documentation generator.

Using the provided printer model name, generate a realistic and professional first-time setup guide.

Requirements:
- Return ONLY valid JSON
- No markdown
- No explanations outside JSON
- Professional engineering tone
- Minimum 10 setup steps
- Steps must be practical, ordered, and specific to printer installation and first-time setup
- Include realistic printer components
- Include power/setup/network/paper/ink-or-toner/testing steps where applicable
- Device type must always be "Printer"
- Component descriptions must be concise and realistic
- Avoid repeating the same step wording

JSON schema:
{
  "device_name": "printer model name",
  "device_type": "Printer",
  "guide": {
    "title": "professional guide title",
    "steps": [
      {
        "step_number": 1,
        "description": "clear technical step"
      }
    ]
  },
  "components": [
    {
      "name": "component name",
      "description": "short realistic technical description"
    }
  ]
}
"""


# ==============================
# NAME HELPERS
# ==============================
def canonical_name(name: str) -> str:
    if not name:
        return ""
    return " ".join(str(name).strip().split()).upper()


def normalize_text(text: str) -> str:
    if not text:
        return ""
    return " ".join(
        str(text)
        .strip()
        .lower()
        .replace("_", " ")
        .replace("-", " ")
        .replace(".", " ")
        .split()
    )


# ==============================
# RETRY HELPERS
# ==============================
def retry_openai_call(func, *args, **kwargs):
    last_error = None

    for attempt in range(1, OPENAI_MAX_RETRIES + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_error = e
            logger.warning(
                "OpenAI call failed on attempt %s/%s: %s",
                attempt,
                OPENAI_MAX_RETRIES,
                e,
            )
            if attempt < OPENAI_MAX_RETRIES:
                time.sleep(OPENAI_RETRY_DELAY * attempt)

    raise last_error


# ==============================
# IMAGE HELPERS
# ==============================
def is_supported_image_url(url: str) -> bool:
    lowered = url.lower()
    supported_exts = (".jpg", ".jpeg", ".png", ".webp", ".gif")
    blocked_exts = (".avif", ".svg", ".bmp", ".tiff", ".ico")

    if any(ext in lowered for ext in blocked_exts):
        return False
    if any(ext in lowered for ext in supported_exts):
        return True
    return True


def is_url_alive(url: str) -> bool:
    if url in _url_alive_cache:
        return _url_alive_cache[url]

    if not is_supported_image_url(url):
        _url_alive_cache[url] = False
        return False

    try:
        response = http.head(url, allow_redirects=True, timeout=REQUEST_TIMEOUT)
        content_type = response.headers.get("Content-Type", "").lower()
        alive = response.status_code == 200 and "image" in content_type

        if not alive:
            response = http.get(url, stream=True, allow_redirects=True, timeout=REQUEST_TIMEOUT)
            content_type = response.headers.get("Content-Type", "").lower()
            alive = response.status_code == 200 and "image" in content_type

        _url_alive_cache[url] = alive
        return alive
    except Exception:
        _url_alive_cache[url] = False
        return False


def deduplicate_and_renumber_images(images: list[dict]) -> list[dict]:
    unique_by_url = []
    seen_urls = set()

    for img in images:
        url = img["url"].strip()
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        unique_by_url.append({"url": url, "num": img["num"]})

    return [{"url": img["url"], "num": i} for i, img in enumerate(unique_by_url, start=1)]


# ==============================
# VLM FUNCTION
# ==============================
def detect_printer(image_url: str) -> str:
    try:
        response = retry_openai_call(
            client.responses.create,
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Identify the printer model from the image. Return ONLY the printer model name. If unclear, return UNKNOWN.",
                        },
                        {
                            "type": "input_image",
                            "image_url": image_url,
                        },
                    ],
                }
            ],
        )
        return response.output_text.strip()
    except Exception as e:
        logger.warning("VLM error for %s: %s", image_url, e)
        return "UNKNOWN"


# ==============================
# GUIDE HELPERS
# ==============================
def ensure_minimum_steps(data: dict, printer_name: str) -> dict:
    data.setdefault("guide", {})
    steps = data["guide"].get("steps", []) or []

    cleaned_steps = []
    for step in steps:
        description = str(step.get("description", "")).strip()
        if description:
            cleaned_steps.append({
                "step_number": len(cleaned_steps) + 1,
                "description": description,
            })

    fallback_steps = [
        f"Unpack the {printer_name} and verify that all supplied accessories are present.",
        "Remove all transport tapes, foam inserts, and protective packaging materials.",
        "Place the printer on a stable, ventilated surface close to a power outlet.",
        "Connect the power cable securely and switch the printer on.",
        "Install the ink cartridges or toner cartridges according to the marked slots.",
        "Load a clean stack of compatible paper into the input tray and adjust the guides.",
        "Use the control panel to set the language, region, and basic device preferences.",
        "Connect the printer to the computer or network using USB, Wi-Fi, or Ethernet as applicable.",
        "Install the correct printer driver and utility software on the target computer.",
        "Print a test page to confirm proper print quality and successful communication.",
    ]

    while len(cleaned_steps) < 10:
        cleaned_steps.append({
            "step_number": len(cleaned_steps) + 1,
            "description": fallback_steps[len(cleaned_steps)],
        })

    data["guide"]["steps"] = cleaned_steps
    return data


def ensure_components(data: dict) -> dict:
    components = data.get("components", []) or []
    cleaned = []
    seen = set()

    for comp in components:
        name = str(comp.get("name", "")).strip()
        desc = str(comp.get("description", "")).strip()
        if not name:
            continue
        key = normalize_text(name)
        if key in seen:
            continue
        seen.add(key)
        cleaned.append({
            "name": name,
            "description": desc or "Essential component of the printer used during normal operation.",
        })

    if not cleaned:
        cleaned = [
            {"name": "Power Cable", "description": "Supplies electrical power to the printer."},
            {"name": "Input Tray", "description": "Holds paper before printing begins."},
            {"name": "Output Tray", "description": "Collects printed pages after printing."},
            {"name": "Control Panel", "description": "Allows the user to configure and operate the device."},
            {"name": "Ink or Toner Cartridge", "description": "Provides the printing material required to produce output."},
        ]

    data["components"] = cleaned
    return data


# ==============================
# LLM FUNCTION
# ==============================
def generate_guide(name: str) -> dict:
    fixed_name = canonical_name(name)
    if fixed_name in _guide_cache:
        return json.loads(json.dumps(_guide_cache[fixed_name]))

    response = retry_openai_call(
        client.chat.completions.create,
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": HYBRID_PROMPT},
            {"role": "user", "content": f"Generate a setup guide for this printer model: {fixed_name}"},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content

    try:
        data = json.loads(content)
    except Exception:
        start = content.find("{")
        end = content.rfind("}") + 1
        data = json.loads(content[start:end])

    data["device_name"] = fixed_name
    data["device_type"] = "Printer"
    data.setdefault("guide", {})
    data["guide"]["title"] = data["guide"].get("title") or f"Setup Guide for {fixed_name}"
    data = ensure_minimum_steps(data, fixed_name)
    data = ensure_components(data)

    _guide_cache[fixed_name] = json.loads(json.dumps(data))
    return data


# ==============================
# DB HELPERS
# ==============================
def get_existing_source_ids() -> set[int]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT SourceID FROM Devices WHERE SourceID IS NOT NULL")
        return {int(row[0]) for row in cur.fetchall()}
    finally:
        cur.close()
        conn.close()


def insert_all(source_id: int, data: dict, images: list[dict]) -> str:
    with DB_BATCH_LOCK:
        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                """
                INSERT INTO Devices (SourceID, DeviceName, DeviceType)
                VALUES (%s, %s, %s)
                RETURNING DeviceID
                """,
                (source_id, data["device_name"], data["device_type"]),
            )
            device_id = cur.fetchone()[0]

            if images:
                image_rows = [(device_id, img["url"], img["num"]) for img in images]
                cur.executemany(
                    """
                    INSERT INTO DeviceImages (DeviceID, ImageURL, ImageNumber)
                    VALUES (%s, %s, %s)
                    """,
                    image_rows,
                )

            cur.execute(
                """
                INSERT INTO Guides (DeviceID, Title, DateCreated)
                VALUES (%s, %s, CURRENT_DATE)
                RETURNING GuideID
                """,
                (device_id, data["guide"]["title"]),
            )
            guide_id = cur.fetchone()[0]

            step_rows = []
            for idx, step in enumerate(data["guide"]["steps"], start=1):
                step_number = int(step.get("step_number", idx))
                description = str(step.get("description", "")).strip()
                step_rows.append((guide_id, step_number, description))

            if step_rows:
                cur.executemany(
                    """
                    INSERT INTO Steps (GuideID, StepNumber, Description)
                    VALUES (%s, %s, %s)
                    """,
                    step_rows,
                )

            component_rows = []
            for comp in data["components"]:
                comp_name = str(comp.get("name", "Unknown Component")).strip() or "Unknown Component"
                comp_desc = str(comp.get("description", "")).strip()
                component_rows.append((device_id, comp_name, comp_desc))

            if component_rows:
                cur.executemany(
                    """
                    INSERT INTO Components (DeviceID, ComponentName, Description)
                    VALUES (%s, %s, %s)
                    """,
                    component_rows,
                )

            conn.commit()
            return f"Inserted ID={source_id} | {data['device_name']} ({len(images)} images, {len(step_rows)} steps)"

        except Exception as e:
            conn.rollback()
            return f"DB Error for ID={source_id} | {data.get('device_name', 'UNKNOWN')}: {e}"
        finally:
            cur.close()
            conn.close()


# ==============================
# PROCESS ONE PRINTER
# ==============================
def process_printer(source_id: int, group: pd.DataFrame) -> dict:
    source_id = int(source_id)
    first_row = group.iloc[0]
    printer_name = canonical_name(first_row["Printer Name"])

    logger.info("Processing ID=%s | %s", source_id, printer_name)

    images = []
    for _, row in group.iterrows():
        url = row.get("Image URL")
        num = row.get("Image #")

        if pd.isna(url) or pd.isna(num):
            continue

        try:
            img_num = int(float(num))
        except Exception:
            continue

        images.append({"url": str(url).strip(), "num": img_num})

    images = deduplicate_and_renumber_images(images)
    original_image_count = len(images)

    if images:
        valid_images = [img for img in images if is_url_alive(img["url"])]
        valid_images = deduplicate_and_renumber_images(valid_images)
    else:
        valid_images = []

    detected = "SKIPPED"
    vlm_used = False

    if ENABLE_VLM_CHECK and valid_images:
        vlm_used = True
        detected = "UNKNOWN"
        for img in valid_images[:MAX_VLM_IMAGES]:
            detected = detect_printer(img["url"])
            logger.info("VLM | ID=%s | %s -> %s", source_id, printer_name, detected)
            if normalize_text(detected) != "unknown":
                break

        if normalize_text(detected) == "unknown":
            logger.warning("VLM failed for ID=%s | %s", source_id, printer_name)
        elif normalize_text(printer_name) not in normalize_text(detected) and normalize_text(detected) not in normalize_text(printer_name):
            logger.warning(
                "VLM mismatch for ID=%s | %s | detected=%s",
                source_id,
                printer_name,
                detected,
            )

    data = generate_guide(printer_name)
    db_message = insert_all(source_id, data, valid_images)

    status = "success" if db_message.startswith("Inserted") else "error"

    return {
        "source_id": source_id,
        "printer_name": printer_name,
        "status": status,
        "db_message": db_message,
        "original_images": original_image_count,
        "valid_images": len(valid_images),
        "steps_count": len(data["guide"]["steps"]),
        "components_count": len(data["components"]),
        "vlm_used": vlm_used,
        "vlm_detected": detected,
    }


# ==============================
# SUMMARY EXPORT
# ==============================
def export_summary_csv(results: list[dict]) -> None:
    df_summary = pd.DataFrame(results)
    df_summary = df_summary.sort_values(by=["source_id"])
    df_summary.to_csv(SUMMARY_OUTPUT_PATH, index=False, encoding="utf-8-sig")
    logger.info("Summary CSV exported to: %s", SUMMARY_OUTPUT_PATH)


# ==============================
# MAIN
# ==============================
def main():
    start_time = time.time()

    df = pd.read_csv(DATASET_PATH)
    df.columns = [str(col).strip() for col in df.columns]

    logger.info("CSV columns: %s", list(df.columns))

    id_col = "Printer ID"
    required_columns = [id_col, "Printer Name", "Image URL", "Image #"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns in CSV: {missing_columns}")

    df = df.drop_duplicates(subset=[id_col, "Printer Name", "Image URL", "Image #"])
    df = df[df[id_col].notna()].copy()
    df[id_col] = df[id_col].astype(int)
    df["Printer Name"] = df["Printer Name"].astype(str).apply(canonical_name)

    grouped = list(df.groupby(id_col))
    logger.info("Total printers found by %s: %s", id_col, len(grouped))

    existing_ids = get_existing_source_ids()
    pending = [(int(source_id), group) for source_id, group in grouped if int(source_id) not in existing_ids]
    logger.info("Pending printers to process: %s", len(pending))

    if not pending:
        logger.info("No pending printers. Exporting empty/current summary.")
        export_summary_csv([])
        print("DONE")
        return

    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_printer, source_id, group) for source_id, group in pending]

        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing printers"):
            try:
                result = future.result()
                results.append(result)
                if result["status"] == "success":
                    logger.info(result["db_message"])
                else:
                    logger.error(result["db_message"])
            except Exception as e:
                logger.exception("Unexpected worker error: %s", e)
                results.append({
                    "source_id": -1,
                    "printer_name": "UNKNOWN",
                    "status": "error",
                    "db_message": f"Unexpected worker error: {e}",
                    "original_images": 0,
                    "valid_images": 0,
                    "steps_count": 0,
                    "components_count": 0,
                    "vlm_used": False,
                    "vlm_detected": "N/A",
                })

    export_summary_csv(results)

    success_count = sum(1 for r in results if r["status"] == "success")
    error_count = sum(1 for r in results if r["status"] == "error")
    total_valid_images = sum(int(r["valid_images"]) for r in results)
    total_steps = sum(int(r["steps_count"]) for r in results)

    elapsed = round(time.time() - start_time, 2)

    logger.info("Run finished in %s seconds", elapsed)
    logger.info("Success: %s | Errors: %s", success_count, error_count)
    logger.info("Total valid images inserted: %s", total_valid_images)
    logger.info("Total steps inserted: %s", total_steps)

    print("DONE")


if __name__ == "__main__":
    main()