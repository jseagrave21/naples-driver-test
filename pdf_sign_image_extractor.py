#!/usr/bin/env python3
"""
extract_signs.py
----------------
Slices all 125 road sign icons from 'Drivers Study Guide.pdf' into individual
PNG files inside ./assets/signs/ and writes ./assets/signs_manifest.json.

Uses smart color-saturation bounding-box detection on Page 1 (so tall signs like
Unguarded Railroad Crossing Multiple Track are never clipped at the top and never
include the 4-line text label at the bottom) and exact measured cell coordinates
on Page 2 (handling the shorter Row 7 and 7-column Row 8 accurately).

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
    "ROAD NARROWS ON RIGHT (TEMPORARY)", "ROAD NARROWS ON LEFT (TEMPORARY)",
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
    [
        "TOWN NAME SIGN", "MOTORWAY DIRECTION",
        "PRIMARY OR SECONDARY ROAD DIRECTION", "URBAN AREA DIRECTION",
        "DETOUR", "DIRECTION TO TOURIST ATTRACTION"
    ],
    [
        "MERGING LANES (REDUCTION)", "MERGING LANES (DEVIATION)",
        "MERGING CARRIAGEWAY", "ALL TRIANGLES INDICATE A WARNING",
        "ALL CIRCLES INDICATE SOMETHING PROHIBITED",
        "ALL BLUE CIRCLES INDICATE SOMETHING MANDATORY",
        "RED AND YELLOW TRIANGLES INDICATE A TEMPORARY WARNING"
    ]
]

P2_COLS_8 = [
    (0.012, 0.114), (0.124, 0.238), (0.248, 0.362), (0.374, 0.488),
    (0.498, 0.612), (0.623, 0.742), (0.753, 0.867), (0.876, 0.986)
]
P2_ROWS_6 = [
    (0.002, 0.060), (0.112, 0.191), (0.236, 0.315),
    (0.358, 0.439), (0.482, 0.563), (0.606, 0.686)
]
P2_ROW_7_COLS = [
    (0.008, 0.150), (0.168, 0.315), (0.332, 0.485),
    (0.500, 0.652), (0.665, 0.818), (0.830, 0.975)
]
P2_ROW_7_Y = (0.743, 0.782)
P2_ROW_8_COLS = [
    (0.015, 0.110), (0.162, 0.252), (0.308, 0.395),
    (0.432, 0.555), (0.578, 0.692), (0.718, 0.830), (0.855, 0.975)
]
P2_ROW_8_Y = (0.838, 0.918)


def slugify(text: str) -> str:
    cleaned = "".join(c if c.isalnum() else "_" for c in text.lower())
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned.strip("_")


def smart_crop_page1_cell(img: Image.Image, row: int, col: int) -> Image.Image:
    w, h = img.size
    top_header = h * 0.032
    grid_h = h - top_header
    cell_w = w / 8.0
    cell_h = grid_h / 8.0

    sx0 = max(0, int(col * cell_w + cell_w * 0.02))
    sx1 = min(w, int((col + 1) * cell_w - cell_w * 0.02))
    sy0 = max(0, int(top_header + row * cell_h - cell_h * 0.08))
    sy1 = min(h, int(top_header + (row + 0.72) * cell_h))

    sub = img.crop((sx0, sy0, sx1, sy1))
    sw, sh = sub.size
    pixels = sub.load()

    min_x, max_x = sw, 0
    min_y, max_y = sh, 0
    found = False

    for py in range(sh):
        for px in range(sw):
            r, g, b = pixels[px, py][:3]
            max_c = max(r, g, b)
            min_c = min(r, g, b)
            if (max_c - min_c) > 38 and max_c > 75:
                if px < min_x: min_x = px
                if px > max_x: max_x = px
                if py < min_y: min_y = py
                if py > max_y: max_y = py
                found = True

    if found and (max_x - min_x) > 10 and (max_y - min_y) > 10:
        pad_x = int((max_x - min_x) * 0.10)
        pad_top = int((max_y - min_y) * 0.10)
        pad_bot = int((max_y - min_y) * 0.05)
        cx0 = max(0, sx0 + min_x - pad_x)
        cy0 = max(0, sy0 + min_y - pad_top)
        cx1 = min(w, sx0 + max_x + pad_x)
        cy1 = min(h, sy0 + max_y + pad_bot)
        return img.crop((cx0, cy0, cx1, cy1))

    return img.crop((
        int(col * cell_w + cell_w * 0.05),
        int(top_header + row * cell_h),
        int((col + 1) * cell_w - cell_w * 0.05),
        int(top_header + row * cell_h + cell_h * 0.56)
    ))


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

    for row in range(8):
        for col in range(8):
            label = PAGE_1_LABELS[row * 8 + col]
            crop = smart_crop_page1_cell(img1, row, col)
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

        for row_idx, row_labels in enumerate(PAGE_2_ROWS):
            for col_idx, label in enumerate(row_labels):
                if row_idx < 6:
                    xr = P2_COLS_8[col_idx]
                    yr = P2_ROWS_6[row_idx]
                elif row_idx == 6:
                    xr = P2_ROW_7_COLS[col_idx]
                    yr = P2_ROW_7_Y
                else:
                    xr = P2_ROW_8_COLS[col_idx]
                    yr = P2_ROW_8_Y

                x0, x1 = int(xr[0] * w2), int(xr[1] * w2)
                y0, y1 = int(yr[0] * h2), int(yr[1] * h2)
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
