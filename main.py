from fastapi import FastAPI
from db import tables
from database import engine
from routes import items, products, user

MyApp = FastAPI()
MyApp.include_router(user.router)
MyApp.include_router(products.router)
MyApp.include_router(items.router)

@MyApp.get('/')
def home():
    return {'message': 'Hello Milma'}

tables.Base.metadata.create_all(bind=engine)