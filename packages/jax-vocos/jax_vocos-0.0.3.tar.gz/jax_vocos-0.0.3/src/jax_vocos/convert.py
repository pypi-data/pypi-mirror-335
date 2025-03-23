import flax
import torch

def convert_torch_weights(path="pytorch_model.bin"):
    state_dict = torch.load(path, map_location=torch.device('cpu'))
    params = {}

    # Initial Conv_0
    params["VocosBackbone_0.Conv_0.kernel"] = state_dict["backbone.embed.weight"].T
    params["VocosBackbone_0.Conv_0.bias"] = state_dict["backbone.embed.bias"]

    # Initial LayerNorm_0
    params["VocosBackbone_0.LayerNorm_0.scale"] = state_dict["backbone.norm.weight"]
    params["VocosBackbone_0.LayerNorm_0.bias"] = state_dict["backbone.norm.bias"]

    # ConvNeXtBlocks 0 to 7
    for i in range(8):
        params[f"VocosBackbone_0.ConvNeXtBlock_{i}.Conv_0.kernel"] = state_dict[f"backbone.convnext.{i}.dwconv.weight"].T
        params[f"VocosBackbone_0.ConvNeXtBlock_{i}.Conv_0.bias"] = state_dict[f"backbone.convnext.{i}.dwconv.bias"]
        params[f"VocosBackbone_0.ConvNeXtBlock_{i}.LayerNorm_0.scale"] = state_dict[f"backbone.convnext.{i}.norm.weight"]
        params[f"VocosBackbone_0.ConvNeXtBlock_{i}.LayerNorm_0.bias"] = state_dict[f"backbone.convnext.{i}.norm.bias"]
        params[f"VocosBackbone_0.ConvNeXtBlock_{i}.Dense_0.kernel"] = state_dict[f"backbone.convnext.{i}.pwconv1.weight"].T
        params[f"VocosBackbone_0.ConvNeXtBlock_{i}.Dense_0.bias"] = state_dict[f"backbone.convnext.{i}.pwconv1.bias"]
        params[f"VocosBackbone_0.ConvNeXtBlock_{i}.Dense_1.kernel"] = state_dict[f"backbone.convnext.{i}.pwconv2.weight"].T
        params[f"VocosBackbone_0.ConvNeXtBlock_{i}.Dense_1.bias"] = state_dict[f"backbone.convnext.{i}.pwconv2.bias"]
        params[f"VocosBackbone_0.ConvNeXtBlock_{i}.gamma"] = state_dict[f"backbone.convnext.{i}.gamma"]

    # Final LayerNorm_1
    params["VocosBackbone_0.LayerNorm_1.scale"] = state_dict["backbone.final_layer_norm.weight"]
    params["VocosBackbone_0.LayerNorm_1.bias"] = state_dict["backbone.final_layer_norm.bias"]

    # ISTFTHead
    params["ISTFTHead_0.Dense_0.kernel"] = state_dict["head.out.weight"].T
    params["ISTFTHead_0.Dense_0.bias"] = state_dict["head.out.bias"]
    params["ISTFTHead_0.ISTFT_0.window"] = state_dict["head.istft.window"]

    # Convert to numpy and unflatten
    params = {k: v.cpu().numpy() for k, v in params.items()}
    params = flax.traverse_util.unflatten_dict(params, sep=".")
    return params