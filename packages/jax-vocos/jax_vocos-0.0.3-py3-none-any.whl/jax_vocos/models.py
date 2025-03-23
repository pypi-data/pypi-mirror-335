from typing import Any, Optional
import jax
import jax.numpy as jnp
import flax.linen as nn
import flax

class ISTFT(nn.Module):
    """
    自定义 ISTFT 实现，支持 "same" 和 "center" 填充模式。

    参数:
        n_fft (int): 傅里叶变换的大小。
        hop_length (int): 相邻滑动窗口帧之间的距离。
        win_length (int): 窗口帧和 STFT 滤波器的大小。
        padding (str, optional): 填充类型，"center" 或 "same"。默认为 "same"。
    """
    n_fft: int = 1024
    hop_length: int = 256
    win_length: int = 1024
    padding: str = "same"

    def setup(self):
        # 验证填充类型
        if self.padding not in ["center", "same"]:
            raise ValueError("Padding must be 'center' or 'same'.")
        # 定义窗口函数作为可学习参数
        window = self.param('window', lambda key: jnp.hanning(self.win_length))
        self.window = window

    @nn.compact
    def __call__(self, spec):
        # 根据填充类型设置参数
        if self.padding == "center":
            raise NotImplementedError("Center padding not implemented yet.")
        elif self.padding == "same":
            pad = (self.win_length - self.hop_length) // 2

        # 输入张量维度检查
        B, N, T = spec.shape

        # 逆 FFT
        ifft = jax.numpy.fft.irfft(spec, n=self.n_fft, axis=1, norm="backward")
        ifft = ifft * self.window[None, :, None]

        # 计算输出长度
        output_size = (T - 1) * self.hop_length + self.win_length

        # 重叠相加
        y = self._overlap_add(ifft, output_size, pad)

        # 计算窗口包络
        window_sq = self.window ** 2
        window_sq = window_sq[None, :, None].repeat(T, axis=2)
        window_envelope = self._overlap_add(window_sq, output_size, pad)

        # 归一化
        y = y / (window_envelope + 1e-11)
        return y

    def _overlap_add(self, ifft, output_size, pad):
        """手动实现重叠相加操作"""
        B, N, T = ifft.shape
        y = jnp.zeros((B, output_size))
        for t in range(T):
            start = t * self.hop_length
            end = start + self.win_length
            y = y.at[:, start:end].add(ifft[:, :, t])
        return y[:, pad:-pad]
    
class ISTFTHead(nn.Module):
    """
    ISTFT 头部模块，用于预测 STFT 复系数。

    参数:
        dim (int): 模型的隐藏维度。
        n_fft (int): 傅里叶变换的大小。
        hop_length (int): 相邻滑动窗口帧之间的距离。
        padding (str, optional): 填充类型，"center" 或 "same"。默认为 "same"。
    """
    dim: int = 512
    n_fft: int = 1024
    hop_length: int = 256
    padding: str = "same"

    @nn.compact
    def __call__(self, x):
        # 输出维度
        out_dim = self.n_fft + 2
        # 全连接层
        x = nn.Dense(out_dim)(x)
        # 转置张量维度: (B, L, H) -> (B, H, L)
        x = jnp.transpose(x, (0, 2, 1))
        # 分割幅度和相位
        mag, p = jnp.split(x, 2, axis=1)
        # 计算幅度
        mag = jnp.exp(mag)
        mag = jnp.clip(mag, a_max=1e2)  # 限制最大值
        # 计算实部和虚部
        x = jnp.cos(p)
        y = jnp.sin(p)
        # 构造复数谱
        S = mag * (x + 1j * y)
        # 调用 ISTFT 重建音频
        audio = ISTFT(n_fft=self.n_fft, hop_length=self.hop_length, 
                      win_length=self.n_fft, padding=self.padding)(S)
        return audio
    
class ConvNeXtBlock(nn.Module):
    """
    ConvNeXt 块，适配为 1D 音频信号。

    参数:
        dim (int): 输入通道数。
        intermediate_dim (int): 中间层维度。
        layer_scale_init_value (float): 层缩放的初始值，若为 0 则不应用缩放。
        adanorm_num_embeddings (int, 可选): AdaLayerNorm 的嵌入数量，若为 None 则使用普通 LayerNorm。
    """
    dim: int 
    intermediate_dim: int
    layer_scale_init_value: float
    adanorm_num_embeddings: int = None

    @nn.compact
    def __call__(self, x, cond_embedding_id=None):
        residual = x
        # 深度卷积
        x = nn.Conv(features=self.dim, kernel_size=(7,), padding='SAME', 
                    feature_group_count=self.dim)(x)
        # 调整维度: (B, C, T) -> (B, T, C)
        # 条件归一化或普通归一化
        if self.adanorm_num_embeddings is not None:
            assert cond_embedding_id is not None
            x = AdaLayerNorm(self.adanorm_num_embeddings, self.dim)(x, cond_embedding_id)
        else:
            x = nn.LayerNorm(epsilon=1e-6)(x)
        # 逐点卷积
        x = nn.Dense(self.intermediate_dim)(x)
        x = nn.gelu(x)
        x = nn.Dense(self.dim)(x)
        # 层缩放（可选）
        if self.layer_scale_init_value > 0:
            gamma = self.param('gamma', 
                             lambda key: self.layer_scale_init_value * jnp.ones((self.dim,)))
            x = gamma * x
        # 恢复维度: (B, T, C) -> (B, C, T)
        # 残差连接
        x = residual + x
        return x


