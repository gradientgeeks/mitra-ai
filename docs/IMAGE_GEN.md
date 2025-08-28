
Home
Gemini API
Gemini API docs
Was this helpful?

Send feedbackImage generation with Gemini


Gemini can generate and process images conversationally. You can prompt Gemini with text, images, or a combination of both allowing you to create, edit, and iterate on visuals with unprecedented control:

Text-to-Image: Generate high-quality images from simple or complex text descriptions.
Image + Text-to-Image (Editing): Provide an image and use text prompts to add, remove, or modify elements, change the style, or adjust the color grading.
Multi-Image to Image (Composition & Style Transfer): Use multiple input images to compose a new scene or transfer the style from one image to another.
Iterative Refinement: Engage in a conversation to progressively refine your image over multiple turns, making small adjustments until it's perfect.
High-Fidelity Text Rendering: Accurately generate images that contain legible and well-placed text, ideal for logos, diagrams, and posters.
All generated images include a SynthID watermark.

Note: You can also generate images with Imagen, our specialized image generation model. See the When to use Imagen section for details on how to choose between Gemini and Imagen.
Image generation (text-to-image)
The following code demonstrates how to generate an image based on a descriptive prompt.

Python
JavaScript
Go
REST

from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

client = genai.Client()

prompt = (
    "Create a picture of a nano banana dish in a fancy restaurant with a Gemini theme"
)

response = client.models.generate_content(
    model="gemini-2.5-flash-image-preview",
    contents=[prompt],
)

for part in response.candidates[0].content.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        image = Image.open(BytesIO(part.inline_data.data))
        image.save("generated_image.png")
AI-generated image of a nano banana dish
AI-generated image of a nano banana dish in a Gemini-themed restaurant
Image editing (text-and-image-to-image)
Reminder: Make sure you have the necessary rights to any images you upload. Don't generate content that infringe on others' rights, including videos or images that deceive, harass, or harm. Your use of this generative AI service is subject to our Prohibited Use Policy.

To perform image editing, add an image as input. The following example demonstrates uploading base64 encoded images. For multiple images, larger payloads, and supported MIME types, check the Image understanding page.

Python
JavaScript
Go
REST

from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

client = genai.Client()

prompt = (
    "Create a picture of my cat eating a nano-banana in a "
    "fancy restaurant under the Gemini constellation",
)

image = Image.open("/path/to/cat_image.png")

response = client.models.generate_content(
    model="gemini-2.5-flash-image-preview",
    contents=[prompt, image],
)

for part in response.candidates[0].content.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        image = Image.open(BytesIO(part.inline_data.data))
        image.save("generated_image.png")