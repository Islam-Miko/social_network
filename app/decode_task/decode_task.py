from fastapi import APIRouter, Body, Request

router = APIRouter(prefix="/tasks/decode")


def decode_url(raw_url: str) -> str:
    raw_url = raw_url.replace("+", " ").replace("%", "\\x")
    encoded_url = raw_url.encode()
    decoded_url = encoded_url.decode("unicode_escape")
    return decoded_url


@router.post("/")
def decode_url_endpoint(
    request: Request, unencoded: str = Body(..., embed=True)
):
    decoded = decode_url(unencoded)
    return {"decoded_url": decoded}
