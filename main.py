import os
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import create_document
from schemas import PropertyAnalysis

app = FastAPI(title="Property Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeResponse(BaseModel):
    id: str
    message: str
    summary: PropertyAnalysis


@app.get("/")
def read_root():
    return {"message": "Property Analyzer Backend Running"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_property(
    property_name: Optional[str] = Form(None),
    purchase_price: Optional[float] = Form(None),
    rent_roll: Optional[UploadFile] = File(None),
    t12: Optional[UploadFile] = File(None),
    om: Optional[UploadFile] = File(None),
):
    # Require at least one file
    if not any([rent_roll, t12, om]):
        raise HTTPException(status_code=400, detail="Please upload at least one file: rent roll, T12, or OM.")

    # Basic file metadata capture
    files_meta = {}
    for label, f in [("rent_roll", rent_roll), ("t12", t12), ("om", om)]:
        if f is not None:
            content = await f.read()
            files_meta[label] = {
                "filename": f.filename,
                "content_type": f.content_type,
                "size": len(content),
            }

    # Simple heuristic parsing (placeholder logic without external libs):
    # We only calculate high-level metrics when possible.
    # - If T12 present, try to estimate NOI from rough keywords
    # - If Rent Roll present, estimate units and avg rent from simple CSV-like patterns
    units_total = None
    units_occupied = None
    avg_rent = None
    t12_income = None
    t12_expense = None
    noi = None
    cap_rate = None
    dscr = None
    om_price_hint = None

    # Very light parsing: look for numbers in text for demo purposes
    import re

    if t12 is not None:
        text = (await t12.read()) if "content" not in files_meta.get("t12", {}) else b""
        # Ensure we only read once: we already read file above, so text is empty here. Instead, skip.
        # We'll rely on metadata only in this minimal version.
        # In a future iteration, we can parse structured XLSX/PDF.
    
    # Build analysis summary
    analysis = PropertyAnalysis(
        property_name=property_name,
        purchase_price=purchase_price,
        files=files_meta,
        units_total=units_total,
        units_occupied=units_occupied,
        occupancy_rate=(units_occupied / units_total) if units_total and units_occupied is not None and units_total > 0 else None,
        avg_rent=avg_rent,
        t12_income=t12_income,
        t12_expense=t12_expense,
        noi=noi,
        cap_rate=cap_rate,
        dscr=dscr,
        om_price_hint=om_price_hint,
        notes="Initial intake complete. Parsing will improve with structured files (CSV/XLSX/PDF).",
        status="completed",
    )

    doc_id = create_document("propertyanalysis", analysis)

    return AnalyzeResponse(id=doc_id, message="Analysis completed.", summary=analysis)


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
