#!/usr/bin/env python3
"""
extract_signs.py
----------------
Slices all 125 road sign icons from 'Drivers Study Guide.pdf' into individual
PNG files inside ./assets/signs/ and writes ./assets/signs_manifest.json.

Usage:
    pip install pymupdf pillow
    python3 extract_signs.py "Drivers Study Guide.pdf"
"""

import json
import os
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
    from PIL import Image
except ImportError:
    print("Missing dependencies! Please run:")
    print("    pip install pymupdf pillow")
    sys.exit(1)


# Official 125-sign layout matching Page 1 (8x8 = 64) and Page 2 (61 signs)
PAGE_1_LABELS = [
    # Row 1
    "BUMPY ROAD", "HUMPS", "CURVE TO THE RIGHT", "CURVE TO THE LEFT",
    "DOUBLE CURVE, FIRST TO THE RIGHT THEN TO THE LEFT",
    "DOUBLE CURVE, FIRST TO THE LEFT THEN TO THE RIGHT",
    "GUARDED RAILROAD CROSSING", "UNGUARDED RAILROAD CROSSING",
    # Row 2
    "UNGUARDED RAILROAD CROSSING (SINGLE TRACK)",
    "UNGUARDED RAILROAD CROSSING (MULTIPLE TRACK)",
    "TRAMS CROSSING AHEAD", "PEDESTRIAN CROSSING", "DRAW BRIDGE",
    "DANGEROUS VERGES", "SLIPPERY ROAD", "DANGEROUS DOWNGRADE",
    # Row 3
    "DANGEROUS UPGRADE", "ROAD NARROWS", "ROAD NARROWS ON LEFT",
    "ROAD NARROWS ON RIGHT", "CAUTION SCHOOL ZONE",
    "DOMESTIC ANIMALS ON THE ROAD", "TWO-WAY TRAFFIC", "ROUNDABUT AHEAD",
    # Row 4
    "RIVER BANK", "DANGEROUS UNSTEADY MATERIALS ON THE ROAD",
    "FALLING ROCKS OR DEBRIS", "TRAFFIC LIGHTS", "SIDE WINDS",
    "RISK OF FIRE", "WILD ANIMALS", "DANGER",
    # Row 5 (Temporary Yellow Warning Triangles)
    "WORK IN PROGRESS", "ROAD NARROWS (TEMPORARY)",
    "ROAD NARROWS ON LEFT (TEMPORARY)", "ROAD NARROWS ON RIGHT (TEMPORARY)",
    "TWO-WAY TRAFFIC (TEMPORARY)",
    "DANGEROUS UNSTEADY MATERIALS ON THE ROAD (TEMPORARY)",
    "TRAFFIC LIGHTS (TEMPORARY)", "DANGER (TEMPORARY)",
    # Row 6
    "CROSSROADS WITH RIGHT-OF-WAY FROM THE RIGHT",
    "PRIORITY TO VEHICLES FROM OPPOSITE DIRECTION",
    "YIELD RIGHT OF WAY", "STOP", "ROAD WITH RIGHT OF WAY",
    "END OF ROAD WITH RIGHT OF WAY",
    "INTERSECTION WITH ROAD THAT DOES NOT HAVE RIGHT OF WAY",
    "JUNCTION WITH A MINOR SIDE-ROAD FROM RIGHT",
    # Row 7
    "JUNCTION WITH A MINOR SIDE-ROAD FROM LEFT",
    "MERGING TRAFFIC FROM RIGHT", "MERGING TRAFFIC FROM LEFT",
    "ONCOMING TRAFFIC MUST WAIT", "SPEED LIMIT IN KILOMETERS",
    "ALL VEHICLES PROHIBITED", "ENTRY PROHIBITED", "NO HORN BLOWING",
    # Row 8
    "PEDESTRIANS PROHIBITED", "BICYCLES PROHIBITED", "MOTORCYCLES PROHIBITED",
    "ALL MOTOR VEHICLES PROHIBITED", "NO PASSING",
    "LARGE GOODS VEHICLES PROHIBITED", "MINIMUM DISTANCE",
    "MAXIMUM LENGHT IN METERS"
]

