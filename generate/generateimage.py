

import sys
sys.path.append('../')
import config  
from base64 import b64decode
import webbrowser
import openai
#this is the copout way.  
#do we want to spend time understanding the image generation at the moment?  

def generateImage(prompt, image_count):
    images = []
    response = openai.Image.create(prompt=prompt, n=image_count, size='512x512', response_format='b64_json')
    
    for image in response['data']:
        images.append(image.b64_json)
        
    prefix = 'Img'
    for index,image in enumerate(images):
        with open(f'{prefix}_{index}.jpg', 'wb') as file:
            file.write(b64decode(image))

openai.api_key =config.cfg["openai"]["APIKEY"]
generateImage("Grand Canyon", 1)
        
#notebook_login()

#experimental_pipe = StableDiffusionPipeline.from_pretrained("CompVis/stable-diffusion-v1-4", revision="fp16", torch_dtype=torch.float16, use_auth_token=True) 

#description_1 = "a photograph of an horse on moon"
#image_1 = experimental_pipe(description_1).images[0]  
# Now to display an image you can do either save it such as:
#image_1.save(f"horse_moon.png")