import requests
import os
from typing import List
from string import punctuation
from random import choice
from random import randint
import base64

from webscout.AIbase import ImageProvider
from webscout.litagent import LitAgent  # Import our fire user agent generator 🔥
from webscout.Litlogger import Logger  # For that cyberpunk logging swag ⚡

# Initialize our fire logger 🚀
logger = Logger("FreeAIPlayground")

class FreeAIImager(ImageProvider):
    """
    FreeAI Image Provider - Your go-to for fire AI art! 🎨
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
        """Initialize your FreeAIPlayground provider with custom settings! ⚙️

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
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.session.proxies.update(proxies)
        self.timeout = timeout
        self.model = model
        self.prompt: str = "AI-generated image - webscout"
        self.image_extension: str = "png"
        self.logging = logging
        if self.logging:
            logger.info("FreeAIPlayground initialized! Ready to create some fire art! 🚀")

    def generate(
        self, prompt: str, amount: int = 1, additives: bool = True,
        size: str = "1024x1024", quality: str = "standard",
        style: str = "vivid"
    ) -> List[bytes]:
        """Generate some fire images from your prompt! 🎨

        Args:
            prompt (str): Your creative prompt
            amount (int): How many images to generate
            additives (bool): Add random characters to make prompts unique
            size (str): Image size (1024x1024, 1024x1792, 1792x1024)
            quality (str): Image quality (standard, hd)
            style (str): Image style (vivid, natural)

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
        for _ in range(amount):
            payload = {
                "model": self.model,
                "prompt": prompt + ads(),
                "n": 1,
                "size": size,
                "quality": quality,
                "style": style
            }
            try:
                resp = self.session.post(
                    url=self.image_gen_endpoint,
                    json=payload,
                    timeout=self.timeout
                )
                resp.raise_for_status()
                image_url = resp.json()['data'][0]['url']
                # Get the image data from the URL
                img_resp = self.session.get(image_url, timeout=self.timeout)
                img_resp.raise_for_status()
                response.append(img_resp.content)
                if self.logging:
                    logger.success(f"Generated image {len(response)}/{amount}! 🎨")
            except Exception as e:
                if self.logging:
                    logger.error(f"Failed to generate image: {e} 😢")
                raise

        if self.logging:
            logger.success("All images generated successfully! 🎉")
        return response

    def save(
        self,
        response: List[bytes],
        name: str = None,
        dir: str = os.getcwd(),
        filenames_prefix: str = "",
    ) -> List[str]:
        """Save your fire images! 💾

        Args:
            response (List[bytes]): List of image data
            name (str, optional): Base name for saved files
            dir (str, optional): Where to save the images
            filenames_prefix (str, optional): Prefix for filenames

        Returns:
            List[str]: List of saved filenames
        """
        assert isinstance(response, list), f"Response should be of {list} not {type(response)}"
        name = self.prompt if name is None else name

        if not os.path.exists(dir):
            os.makedirs(dir)
            if self.logging:
                logger.info(f"Created directory: {dir} 📁")

        if self.logging:
            logger.info(f"Saving {len(response)} images... 💾")

        filenames = []
        count = 0
        for image in response:
            def complete_path():
                count_value = "" if count == 0 else f"_{count}"
                return os.path.join(dir, name + count_value + "." + self.image_extension)

            while os.path.isfile(complete_path()):
                count += 1

            absolute_path_to_file = complete_path()
            filenames.append(filenames_prefix + os.path.split(absolute_path_to_file)[1])

            with open(absolute_path_to_file, "wb") as fh:
                fh.write(image)
            if self.logging:
                logger.success(f"Saved image to: {absolute_path_to_file} 💾")

        if self.logging:
            logger.success(f"All images saved successfully! Check {dir} 🎉")
        return filenames


if __name__ == "__main__":
    bot = FreeAIImager()
    try:
        resp = bot.generate("A shiny red sports car speeding down a scenic mountain road", 1)
        print(bot.save(resp))
    except Exception as e:
        if bot.logging:
            logger.error(f"An error occurred: {e} 😢")
