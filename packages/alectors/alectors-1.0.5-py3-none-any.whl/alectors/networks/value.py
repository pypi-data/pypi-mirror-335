import torch
import torch.nn as nn

from .transformer import TransformerBlock, AttentionGate

from ..optimizers import Adam, UPGD

from ..utils import generate_layers

class ValueNetwork(nn.Module):
    def __init__(
        self,
        input_dims,
        transformer_layers: int = 2,
        optimizer_name: str = "adam",
        **kwargs
        ):
        gate_hparams = {
            **kwargs.get("gate", {})
        }
        network_defaults = dict(
            layers=None,
            activation_fn=None
        )
        network_architecture = {
            **network_defaults,
            **kwargs.get("network", {})
        }
        transformer_hparams = {
            **kwargs.get("transformer", {})
        }
        optimizer_hparams = {
            **kwargs.get("optimizer", {})
        }
        super(ValueNetwork, self).__init__()

        self.transformer = nn.ModuleList(
            [
                TransformerBlock(
                    embed_dims=input_dims,
                    **transformer_hparams,
                )
                for _ in range(transformer_layers)
            ]
        )

        self.gate = AttentionGate(
            embed_dims=input_dims,
            **gate_hparams
        )

        if network_architecture['layers'] is not None:
            layers = generate_layers(
                input_dims=input_dims,
                output_dims=1,
                **network_architecture
            )
            self.critic = nn.ModuleList(layers)
        else:
            self.critic = nn.ModuleList(
                [
                    nn.Linear(input_dims, 1)
                ]
            )

        if 'upgd' in optimizer_name.lower():
            self.optimizer = UPGD(
                params=self.parameters(),
                **optimizer_hparams
            )
        else:
            self.optimizer = Adam(
                params=self.parameters(),
                **optimizer_hparams
            )

    def forward(self, state, mask=None):
        out = state
        for layer in self.transformer:
            out = layer(out, out, out, mask)
        out = self.gate(out)
        for layer in self.critic:
            out = layer(out)
        value = out
        return value
