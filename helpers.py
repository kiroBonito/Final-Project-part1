from typing import List, Optional
from psycopg2.extensions import connection
from psycopg2.extras import DictCursor
import pydantic
from database import postgres_connection
from models import User, Post, Feed

def get_user(conn: connection, user_id: int) -> Optional[User]:
    """
    Загружает одного пользователя из базы данных по его Id.

    Возвращает объект User, если пользователь найден.
    Если пользователь с таким id отсутствует — возвращает None.
    """

    query = "SELECT * FROM public.user WHERE id = %s"

    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(query, (user_id,))
        row = cur.fetchone()

        if row is None:
            return None
        return User(**row)
def get_post(conn: connection, post_id: int) -> Optional[Post]:
    """
    Загружает один пост из базы данных по его Id.

    Возвращает объект Post, если пост найден.
    Если пост с таким id отсутствует — возвращает None.
    """
    query = "SELECT * FROM public.post WHERE id = %s"

    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(query, (post_id,))
        row = cur.fetchone()

        if row is None:
            return None

        return Post(**row)

def get_feed(
    conn: connection, user_id: int = None, post_id: int = None, limit: int = 10
) -> List[Feed]:
    """
    Получает список действий пользователей с постами, включая данные о пользователях и постах.

    - Необходимо указать хотя бы один фильтр: user_id или post_id.
    - Возвращает не более `limit` записей.
    - Действия сортируются по времени: от самых свежих к более старым.
    - Используется для получения последних активностей пользователя или взаимодействий с постом.
    """
    if user_id is None and post_id is None:
        raise ValueError("Необходимо указать хотя бы user_id или post_id")

    query = """
    SELECT
            fa.user_id,
            fa.post_id,
            fa.action,
            fa.time,
            u.id,
            u.gender,
            u.age,
            u.country,
            u.city,
            u.exp_group,
            u.os,
            u.source,
            p.id,
            p.text,
            p.topic

        FROM public.feed_action fa
        JOIN public.user u
            ON fa.user_id = u.id
        JOIN public.post p
            ON fa.post_id = p.id
        WHERE (%s IS NULL OR fa.user_id = %s) AND (%s IS NULL OR fa.post_id = %s)
        ORDER BY fa.time DESC
        LIMIT %s   
    """

    result = []
    with conn.cursor(cursor_factory=DictCursor) as cur:

        cur.execute(query, (user_id,user_id, post_id, post_id, limit))
        rows = cur.fetchall()
        for row in rows:
            user = User(
                id = row["user_id"],
                gender = row["gender"],
                age = row["age"],
                country = row["country"],
                city = row["city"],
                exp_group = row["exp_group"],
                os = row["os"],
                source = row["source"],
            )
            post = Post(
                id = row["post_id"],
                text = row["text"],
                topic = row["topic"],
            )
            feed = Feed(
                user_id=row["user_id"],
                post_id=row["post_id"],
                user=user,
                post=post,
                action=row["action"],
                time=row["time"],
            )
            result.append(feed)
        return result

def get_recommended_feed(conn: connection, id: int, limit: int) -> List[Post]:
    """
    Возвращает список top-N постов с наибольшим числом лайков.

    Это базовая реализация рекомендательной системы (baseline),
    которая не учитывает индивидуальные предпочтения, а показывает
    одинаковые популярные посты всем пользователям.

    Параметры:
        conn (connection): подключение к базе данных.
        id (int): ID пользователя (в этой версии не используется,
                  но оставлен для совместимости с будущей логикой).
        limit (int): количество постов в выдаче.

    Возвращает:
        List[Post]: список объектов Post, отсортированных по убыванию популярности.
    """
    query = """
        SELECT 
            p.id,
            p.text,
            p.topic,
            count(fa.action)
        FROM public.post p
        JOIN public.feed_action fa ON fa.post_id = p.id
        WHERE fa.action = 'like'
        GROUP BY p.id, p.text, p.topic
        ORDER BY COUNT(fa.action) DESC  
        LIMIT %s 
        """
    result = []
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(query, (limit,))
        rows = cur.fetchall()
        for row in rows:
            result.append(Post(id=row["id"], text=row["text"], topic=row["topic"]))
    return result