from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import redis

app = FastAPI()

# Initialize Redis client
redis_client = redis.Redis(host='redis', port=6379)

# Define User model
class User(BaseModel):
    name: str
    email: EmailStr

@app.get("/")
def read_root():
    return {"message": "Welcome to the Redis API"}

@app.post("/users/")
def create_user(user: User):
    user_key = f"user:{user.email}"
    if redis_client.exists(user_key):
        raise HTTPException(status_code=400, detail="User already exists")
    redis_client.hset(user_key, mapping={"name": user.name, "email": user.email})
    return {"message": "User created successfully"}

@app.get("/users/{email}")
def get_user(email: str):
    user_key = f"user:{email}"
    if not redis_client.exists(user_key):
        raise HTTPException(status_code=404, detail="User not found")
    user_data = redis_client.hgetall(user_key)
    user = {key.decode('utf-8'): value.decode('utf-8') for key, value in user_data.items()}
    return user

@app.put("/users/{email}")
def update_user(email: str, user: User):
    user_key = f"user:{email}"
    if not redis_client.exists(user_key):
        raise HTTPException(status_code=404, detail="User not found")
    redis_client.hset(user_key, mapping={"name": user.name, "email": user.email})
    return {"message": "User updated successfully"}

@app.delete("/users/{email}")
def delete_user(email: str):
    user_key = f"user:{email}"
    result = redis_client.delete(user_key)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

@app.get("/users/")
def get_all_users():
    keys = redis_client.keys('user:*')
    users = []
    for key in keys:
        user_data = redis_client.hgetall(key)
        user = {key.decode('utf-8'): value.decode('utf-8') for key, value in user_data.items()}
        users.append(user)
    return {"users": users}