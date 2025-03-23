import asyncio
from curl_cffi import requests

class IloveSydAPI:
    BASE_URL = "https://ilovesyd.xyz/api"

    def __init__(self, api_key: str = None, proxy: str = None, retries: int = 3):
        """
        Wrapper for ilovesyd.xyz API.

        :param api_key: API key for authentication.
        :param proxy: Proxy URL (optional).
        :param retries: Number of retry attempts on failure.
        """
        self.api_key = api_key
        self.proxy = proxy
        self.retries = retries
        self.headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    async def _request(self, method: str, endpoint: str, **kwargs):
        """
        Internal method to handle API requests with retries.
        """
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        kwargs.setdefault("headers", self.headers)
        kwargs.setdefault("proxy", self.proxy)

        for attempt in range(self.retries):
            try:
                response = await requests.request(
                    method, url, **kwargs, impersonate="chrome"
                )
                response.raise_for_status()
                return response.json()
            except requests.RequestsError as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(1)

        raise Exception(f"Failed after {self.retries} attempts")

    async def predict_pokemon(self, image_url: str):
        """
        Predicts a Pokémon from an image URL.

        :param image_url: URL of the Pokémon image.
        :return: JSON response with the predicted Pokémon.
        """
        payload = {"image_url": image_url}
        return await self._request("POST", "predict", json=payload)

    async def upload_screenshot(self, file_path: str):
        """
        Uploads an image to the API.

        :param file_path: Path to the image file.
        :return: JSON response with the uploaded image URL.
        """
        with open(file_path, "rb") as f:
            files = {"file": (file_path, f, "image/png")}
            return await self._request("POST", "upload/", files=files)

    async def get_screenshot(self, image_id: str):
        """
        Fetches a processed screenshot by ID.

        :param image_id: ID of the uploaded image.
        :return: Binary image data.
        """
        return await self._request("GET", f"i/{image_id}")

    async def test_connection(self):
        """
        Tests if the API is reachable.
        """
        try:
            response = await self._request("GET", "ss")
            return response
        except Exception as e:
            return {"error": str(e)}
