import torch
from shap_e.diffusion.sample import sample_latents
from shap_e.diffusion.gaussian_diffusion import diffusion_from_config
from shap_e.models.download import load_model, load_config
from shap_e.util.notebooks import create_pan_cameras, decode_latent_images, gif_widget, decode_latent_mesh

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
xm = load_model('transmitter', device=device)
model = load_model('text300M', device=device)
diffusion = diffusion_from_config(load_config('diffusion'))
batch_size = 1
guidance_scale = 15.0
import socket
import json
import os

def generate_mesh(prompt: str) -> str:
    latents = sample_latents(
        batch_size=batch_size,
        model=model,
        diffusion=diffusion,
        guidance_scale=guidance_scale,
        model_kwargs=dict(texts=[prompt] * batch_size),
        progress=True,
        clip_denoised=True,
        use_fp16=True,
        use_karras=True,
        karras_steps=256,
        sigma_min=1e-3,
        sigma_max=160,
        s_churn=0,
    )
    try:
        for i, latent in enumerate(latents):
            t = decode_latent_mesh(xm, latent).tri_mesh()
            mesh_path = f'example_mesh_{i}.ply'
            with open(mesh_path, 'wb') as f:
                t.write_ply(f)
    except Exception as e:
        print("error!", e)
    return os.path.abspath(mesh_path)

def handle_client(conn):
    prompt = conn.recv(1024).decode()
    mesh_path = generate_mesh(prompt)
    print(mesh_path)
    response = json.dumps({"mesh_path": mesh_path})
    conn.send(response.encode())

HOST = 'localhost'
PORT = 8000
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print(f"Serving on port {PORT}")

while True:
    conn, addr = server_socket.accept()
    handle_client(conn)
    conn.close()
