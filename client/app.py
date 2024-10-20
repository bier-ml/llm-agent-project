from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserInput(BaseModel):
    user_input: str

@app.get("/get-input")
def get_input():
    user_input = input("Please enter something: ")
    return {"user_input": user_input}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)