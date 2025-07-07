import os
from fastapi import UploadFile

UPLOAD_DIR = 'static/airdrop_image'
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_airdrop_image(airdrop_id: int, image: UploadFile) -> str:
    ext = os.path.splitext(image.filename)[1]
    filename = f"airdrop_{airdrop_id}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    content = await image.read()
    with open(file_path, 'wb') as f:
        f.write(content)
    return filename