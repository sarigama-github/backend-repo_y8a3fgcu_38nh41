import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Wallpaper

app = FastAPI(title="Anime Wallpapers API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helpers
class ObjectIdStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        try:
            ObjectId(str(v))
            return str(v)
        except Exception:
            raise ValueError("Invalid ObjectId")

class WallpaperCreate(Wallpaper):
    pass

class WallpaperOut(Wallpaper):
    id: str

@app.get("/", tags=["health"])
def read_root():
    return {"message": "Anime Wallpapers API running"}

@app.get("/test", tags=["health"])
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# Create wallpaper
@app.post("/api/wallpapers", response_model=dict, tags=["wallpapers"])
def create_wallpaper(payload: WallpaperCreate):
    try:
        inserted_id = create_document("wallpaper", payload)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# List/search wallpapers
@app.get("/api/wallpapers", tags=["wallpapers"])
def list_wallpapers(
    q: Optional[str] = Query(None, description="Search by title, anime, or tags"),
    anime: Optional[str] = None,
    premium: Optional[bool] = Query(None, alias="is_premium"),
    limit: int = Query(24, ge=1, le=100),
):
    try:
        filter_query = {}
        if q:
            filter_query["$or"] = [
                {"title": {"$regex": q, "$options": "i"}},
                {"anime": {"$regex": q, "$options": "i"}},
                {"tags": {"$elemMatch": {"$regex": q, "$options": "i"}}},
            ]
        if anime:
            filter_query["anime"] = {"$regex": anime, "$options": "i"}
        if premium is not None:
            filter_query["is_premium"] = premium

        docs = get_documents("wallpaper", filter_query, limit)
        # transform _id to id
        for d in docs:
            d["id"] = str(d.pop("_id"))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Increment download count and return URL selected
class DownloadRequest(BaseModel):
    device: str  # "mobile" or "desktop"

@app.post("/api/wallpapers/{wallpaper_id}/download", tags=["wallpapers"])
def download_wallpaper(wallpaper_id: str, body: DownloadRequest):
    try:
        oid = ObjectId(wallpaper_id)
        doc = db.wallpaper.find_one({"_id": oid})
        if not doc:
            raise HTTPException(status_code=404, detail="Wallpaper not found")
        # increment downloads
        db.wallpaper.update_one({"_id": oid}, {"$inc": {"downloads": 1}})
        # select url
        image_urls = doc.get("image_urls", {})
        url = None
        if body.device == "mobile":
            url = image_urls.get("mobile")
        else:
            url = image_urls.get("desktop") or image_urls.get("mobile")
        if not url:
            raise HTTPException(status_code=400, detail="Download URL not available")
        return {"url": url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Expose schemas for viewer tools
@app.get("/schema", tags=["schemas"])
def get_schema():
    from schemas import User, Product, Wallpaper
    return {
        "user": User.model_json_schema(),
        "product": Product.model_json_schema(),
        "wallpaper": Wallpaper.model_json_schema(),
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
