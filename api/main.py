from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import shutil
import os
import io
import uuid
from api.services.extraction import process_and_analyze_pdf
from fastapi.responses import StreamingResponse
from fastapi import Form
import json
app = FastAPI()

app.mount("/static", StaticFiles(directory="api/static"), name="static")
templates = Jinja2Templates(directory="api/templates")

UPLOAD_DIR = "downloads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None})


@app.post("/", response_class=HTMLResponse)
async def upload_and_process_pdf(request: Request, file: UploadFile = File(...)):
    # ... (file saving code remains the same) ...
    file_ext = file.filename.split(".")[-1]
    temp_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, temp_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Traitement
    result_data = process_and_analyze_pdf(file_path) # Assuming this returns a dict/list

    # Generate JSON string for display with correct encoding and indentation
    result_display_str = None
    if result_data:
        result_display_str = json.dumps(result_data, indent=2, ensure_ascii=False)

    # Pass the original data for the download form and the formatted string for display
    return templates.TemplateResponse("index.html", {
        "request": request,
        "result": result_data, # Pass original data for the download form's tojson
        "result_display": result_display_str # Pass formatted string for display
        })

@app.post("/download-json/")
async def download_json(json_data: str = Form(...)):
    # This part remains the same, it expects a compact JSON string from the form
    buffer = io.BytesIO()
    # Ensure the data received from the form is encoded correctly for the file
    buffer.write(json_data.encode("utf-8"))
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/json; charset=utf-8", # Specify charset
        headers={"Content-Disposition": "attachment; filename=result.json"}
    )