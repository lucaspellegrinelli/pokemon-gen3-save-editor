import os
import uuid

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse, HTMLResponse

from saveeditor.saveeditor import set_pokemon_levels

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>Save Editor</title>
        </head>
        <body>
            <h1>Save Editor</h1>
            <form action="/upload/" enctype="multipart/form-data" method="post">
                <input name="file" type="file">
                <select name="game">
                    <option value="frlg">FireRed/LeafGreen</option>
                    <option value="rse">Ruby/Sapphire/Emerald</option>
                </select>
                <input type="submit">
            </form>
        </body>
    </html>
    """


@app.post("/upload/")
def create_upload_file(file: UploadFile = File(...), game: str = Form(...)):
    try:
        save_name = str(uuid.uuid4())
        filename = file.filename
        contents = file.file.read()
        is_frlg = game == "frlg"
        new_sav_data = set_pokemon_levels(contents, is_frlg, 100)
        os.makedirs("save_files", exist_ok=True)
        with open(f"save_files/{save_name}.sav", "wb") as f:
            f.write(new_sav_data)
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        file.file.close()

    return FileResponse(f"save_files/{save_name}.sav", filename=filename)
