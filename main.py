from fastapi import FastAPI
from db import tables
from database import engine
from routes import orders, products, users

MyApp = FastAPI()
MyApp.include_router(users.router)
MyApp.include_router(products.router)
MyApp.include_router(orders.router)

@MyApp.get('/')
def home():
    return {'message': 'Hello Milma'}

tables.Base.metadata.create_all(bind=engine)