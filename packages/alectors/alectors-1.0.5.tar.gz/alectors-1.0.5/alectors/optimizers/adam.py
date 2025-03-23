import torch.optim as optim

class Adam(optim.Adam):
    """
        Set parameters to the Adam optimizer using a dict
    """
    def __init__(
        self,
        params,
        lr=0.001,
        betas=(0.9, 0.999),
        eps=1e-8,
        weight_decay=0,
        amsgrad=False,
        foreach=None,
        maximize=False,
        capturable=False,
        differentiable=False,
        fused=None
    ):
        super(Adam, self).__init__(
            params,
            lr=lr,
            betas=betas,
            eps=eps,
            weight_decay=weight_decay,
            amsgrad=amsgrad,
            foreach=foreach,
            maximize=maximize,
            capturable=capturable,
            differentiable=differentiable,
            fused=fused
        )
