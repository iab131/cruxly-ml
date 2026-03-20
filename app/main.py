from fastapi import FastAPI, UploadFile
from app.route_solver import build_graph, find_route

app = FastAPI()

@app.post("/solve")
async def solve(file: UploadFile):
    # TODO: save image

    # TEMP: fake holds
    holds = [
        {"x": 100, "y": 500, "color": "red"},
        {"x": 150, "y": 400, "color": "red"},
        {"x": 200, "y": 300, "color": "red"},
    ]

    graph = build_graph(holds)
    route = find_route(graph, holds)

    return {
        "holds": holds,
        "route": route
    }