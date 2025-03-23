import torch
import torch.optim as optim

class UPGD(optim.Optimizer):
    """
        LICENSED UNDER MIT BY Mohamed Elsayed
        Paper: https://openreview.net/forum?id=sKPzAXoylB
        Code: https://github.com/mohmdelsayed/upgd
        LICENSED UNDER MIT BY Mohamed Elsayed

        Utility-based Perturbed Gradient Descent (UPGD) is an optimization method designed for
        continual learning in neural networks. It addresses two major issues of continual learning:
        catastrophic forgetting and loss of plasticity.

        The UPGD method uses a utility-based gating mechanism to modify the weights:
        - Weights with high utility are not sugnificantly updated, preventing them from being forgotten.
        - Weights with low utility are perturbed, allowing for plasticity in learning new tasks.

        The update rule also incorporates noise to further encourage plasticity, similar to Perturbed Gradient Descent (PGD).
        This method can be used in both standard and streaming learning setups.
    """
    def __init__(
        self,
        params,
        lr=1e-5,
        decay=0.001,
        beta=0.999,
        sigma=0.001
    ):

        hparams = dict(
            lr = lr,
            weight_decay = decay,
            beta_utility = beta,
            sigma = sigma,
        )
        
        super(UPGD, self).__init__(params, hparams)

    def step(self):
        global_max_util = torch.tensor(-torch.inf)
        for group in self.param_groups:
            for p in group['params']:
                state = self.state[p]
                if len(state) == 0:
                    state['step'] = 0
                    state['avg_utility'] = torch.zeros_like(p.data)
                state['step'] += 1
                avg_utility = state['avg_utility']
                avg_utility.mul_(group['beta_utility']).add_(
                    -p.grad.data*p.data,
                    alpha=1-group['beta_utility']
                )
                current_max_util = avg_utility.max()
                if current_max_util > global_max_util:
                    global_max_util = current_max_util
        for group in self.param_groups:
            for p in group['params']:
                state = self.state[p]
                bias_correction_util = 1-group['beta_utility']**state['step']
                noise = torch.randn_like(p.grad)*group['sigma']
                scaled_util = torch.sigmoid_((state['avg_utility']/bias_correction_util)/global_max_util)
                p.data.mul_(
                    1-group['lr']*group['weight_decay']
                ).add_(
                    (p.grad.data+noise)*(1-scaled_util),
                    alpha=-2.0*group['lr'],
                )