class AdaLayerNorm(nn.Module):
    """
    自适应层归一化模块，支持基于条件嵌入的缩放和偏移。

    参数:
        num_embeddings (int): 嵌入的数量。
        embedding_dim (int): 嵌入的维度。
        eps (float): 归一化的稳定性参数，默认为 1e-6。
    """
    num_embeddings: int
    embedding_dim: int
    eps: float = 1e-6

    @nn.compact
    def __call__(self, x, cond_embedding_id):
        # 生成缩放和偏移的嵌入向量
        scale = nn.Embed(self.num_embeddings, self.embedding_dim, 
                        init_fn=nn.initializers.ones)(cond_embedding_id)
        shift = nn.Embed(self.num_embeddings, self.embedding_dim, 
                        init_fn=nn.initializers.zeros)(cond_embedding_id)
        # 应用层归一化
        x = nn.LayerNorm(epsilon=self.eps)(x)
        # 应用缩放和偏移
        x = x * scale + shift
        return x
    
class VocosBackbone(nn.Module):
    """
    Vocos 主干网络，基于 ConvNeXt 块构建，支持自适应层归一化条件。

    参数:
        input_channels (int): 输入特征通道数。
        dim (int): 模型的隐藏维度。
        intermediate_dim (int): ConvNeXtBlock 的中间维度。
        num_layers (int): ConvNeXtBlock 的层数。
        layer_scale_init_value (float, 可选): 层缩放初始值，默认为 1/num_layers。
        adanorm_num_embeddings (int, 可选): AdaLayerNorm 的嵌入数量，若为 None 则非条件模型。
    """
    input_channels: int = 100
    dim: int = 512
    intermediate_dim: int = 1536
    num_layers: int = 8
    layer_scale_init_value: float = None
    adanorm_num_embeddings: int = None

    @nn.compact
    def __call__(self, x, bandwidth_id=None):
        # 默认层缩放初始值
        layer_scale_init_value = self.layer_scale_init_value or 1 / self.num_layers
        # 嵌入层
        x = nn.Conv(features=self.dim, kernel_size=(7,), padding='SAME')(x)
        # 条件归一化或普通归一化
        if self.adanorm_num_embeddings is not None:
            assert bandwidth_id is not None
            x = AdaLayerNorm(self.adanorm_num_embeddings, self.dim)(
                jnp.transpose(x, (0, 2, 1)), bandwidth_id)
        else:
            x = nn.LayerNorm(epsilon=1e-6)(x)
        # 堆叠 ConvNeXtBlock
        for _ in range(self.num_layers):
            x = ConvNeXtBlock(
                dim=self.dim,
                intermediate_dim=self.intermediate_dim,
                layer_scale_init_value=layer_scale_init_value,
                adanorm_num_embeddings=self.adanorm_num_embeddings
            )(x, cond_embedding_id=bandwidth_id)
        # 最终归一化
        x = nn.LayerNorm(epsilon=1e-6)(x)
        return x
class Vocos(nn.Module):
    @nn.compact
    def __call__(self,x):
        x = VocosBackbone()(x)
        audio_output = ISTFTHead()(x)
        return audio_output

if __name__ == "__main__":
    import librosa
    import numpy as np
    from src.jax_vocos.util import get_mel
    import soundfile as sf
    from convert import convert_torch_weights
    model = Vocos()
    wav,sr = librosa.load("./test.wav",sr=24000)
    wav = wav[np.newaxis,:]
    mel = get_mel(wav)
    #mel = mel.transpose(0,2,1)
    #params = model.init(jax.random.PRNGKey(0),mel)
    #flatten_param = flax.traverse_util.flatten_dict(params,sep='.')

    params = convert_torch_weights()
    rng = {'params': jax.random.PRNGKey(0), 'dropout': jax.random.PRNGKey(0)}
    res = model.apply({"params":params},mel,rngs=rng)
    sf.write("output.wav",res[0],samplerate=24000)
    print()