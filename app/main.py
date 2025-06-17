from fastapi import FastAPI
from app.api.v1 import influencer, post

app = FastAPI()

@app.get("/health")
def health():
    return {"message": "ok"}
  
@app.get("/")
def root():
    return {"message": "Hello, World!"}

app.include_router(influencer.router, prefix="/api/v1/instagram/influencer_monitor", tags=["Influencer"])
app.include_router(post.router, prefix="/api/v1/instagram/post_monitor", tags=["Post"])

if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="0.0.0.0", port=8000)