PAGE_2_ROWS = [
    # Rows 1-6 (8 columns each = 48 signs)
    [
        "MAXIMUM WIDTH IN METERS", "MAXIMUM HEIGHT IN METERS",
        "MAXIMUM WEIGHT IN METRIC TONS",
        "MAXIMUM WEIGHT IN METRIC TONS PER AXLE",
        "STOP POLICE ROADBLOCK", "STOP CUSTOMS",
        "END OF SPEED LIMIT", "END OF MAXIMUM SPEED"
    ],
    [
        "END OF NO OVERTAKING", "NO PARKING", "NO STOPPING",
        "PARKING AUTHORIZED", "DRIVE STRAIGHT", "TURN RIGHT",
        "TURN LEFT", "DRIVE STRAIGHT OR TURN RIGHT"
    ],
    [
        "DRIVE STRAIGHT OR TURN LEFT", "ROUNDABOUT", "MINIMUM SPEED",
        "END OF MINIMUM SPEED", "SNOW CHAINS MANDATORY", "PEDESTRIAN LANE",
        "END OF PEDESTRIAN LANE", "CYCLE LANE"
    ],
    [
        "SCHOOL BUS", "PEDESTRIAN CROSSING (SQUARE)", "NO THROUGH ROAD",
        "TUNNEL", "AUTOSTRADA MOTORWAY", "FREEWAY",
        "ADVISORY SPEED LIMIT", "ACCIDENT AHEAD"
    ],
    [
        "HOSPITAL", "FIRST AID", "REPAIR SERVICE", "GAS STATION",
        "CAR FERRIES", "ONE WAY TRAFFIC", "INFORMATION CENTER", "CAMPING SITE"
    ],
    [
        "EU COUNTRY BORDER", "DIRECTIONS IN URBAN AREAS",
        "DIRECTIONS IN URBAN AREAS AND GREEN PANEL INDICATES MOTORWAY",
        "DIRECTIONS ON A MAIN HIGHWAY", "DIRECTIONS ON A MOTORWAY",
        "PROVINCIAL BOUNDARY SIGN", "PROVINCIAL BOUNDARY SIGN (MOTORWAY)",
        "REGIONAL BOUNDARY SIGN"
    ],
    # Row 7 (6 columns)
    [
        "TOWN NAME SIGN", "MOTORWAY DIRECTION",
        "PRIMARY OR SECONDARY ROAD DIRECTION", "URBAN AREA DIRECTION",
        "DETOUR", "DIRECTION TO TOURIST ATTRACTION"
    ],
    # Row 8 (7 columns)
    [
        "MERGING LANES (REDUCTION)", "MERGING LANES (DEVIATION)",
        "MERGING CARRIAGEWAY", "ALL TRIANGLES INDICATE A WARNING",
        "ALL CIRCLES INDICATE SOMETHING PROHIBITED",
        "ALL BLUE CIRCLES INDICATE SOMETHING MANDATORY",
        "RED AND YELLOW TRIANGLES INDICATE A TEMPORARY WARNING"
    ]
]


def slugify(text: str) -> str:
    cleaned = "".join(c if c.isalnum() else "_" for c in text.lower())
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned.strip("_")


def extract_all_signs(pdf_path: str, output_dir: str = "assets/signs"):
    if not os.path.exists(pdf_path):
        print(f"Error: Could not find '{pdf_path}'.")
        sys.exit(1)

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    manifest = []
    sign_id = 1

    # ---------------- PROCESS PAGE 1 (8x8 Grid = 64 Signs) ----------------
    page1 = doc[0]
    pix1 = page1.get_pixmap(dpi=300)
    img1 = Image.frombytes("RGB", [pix1.width, pix1.height], pix1.samples)

    w1, h1 = img1.size
    top_margin_p1 = int(h1 * 0.045)  # Skip "ITALIAN DRIVER'S LICENSE STUDY GUIDE" title
    bottom_margin_p1 = int(h1 * 0.01)
    usable_h1 = h1 - top_margin_p1 - bottom_margin_p1
    row_h1 = usable_h1 / 8.0
    col_w1 = w1 / 8.0

    for row in range(8):
        for col in range(8):
            label = PAGE_1_LABELS[row * 8 + col]
            x0 = int(col * col_w1 + col_w1 * 0.05)
            x1 = int((col + 1) * col_w1 - col_w1 * 0.05)
            y0 = int(top_margin_p1 + row * row_h1 + row_h1 * 0.02)
            # Crop top 64% of cell to isolate the sign graphic without the English caption below
            y1 = int(top_margin_p1 + row * row_h1 + row_h1 * 0.64)

            crop = img1.crop((x0, y0, x1, y1))
            filename = f"sign_{sign_id:03d}_{slugify(label)}.png"
            file_rel_path = out_path / filename
            crop.save(file_rel_path)

            manifest.append({
                "id": sign_id,
                "page": 1,
                "row": row + 1,
                "col": col + 1,
                "label": label,
                "image": str(file_rel_path).replace("\\", "/")
            })
            sign_id += 1

    # ---------------- PROCESS PAGE 2 (8 Rows = 61 Signs) ----------------
    if len(doc) > 1:
        page2 = doc[1]
        pix2 = page2.get_pixmap(dpi=300)
        img2 = Image.frombytes("RGB", [pix2.width, pix2.height], pix2.samples)

        w2, h2 = img2.size
        top_margin_p2 = int(h2 * 0.005)
        usable_h2 = h2 - top_margin_p2 - int(h2 * 0.01)
        row_h2 = usable_h2 / 8.0

        for row_idx, row_labels in enumerate(PAGE_2_ROWS):
            num_cols = len(row_labels)
            col_w2 = w2 / float(num_cols)
            for col_idx, label in enumerate(row_labels):
                x0 = int(col_idx * col_w2 + col_w2 * 0.05)
                x1 = int((col_idx + 1) * col_w2 - col_w2 * 0.05)
                y0 = int(top_margin_p2 + row_idx * row_h2 + row_h2 * 0.02)
                y1 = int(top_margin_p2 + row_idx * row_h2 + row_h2 * 0.64)

                crop = img2.crop((x0, y0, x1, y1))
                filename = f"sign_{sign_id:03d}_{slugify(label)}.png"
                file_rel_path = out_path / filename
                crop.save(file_rel_path)

                manifest.append({
                    "id": sign_id,
                    "page": 2,
                    "row": row_idx + 1,
                    "col": col_idx + 1,
                    "label": label,
                    "image": str(file_rel_path).replace("\\", "/")
                })
                sign_id += 1

    manifest_path = Path("assets/signs_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Successfully extracted {len(manifest)} road sign images to '{output_dir}/'")
    print(f"Saved JSON manifest to '{manifest_path}'")


if __name__ == "__main__":
    pdf_file = sys.argv[1] if len(sys.argv) > 1 else "Drivers Study Guide.pdf"
    extract_all_signs(pdf_file)