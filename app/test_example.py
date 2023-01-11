async def test_example(client, session):
    response = await client.get("/")
    assert response.json() == {"msg": "ok"}
