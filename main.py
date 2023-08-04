from fastapi import FastAPI, File, UploadFile

from saveeditor.saveeditor import set_pokemon_levels

app = FastAPI()


@app.post("/upload/")
def create_upload_file(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        new_sav_data = set_pokemon_levels(contents, 100)
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        file.file.close()

    return {"status": "success"}
