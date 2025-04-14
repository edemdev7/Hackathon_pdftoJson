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
    # Sauvegarde temporaire du fichier
    file_ext = file.filename.split(".")[-1]
    temp_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, temp_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Traitement
    result = process_and_analyze_pdf(file_path)

    return templates.TemplateResponse("index.html", {"request": request, "result": result})

@app.post("/download-json/")
async def download_json(json_data: str = Form(...)):
    buffer = io.BytesIO()
    buffer.write(json_data.encode("utf-8"))
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=result.json"}
    )