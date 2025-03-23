from .models import Vocos
from .convert import convert_torch_weights
from os import environ
from pathlib import Path
import os
import requests
import flax

def convert_torch_weights_to_msgpack(torch_weights_path: Path,  write_path: Path):
    if write_path.exists():
        return

    write_path.parent.mkdir(parents=True, exist_ok=True)

    # 先转换 torch 权重
    weights = convert_torch_weights(torch_weights_path)
    # 将权重和配置组合成一个字典
    data = {"params": weights}
    serialized_data = flax.serialization.msgpack_serialize(data)
    with open(write_path, "wb") as msgpack_file:
        msgpack_file.write(serialized_data)

def download_model():
    # 使用环境变量 JAX_BIGVGAN_CACHE 设置缓存路径，否则默认存放在 ~/.cache/jax_bigvgan
    if 'JAX_BIGVGAN_CACHE' in environ and environ['JAX_BIGVGAN_CACHE'].strip() and os.path.isabs(environ['JAX_BIGVGAN_CACHE']):
        cache_home = Path(environ['JAX_BIGVGAN_CACHE'])
    else:
        cache_home = Path.home() / ".cache" / "jax_bigvgan"

    # 最终合成后的 msgpack 文件路径
    jax_write_path = cache_home / f"vocos_mel.msgpack"

    if jax_write_path.exists():
        return jax_write_path

    # BigVGan 模型权重和配置文件的下载链接（请替换为实际地址）
    download_link_model = "https://huggingface.co/charactr/vocos-mel-24khz/resolve/main/pytorch_model.bin"
    #download_link_config = "https://huggingface.co/nvidia/bigvgan_v2_24khz_100band_256x/raw/main/config.json"

    torch_model_path = cache_home / f"vocos_mel.pt"
    #config_path = cache_home / f"bigvgan_{model_type}_config.json"

    # 下载 torch 模型权重
    if not torch_model_path.exists():
        torch_model_path.parent.mkdir(parents=True, exist_ok=True)
        response = requests.get(download_link_model)
        if response.status_code != 200:
            raise ValueError(f"Could not download model. Received response code {response.status_code}")
        torch_model_path.write_bytes(response.content)

    # 下载配置文件
    # if not config_path.exists():
    #     config_path.parent.mkdir(parents=True, exist_ok=True)
    #     response = requests.get(download_link_config)
    #     if response.status_code != 200:
    #         raise ValueError(f"Could not download config. Received response code {response.status_code}")
    #     config_path.write_bytes(response.content)

    # 读取 JSON 格式的配置
    # with open(config_path, "r", encoding="utf-8") as f:
    #     config = json.load(f)

    # 合并转换后的权重和配置后保存为 msgpack 文件
    convert_torch_weights_to_msgpack(torch_model_path, jax_write_path)

    # 模型权重文件下载完成后可以选择性删除
    if torch_model_path.exists():
        os.remove(torch_model_path)
    # 如果不再需要，也可以删除 config 文件
    # os.remove(config_path)

    return jax_write_path

def load_model(load_path = None):
    if not load_path:
        load_path = download_model()
    with open(load_path, "rb") as msgpack_file:
        msgpack_content = msgpack_file.read()
    data = flax.serialization.msgpack_restore(msgpack_content)
    params = data["params"]
    model = Vocos()
    

    return model,params
