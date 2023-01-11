async def test_example(client):
    response = await client.get("/")
    assert response.json() == {"ok": "pong"}
