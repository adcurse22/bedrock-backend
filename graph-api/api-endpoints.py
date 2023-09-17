import databases
import fastapi
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = fastapi.FastAPI()

DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test"

database = databases.Database(DATABASE_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GraphEdge(BaseModel):
    prev_a: int
    curr_a: int


class GraphNode(BaseModel):
    text: str
    id: int


class NoteBody(BaseModel):
    text: str
    tags: list[str]
    links: list[int]


class Graph(BaseModel):
    edges: list[GraphEdge]
    nodes: list[GraphNode]


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
async def graph_nodes():
    return [
    ]


@app.get("/{node_id}")
async def specific_nodes(node_id: int) -> Graph:
    query = """
        WITH RECURSIVE friend_of_friend AS (SELECT previous_article as prev_a, edges.next_article as curr_a
                                            FROM edges
                                            WHERE edges.previous_article = :node_id
                                            UNION
                                            SELECT edges.previous_article, edges.next_article
                                            FROM edges
                                                     JOIN friend_of_friend
                                                          ON edges.previous_article = friend_of_friend.curr_a)
        SELECT a2.text as prev_text, a1.text as next_text, prev_a, curr_a
        FROM article a1
                 join friend_of_friend e on a1.id = e.curr_a
         left join article a2 on e.prev_a = a2.id;
    """
    result = await database.fetch_all(query, values={"node_id": node_id})
    nodes = {}
    for i in result:
        nodes[i['prev_a']] = i['prev_text']
        nodes[i['curr_a']] = i['next_text']
    return Graph(
        edges=[GraphEdge(**dict(i)) for i in result],
        nodes=[GraphNode(text=val, id=key) for key, val in nodes.items()]
    )


@app.post("/note")
async def upload_note(note: NoteBody):
    note_dict = note.model_dump(exclude={'links'})
    query = "insert into article(text, tags) values (:text, :tags)"
    await database.execute(query=query, values=note_dict)
