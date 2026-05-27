from typing import List, Optional
from psycopg2.extensions import connection
from psycopg2.extras import DictCursor
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

    # - выбрать данные из feed_action
    # - JOIN с user и post
    # - фильтрация по user_id / post_id (если заданы)
    # - сортировка по времени (DESC)
    # - ограничение по LIMIT
    query = """
    SELECT 
        u.id,
        p.id,
        fa.action,
        fa.time
        FROM public.feed_action fa
        JOIN public.user u on fa.user_id = u.id
        JOIN public.post p on fa.post_id = p.id
    WHERE fa.user_id = %s AND fa.post_id = %s 
    LIMIT %s    
    """

    result = []
    with conn.cursor(cursor_factory=DictCursor) as cur:
        # TODO: Выполнить запрос, получить строки
        # TODO: Для каждой строки:
        # TODO: Создать объект User из строки
        # TODO: Создать объект Post из строки
        # TODO: Создать объект Feed и добавить в список result
        ...
        cur.execute(query, (user_id, post_id, limit))
        rows = cur.fetchall()
        for row in rows:
            user = User(**row)
            post = Post(**row)
            feed = Feed(
                user=user,
                post=post,
                **row
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
            p.topic,
            count(fa.action)
        FROM public.post p
        JOIN public.feed_action fa ON fa.post_id = p.id
        WHERE fa.action = 'like'
        GROUP BY p.id, p.topic
        ORDER BY COUNT(fa.action) DESC  
        LIMIT %s 
        """
    result = []
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(query, (limit,))
        rows = cur.fetchall()
        for row in rows:
            post = Post(
                id = row["id"],
                topic = row["topic"]
            )
            result.append(post)
        # TODO: Преобразовать строки в список объектов Post
        return result