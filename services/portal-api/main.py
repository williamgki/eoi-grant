import os

import sqlalchemy as sa
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///portal.db")
engine = sa.create_engine(DATABASE_URL)
metadata = sa.MetaData()

Drafts = sa.Table(
    "drafts",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("draft", sa.Text, nullable=False),
    sa.Column("copy", sa.Text),
)
metadata.create_all(engine)


class DraftCreate(BaseModel):
    draft: str
    copy: str | None = None


class Draft(DraftCreate):
    id: int


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/drafts", response_model=Draft)
async def create_draft(payload: DraftCreate) -> Draft:
    """Create a new draft entry."""
    with engine.begin() as conn:
        result = conn.execute(
            Drafts.insert().values(draft=payload.draft, copy=payload.copy)
        )
        pk = result.inserted_primary_key[0]
        row = conn.execute(sa.select(Drafts).where(Drafts.c.id == pk)).mappings().first()
    return Draft(**row)


@app.get("/drafts/{draft_id}", response_model=Draft)
async def read_draft(draft_id: int) -> Draft:
    """Return a stored draft."""
    with engine.connect() as conn:
        row = conn.execute(sa.select(Drafts).where(Drafts.c.id == draft_id)).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Draft not found")
    return Draft(**row)


@app.put("/drafts/{draft_id}", response_model=Draft)
async def update_draft(draft_id: int, payload: DraftCreate) -> Draft:
    """Update an existing draft."""
    with engine.begin() as conn:
        result = conn.execute(
            Drafts.update()
            .where(Drafts.c.id == draft_id)
            .values(draft=payload.draft, copy=payload.copy)
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Draft not found")
        row = conn.execute(sa.select(Drafts).where(Drafts.c.id == draft_id)).mappings().first()
    return Draft(**row)


@app.delete("/drafts/{draft_id}")
async def delete_draft(draft_id: int) -> dict[str, bool]:
    """Delete a draft."""
    with engine.begin() as conn:
        result = conn.execute(Drafts.delete().where(Drafts.c.id == draft_id))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Draft not found")
    return {"ok": True}


if __name__ == "__main__":  # pragma: no cover - manual execution
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
