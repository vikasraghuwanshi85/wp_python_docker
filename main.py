from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from database import WpPost, get_db

app = FastAPI(title="WP to Python API", description="A simple FastAPI application to interact with WordPress posts stored in a PostgreSQL database.", version="1.0.0")

class PostCreate(BaseModel):
    title: str
    content: str
    slug: str
    status: str = "publish"

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    slug: str
    status: str
    class Config:
        from_attributes = True

@app.get("/")
def root():
    return {"message": "WP API with Docker Postgres", "docs": "/docs"}

@app.get("/posts", response_model=List[PostResponse])
def get_posts(db: Session = Depends(get_db)):
    return db.query(WpPost).all()

@app.get("/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(WpPost).filter(WpPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.post("/posts", response_model=PostResponse)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    db_post = WpPost(**post.dict())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post