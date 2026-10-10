import asyncio
import provider


class FakeResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {"message": {"content": "Hello Founder"}}


class FakeClient:
    last_payload = None

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def post(self, url, json):
        FakeClient.last_payload = json
        return FakeResponse()


def test_chat_does_not_duplicate_current_turn(monkeypatch):
    monkeypatch.setattr(provider.httpx, "AsyncClient", FakeClient)
    history = [{"role": "user", "content": "previous question"},
               {"role": "assistant", "content": "previous answer"}]
    answer = asyncio.run(provider.chat("current question", history=history))
    assert answer == "Hello Founder"
    turns = [m["content"] for m in FakeClient.last_payload["messages"] if m["role"] == "user"]
    assert turns.count("current question") == 1
    assert "previous question" in turns
