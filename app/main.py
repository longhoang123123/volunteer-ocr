import io
import re
from typing import Any

import cv2
import easyocr
import numpy as np
import uvicorn
from PIL import Image
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pyzbar import pyzbar

main_app = FastAPI(title="Read CARD Service",
                   description="Read CARD Service",
                   version="1.0.0")

main_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@main_app.post("/read-card/")
async def read_card(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    image_np = np.array(image)
    reader = easyocr.Reader(['vi'], gpu=False)
    results = reader.readtext(image_np)
    text = "\n".join([result[1] for result in results])
    info = extract_info(text)

    null_fields = [key for key, value in info.items() if value is None]
    if null_fields:
        return JSONResponse(status_code=400,
                            content={"message": "The following fields in the card have null values: " + ', '.join(
                                null_fields)})

    return JSONResponse(status_code=200, content={"data": info})


def extract_info(text: str):
    patterns = {
        "id_number": r"(\b\d{9,12}\b)",
        "full_name": r"Full name:\s*([^\n]+)",
        "gender": r"(Nam|Nữ)",
        "dob": r"(\d{2}\/\d{2}\/\d{4})",
        "home_town": r"Place of origin:\s*([^\n]+)",
        "resident": r"Place of residence\s*([^\n]+)"
    }

    extracted_info = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            extracted_info[key] = match.group(1)
            extracted_info[key] = extracted_info[key].replace(';', ',')
        else:
            extracted_info[key] = None

    lines = text.split('\n')
    if not extracted_info.get('resident', None):
        extracted_info["resident"] = ""

    i = len(lines) - 1
    while i > 0:
        if ',' in lines[i] or ';' in lines[i]:
            extracted_info["resident"] += ", " + lines[i].replace(';', ',')
            break
        i -= 1
    return extracted_info


@main_app.post("/scan-qrcode/")
async def scan_qrcode(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    image_np = np.array(image)

    sizes = [6500, 4500, 3200]
    count = 0
    info = None
    while count < len(sizes) - 1:
        origin_img = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        origin_img = resize_image(image=origin_img, new_width=sizes[count])

        qr_detector = cv2.QRCodeDetector()
        data, bbox, _ = qr_detector.detectAndDecode(origin_img)

        if bbox is not None:
            qr_code_img = split_qr_code_area(origin_img=origin_img, bbox=bbox)
            decoded_objects = pyzbar.decode(qr_code_img)

            for obj in decoded_objects:
                data = obj.data.decode('utf-8')

            info = extract_qr_info(data=data)

        if info:
            break
        count += 1

    if not info:
        return JSONResponse(status_code=400,
                            content={"message": "Please upload a photo with QRcode"})

    return JSONResponse(status_code=200, content={"data": info})


def resize_image(image: np.ndarray, new_width: int) -> np.ndarray:
    ratio = new_width / image.shape[1]
    new_height = int(image.shape[0] * ratio)

    new_size = (new_width, new_height)
    new_image = cv2.resize(image, new_size, interpolation=cv2.INTER_LINEAR)
    return new_image


def split_qr_code_area(origin_img: np.ndarray, bbox: Any) -> np.ndarray:
    x, y, w, h = cv2.boundingRect(bbox)
    image = origin_img[y:y + h, x:x + w]

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(30, 30))
    image = clahe.apply(gray)
    return image


def extract_qr_info(data: str):
    if not data:
        return None

    data_parts = data.split('|')
    if len(data_parts) == 7:
        return {
            "cccd_id": data_parts[0],
            "cmnd_id": data_parts[1],
            "full_name": data_parts[2],
            "dob": format_date_str(data_parts[3]),
            "gender": data_parts[4],
            "residence": data_parts[5],
            "issuance": format_date_str(data_parts[6]),
        }
    else:
        return {
            "cccd_id": data_parts[0],
            "cmnd_id": None,
            "full_name": data_parts[1],
            "dob": format_date_str(data_parts[2]),
            "gender": data_parts[3],
            "residence": data_parts[4],
            "issuance": format_date_str(data_parts[5]),
        }


def format_date_str(date_str: str):
    return f"{date_str[0:2]}-{date_str[2:4]}-{date_str[4:]}"


if __name__ == "__main__":
    uvicorn.run("main:main_app", host="0.0.0.0", reload=True, port=8001)
