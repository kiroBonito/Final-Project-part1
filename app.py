from typing import List
from fastapi import FastAPI, HTTPException, Depends
from database import postgres_connection
from schema import UserGet, PostGet, FeedGet
from helpers import get_user, get_post, get_feed, get_recommended_feed

# Инициализация FastAPI-приложения — точка входа для всех маршрутов
app = FastAPI()


# Функция для создания и закрытия подключения к базе данных.
# Используется в Depends — FastAPI сам управляет подключением и закрытием.
def get_conn():
    """
    Создаёт и возвращает подключение к PostgreSQL через psycopg2.
    """
    conn = postgres_connection()
    try:
        yield conn  # отдаём соединение в обработчик запроса
    finally:
        conn.close()  # обязательно закрываем соединение после завершения

app = FastAPI()

@app.get("/user/{id}", response_model=UserGet)
def handle_get_user(id: int, conn = Depends(get_conn)) -> UserGet:

    user = get_user(conn, id)
    if user is None:
        raise HTTPException(404)
    return user

@app.get("/post/{id}", response_model=PostGet)
def handle_get_post(id: int, conn = Depends(get_conn)) -> PostGet:

    post = get_post(conn, id)
    if post is None:
        raise HTTPException(404)
    return post

@app.get("/user/{id}/feed", response_model=List[FeedGet])
def handle_get_user_feed(id: int, limit: int = 10, conn = Depends(get_conn)) -> List[FeedGet]:
    return get_feed(conn, user_id = id, post_id= None, limit = limit )

@app.get("/post/{id}/feed", response_model=List[FeedGet])
def handle_get_posts_feed(id: int, limit: int = 10, conn = Depends(get_conn)) -> List[FeedGet]:
    return get_feed(conn, user_id = None, post_id = id, limit = limit )

@app.get("/post/recommendations/", response_model=List[PostGet])
def recommended_posts(id: int, limit: int, conn=Depends(get_conn)) -> List[PostGet]:
    return get_recommended_feed(conn, id = id, limit = limit)
