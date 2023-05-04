import requests
import json
from pprint import pprint
import gradio as gr

API_KEY = "2b109sYMpWyL50uehM9kUesDMO"  # Your API_KEY here
PROJECT = "all";  # try specific floras: "weurope", "canada"…
api_endpoint = f"https://my-api.plantnet.org/v2/identify/{PROJECT}?api-key={API_KEY}&lang=zh"

def identify_plant(image_paths, organs):
    files = []
    for image_path in image_paths:
        image_data = open(image_path, 'rb')
        files.append(('images', (image_path, image_data)))
    data = {'organs': organs}
    req = requests.Request('POST', url=api_endpoint, files=files, data=data)
    prepared = req.prepare()
    s = requests.Session()
    response = s.send(prepared)
    json_result = json.loads(response.text)
    # Close the opened files
    for _, (_, image_data) in files:
        image_data.close()
    return response.status_code, json_result

def gradio_interface(image_path, organs):
    image_paths = [image_path]
    print(image_paths)
    status_code, json_result = identify_plant(image_paths, organs)
    return json_result.get("bestMatch",None), json_result

with gr.Blocks() as demo:
    image = gr.Image(type="filepath", label = "Plant Image")
    identify_btn = gr.Button("Identify")
    
    organs_input = gr.CheckboxGroup(choices=["flower", "leaf", "fruit", "bark", "habit"],label="Organs", info="What are the organs?")
    best_match_text = gr.Textbox(label="Scientific Name")
    json_text = gr.JSON(label="Raw Json String")
    
    identify_btn.click(gradio_interface, inputs=[image,organs_input], outputs = [best_match_text,json_text])

demo.launch()

