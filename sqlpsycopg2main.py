from typing import Optional
from fastapi import Body, FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World"}


while True:
    try:
        conn = psycopg2.connect(
            host='localhost', database='test', user='jitu', password='jitu', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("DB  connection is done successfully")
        break
    except Exception as e:
        print(f"Unable to connect to Database Error: f{e}")
        time.sleep(2)

# def read_json_file(file_name):
#     with open(file=file_name, mode="r+") as file:
#         print(file.read())


# read_json_file("my_post.json")


# my_posts = [{"title": "Python", "content": "Python is an OOP language", "id": 1}, {
#     "title": "Java", "content": "Java is also an OOP language", "id": 2}]


@app.get("/posts")
def get_posts():
    cursor.execute("""select * from posts""")
    my_posts = cursor.fetchall()
    print(my_posts)
    return {"data": my_posts}


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


@app.post("/createposts", status_code=201)
def create_post(post: Post):
    # print(post.title)
    # print(post.content)
    # print(post.published)
    # print(post.rating)
    # post_dict = post.model_dump()
    # post_dict['id'] = randrange(0, 100000000000)
    # my_posts.append(post_dict)
    cursor.execute(
        """ INSERT INTO posts(title,content,published) VALUES(%s,%s,%s) RETURNING * """, (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}


# def find_post(id):
#     cursor.execute(""" SELECT * FROM posts where id={0} """, {id})
#     return cursor.fetchall()


@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    cursor.execute(
        """SELECT * FROM posts where id = %s """, (str(id),))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} is not found")
    return {"post": post}
    # if not post:
    #     response.status_code = status.HTTP_404_NOT_FOUND
    #     return {"message": f"Post with id {id} is not found"}
    # return {"post": post}


# def find_post_index(id):
#     for i, p in enumerate(my_posts):
#         if p["id"] == id:
#             return i


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):

    cursor.execute(
        """DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    deleted_post = cursor.fetchone()
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} is not found")
    conn.commit()

    # cursor.execute(f" select id FROM posts where id = {id} ")
    # id = cursor.fetchone()
    # if id == None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                         detail=f"Post with id: {id} is not found")
    # index = find_post_index(id)
    # if index == None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                         detail=f"Post with id: {id} is not found")
    # else:
    # my_posts.pop(index)


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute(""" UPDATE posts SET title= %s, content= %s, published= %s WHERE id=%s RETURNING * """,
                   (post.title, post.content, post.published, (str(id),)))
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} is not found")
    return {"data": updated_post}

# index = find_post_index(id)
# if index == None:
#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                         detail=f"Post with id: {id} is not found")
# post_dict = post.model_dump()
# post_dict["id"] = id
# my_posts[index] = post_dict
# return {"data": post_dict}
