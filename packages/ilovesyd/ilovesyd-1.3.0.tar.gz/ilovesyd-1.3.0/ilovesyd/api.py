import aiohttp
import asyncio

class IloveSydAPI:
    BASE_URL = "https://ilovesyd.xyz/api"

    def __init__(self, api_key: str = None, proxy: str = None, retries: int = 3):
        self.api_key = api_key
        self.proxy = proxy
        self.retries = retries
        self.headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self.session = aiohttp.ClientSession()

    async def _request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        kwargs.setdefault("headers", self.headers)

        if self.proxy:
            connector = aiohttp.TCPConnector()
            async with aiohttp.ClientSession(connector=connector) as session:
                return await self._fetch(session, method, url, **kwargs)
        else:
            return await self._fetch(self.session, method, url, **kwargs)

    async def _fetch(self, session, method, url, **kwargs):
        for attempt in range(self.retries):
            try:
                async with session.request(method, url, **kwargs) as response:
                    response.raise_for_status()
                    return await response.json()
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(1)

        raise Exception(f"Failed after {self.retries} attempts")

    async def predict_pokemon(self, image_url: str):
        payload = {"image_url": image_url}
        return await self._request("POST", "predict", json=payload)

    async def test_connection(self):
        try:
            return await self._request("GET", "ss")
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.session.close()

