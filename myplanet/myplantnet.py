import requests
import json
from pprint import pprint
import gradio as gr

API_KEY = "2b109sYMpWyL50uehM9kUesDMO"  # Your API_KEY here
PROJECT = "all";  # try specific floras: "weurope", "canada"…
api_endpoint = f"https://my-api.plantnet.org/v2/identify/{PROJECT}?api-key={API_KEY}"

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


def gradio_interface(files, organs):
    image_paths = [file.name for file in files]
    print(image_paths)
    status_code, json_result = identify_plant(image_paths, organs)
    return json_result
with gr.Blocks() as demo:
    file_output = gr.File()
    upload_button = gr.UploadButton("Click to Upload a File", file_types=["image", "video"], file_count="multiple")
    organs_input = gr.CheckboxGroup(choices=["flower", "leaf", "fruit", "bark", "habit"])
    outputs = gr.outputs.JSON()
    upload_button.upload(gradio_interface, inputs=[upload_button,organs_input], outputs = outputs)

#gr.Interface(fn=gradio_interface, inputs=[image_input, organs_input], outputs=outputs).launch()
demo.launch(share=True)

