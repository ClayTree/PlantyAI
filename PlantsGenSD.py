import openai
import random
import gradio as gr
import time
import os

openai.api_key = os.environ["OPENAI_API_KEY"]

# Define plant characteristics
characteristics = {
    "locations":["North America", "South America", "Europe", "Asia", "Africa", "Australia", "woodland", "desert", "tundra", "rainforest", "temperate"],
    "plant_types":["tree", "shrub", "vine", "herb", "grass"],
    "leaf_arrangements":["alternate", "opposite", "whorled", "basal", "spiral"],
    "leaf_shapes":["ovate", "lanceolate", "elliptical", "linear", "lobed", "cordate", "deltoid", "obovate", "pinnate", "palmate"],
    "leaf_margins":["smooth", "serrated", "toothed", "lobed", "undulate", "entire", "crenate"],
    "stems":["woody", "herbaceous", "square", "round", "ridged", "hollow"],
    "flower_colors":["white", "yellow", "red", "blue", "purple", "pink", "green", "orange", "multicolor", "none"],
    "flower_structures":["solitary", "cluster", "spike", "raceme", "umbel", "panicle", "corymb", "head"],
    "fruits":["berry", "capsule", "nut", "achene", "drupe", "samara", "pome", "none"],
    "additional_features":["thorns", "fragrance", "milky sap", "bristles", "succulent", "none"],
}

def generate_plant_prompt():
    template = "Generate a unique plant with the following characteristics:\n"
    for char, values in characteristics.items():
        random_value = random.choice(values)
        template += f"- {char.capitalize()}: {random_value}\n"
    template += "just give me the scientific name.no other text,just reply a single word NONE if not found, just NONE, no other texts."
    return template

def generate_plant_description(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

    import requests

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
headers = {"Authorization": f"Bearer {os.environ['HUGGINGFACE_API_KEY']}"}

import requests
def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content

from PIL import Image
import io

from bs4 import BeautifulSoup

def search_image_url(plant_name):
    if plant_name == "NONE":
        return None
    search_url = f"https://www.bing.com/images/search?q={plant_name}+plant"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, "html.parser")
    image_url = soup.find("img", class_="mimg").get("src")

    image_response = requests.get(image_url)
    image = Image.open(io.BytesIO(image_response.content))
    return image


def generate_image_stable_diffusion(plant_name, prompt):
    if plant_name == "NONE":
        return None
    try:
        image_bytes = query({
            "inputs": plant_name + ", realistic, photograph",
        })
        # print(image_bytes)
        image = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        print(f"Error: {e}")
        image = None

    return image


def generate_plant_name_and_prompt():
    prompt = generate_plant_prompt()
    plant_description = generate_plant_description(prompt)
    plant_name = plant_description.strip()
    return plant_name, prompt

def generate_plant_image_and_name_and_prompt():
    plant_name, prompt = generate_plant_name_and_prompt()
    image_generated = generate_image_stable_diffusion(plant_name, prompt)
    image_url = search_image_url(plant_name)
    return image_generated, image_url, plant_name, prompt


with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=1, min_width=600):
            image_sd = gr.Image(type='pil', label="Generated Image")
        with gr.Column(scale=1, min_width=600):
            image_url =  gr.Image(type='pil', label="Image from URL")
    with gr.Row():
        prompt_box = gr.Textbox(label="Prompt")
        plant_name_box = gr.Textbox(label="Plant Name"), gr.outputs.Textbox(label="Prompt")
        text_button = gr.Button("Generate Plant!")

    text_button.click(generate_plant_image_and_name_and_prompt, inputs = [], outputs = [image_sd,image_url,plant_name_box, plant_name_box] )
# iface = gr.Interface(fn=generate_plant_image_and_name_and_prompt_with_cooldown, inputs=[], outputs=[gr.Image(type='pil', label="Generated Image"), gr.outputs.Image(type='pil', label="Image from URL"), gr.outputs.Textbox(label="Plant Name"), gr.outputs.Textbox(label="Prompt")], title="Plant Image and Name Generator", layout="horizontal", live=False)
# iface = gr.Interface(fn=generate_plant_image_and_name_and_prompt_with_cooldown, inputs=[], outputs=[gr.Image(type='pil', label="Generated Image"), gr.outputs.Image(type='pil', label="Image from URL"), ], title="Plant Image and Name Generator", layout="horizontal", live=False)

demo.launch()

