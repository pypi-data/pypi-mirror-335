import aiohttp
import asyncio
import os
from typing import List, Union, AsyncGenerator
from string import punctuation
from random import choice
import aiofiles

from webscout.AIbase import AsyncImageProvider
from webscout.litagent import LitAgent  # Import our fire user agent generator 🔥
from webscout.Litlogger import Logger  # For that cyberpunk logging swag ⚡

# Initialize our fire logger 🚀
logger = Logger("AsyncFreeAIPlayground")

class AsyncFreeAIImager(AsyncImageProvider):
    """
    Async FreeAI Image Provider - Your go-to for fire AI art! 🎨
    """
    
    AVAILABLE_MODELS = [
        "dall-e-3",
        "Flux Pro Ultra",
        "Flux Pro",
        "Flux Pro Ultra Raw",
        "Flux Schnell",
        "Flux Realism",
        "grok-2-aurora"
    ]

    def __init__(
        self,
        model: str = "dall-e-3",  # Updated default model
        timeout: int = 60,
        proxies: dict = {},
        logging: bool = True
    ):
        """Initialize your async FreeAIPlayground provider with custom settings! ⚙️

        Args:
            model (str): Which model to use (default: dall-e-3)
            timeout (int): Request timeout in seconds (default: 60)
            proxies (dict): Proxy settings for requests (default: {})
            logging (bool): Enable fire logging (default: True)
        """
        self.image_gen_endpoint: str = "https://api.freeaichatplayground.com/v1/images/generations"
        self.headers = {
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json",
            "User-Agent": LitAgent().random(),  # Using our fire random agent! 🔥
            "Origin": "https://freeaichatplayground.com",
            "Referer": "https://freeaichatplayground.com/",
        }
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.model = model
        self.proxies = proxies
        self.prompt: str = "AI-generated image - webscout"
        self.image_extension: str = "png"
        self.logging = logging
        if self.logging:
            logger.info("AsyncFreeAIPlayground initialized! Ready to create some fire art! 🚀")

    async def generate(
        self, prompt: str, amount: int = 1, additives: bool = True,
        size: str = "1024x1024", quality: str = "standard",
        style: str = "vivid", max_retries: int = 3, retry_delay: int = 5
    ) -> List[bytes]:
        """Generate some fire images from your prompt! 🎨

        Args:
            prompt (str): Your creative prompt
            amount (int): How many images to generate
            additives (bool): Add random characters to make prompts unique
            size (str): Image size (1024x1024, 1024x1792, 1792x1024)
            quality (str): Image quality (standard, hd)
            style (str): Image style (vivid, natural)
            max_retries (int): Max retry attempts if generation fails
            retry_delay (int): Delay between retries in seconds

        Returns:
            List[bytes]: Your generated images as bytes
        """
        assert bool(prompt), "Prompt cannot be null"
        assert isinstance(amount, int), f"Amount should be an integer only not {type(amount)}"
        assert amount > 0, "Amount should be greater than 0"

        ads = lambda: (
            ""
            if not additives
            else choice(punctuation)
            + choice(punctuation)
            + choice(punctuation)
        )

        if self.logging:
            logger.info(f"Generating {amount} images... 🎨")

        self.prompt = prompt
        response = []
        
        async with aiohttp.ClientSession(headers=self.headers, timeout=self.timeout) as session:
            for i in range(amount):
                payload = {
                    "model": self.model,
                    "prompt": prompt + ads(),
                    "n": 1,
                    "size": size,
                    "quality": quality,
                    "style": style
                }
                
                for attempt in range(max_retries):
                    try:
                        async with session.post(self.image_gen_endpoint, json=payload) as resp:
                            resp.raise_for_status()
                            data = await resp.json()
                            image_url = data['data'][0]['url']
                            
                            # Get the image data from the URL
                            async with session.get(image_url) as img_resp:
                                img_resp.raise_for_status()
                                image_bytes = await img_resp.read()
                                response.append(image_bytes)
                                
                            if self.logging:
                                logger.success(f"Generated image {len(response)}/{amount}! 🎨")
                            break
                    except Exception as e:
                        if attempt == max_retries - 1:
                            if self.logging:
                                logger.error(f"Failed to generate image after {max_retries} attempts: {e} 😢")
                            raise
                        if self.logging:
                            logger.warning(f"Attempt {attempt + 1} failed, retrying in {retry_delay}s... 🔄")
                        await asyncio.sleep(retry_delay)

        if self.logging:
            logger.success("All images generated successfully! 🎉")
        return response

    async def save(
        self,
        response: Union[List[bytes], AsyncGenerator[bytes, None]],
        name: str = None,
        dir: str = os.getcwd(),
        filenames_prefix: str = "",
    ) -> List[str]:
        """Save your fire images! 💾

        Args:
            response (Union[List[bytes], AsyncGenerator[bytes, None]]): Image data
            name (str, optional): Base name for saved files
            dir (str, optional): Where to save the images
            filenames_prefix (str, optional): Prefix for filenames

        Returns:
            List[str]: List of saved filenames
        """
        if not os.path.exists(dir):
            os.makedirs(dir)
            if self.logging:
                logger.info(f"Created directory: {dir} 📁")

        name = self.prompt if name is None else name
        saved_paths = []

        async def save_single_image(image_bytes: bytes, index: int) -> str:
            filename = f"{filenames_prefix}{name}_{index}.{self.image_extension}"
            filepath = os.path.join(dir, filename)
            
            async with aiofiles.open(filepath, "wb") as f:
                await f.write(image_bytes)
            
            if self.logging:
                logger.success(f"Saved image to: {filepath} 💾")
            return filename

        if isinstance(response, list):
            image_list = response
        else:
            image_list = [chunk async for chunk in response]

        if self.logging:
            logger.info(f"Saving {len(image_list)} images... 💾")

        tasks = [save_single_image(img, i) for i, img in enumerate(image_list)]
        saved_paths = await asyncio.gather(*tasks)

        if self.logging:
            logger.success(f"All images saved successfully! Check {dir} 🎉")
        return saved_paths


if __name__ == "__main__":
    async def main():
        bot = AsyncFreeAIImager()
        try:
            resp = await bot.generate("A shiny red sports car speeding down a scenic mountain road", 1)
            paths = await bot.save(resp)
            print(paths)
        except Exception as e:
            if bot.logging:
                logger.error(f"An error occurred: {e} 😢")

    asyncio.run(main())
