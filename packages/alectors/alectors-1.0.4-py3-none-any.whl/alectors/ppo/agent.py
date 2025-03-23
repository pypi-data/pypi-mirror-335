import os

import torch
import numpy as np

from tqdm import tqdm
from transformers import AutoModel, AutoTokenizer

from ..networks import PolicyNetwork, ValueNetwork
from .memory import Memory

class Agent:
    def __init__(
        self,
        action_dims: int = None,
        gamma: float = 0.99,
        epochs: int = 10,
        gae_lambda: float =0.95,
        policy_clip: float = 0.1,
        entropy: float = 0.001,
        batch_size: int = 64,
        encoder_name: str = 'bert-base-uncased',
        tokenizer_name: str = 'bert-base-uncased',
        actor_ridge: float = 0,
        actor_coefficient: float = 1.,
        actor_clip_grad_norm: float = None,
        critic_ridge: float = 0,
        critic_coefficient: float = 1.,
        critic_clip_grad_norm: float = None,
        name: str = 'alector',
        verbose: bool = False,
        load: bool = False,
        chkpt_dir: str = 'chkpts',
        device: str = 'cpu',
        **kwargs
        ):

        actor_hparams = {
            **kwargs.get("actor_hparams", {})
        }
        critic_hparams = {
            **kwargs.get("critic_hparams", {})
        }
        encoder_hparams = {
            **kwargs.get("encoder_hparams", {})
        }
        tokenizer_hparams = {
            **kwargs.get("tokenizer_hparams", {})
        }
        
        self.gamma = gamma
        self.epochs = epochs
        self.gae_lambda = gae_lambda
        self.policy_clip = policy_clip

        self.actor_coef = actor_coefficient
        self.actor_ridge_lambda = actor_ridge

        self.critic_coef = critic_coefficient
        self.critic_ridge_lambda = critic_ridge

        self.entropy_coef = entropy

        self.name = name
        self.verbose = verbose
        self.path = os.path.join(
            chkpt_dir,
            'ppo'
        )
        os.makedirs(self.path, exist_ok=True)
 
        self.device = device

        self.encoder = AutoModel.from_pretrained(
            pretrained_model_name_or_path=encoder_name,
            **encoder_hparams
        )
        self.encoder.eval()
        embed_dims = self.encoder.config.hidden_size

        self.tokenizer = AutoTokenizer.from_pretrained(
            pretrained_model_name_or_path=tokenizer_name,
            **tokenizer_hparams
        )
        vocab_size = self.tokenizer.vocab_size

        output_dims = action_dims or vocab_size

        self.actor = PolicyNetwork(
            input_dims=embed_dims,
            output_dims=output_dims,
            **actor_hparams
        )
        self.actor_clip_grad_norm = actor_clip_grad_norm

        self.critic = ValueNetwork(
            input_dims=embed_dims,
            **critic_hparams
        )
        self.critic_clip_grad_norm = critic_clip_grad_norm

        if load:
            if os.path.exists(os.path.join(self.path, f"{self.name}.pt")):
                self.load()
            else:
                if self.verbose:
                    print("No possible file to load from found. Initialising new agent")

        self.encoder.to(device)

        self.actor.to(device)
        actor_params = sum(p.numel() for p in self.actor.parameters())

        self.critic.to(device)
        critic_params = sum(p.numel() for p in self.critic.parameters())

        self.memory = Memory(
            batch_size=batch_size
        )

        if self.verbose:
            
            if load:
                print(f"agent successfully loaded from {self.path}/{self.name}")
            print(f"encoder ready on {self.device}. using {embed_dims} embedding dims")
            print(f"actor ready on {self.device}. total params: {actor_params}")
            print(f"critic ready on {self.device}. total params: {critic_params}")
            print(f"{self.name} initialised with {actor_params+critic_params} params.")
            print(f"tokenizer using {vocab_size} different tokens")

    @torch.no_grad()
    def choose_action(self, state):
        encoded_state = self.tokenizer(
            state,
            padding=True,
            truncation=True,
            return_tensors='pt'
        ).to(self.device)
        encoder_output = self.encoder(**encoded_state)
        embeddings = encoder_output['last_hidden_state']

        dist = self.actor(embeddings)
        value = self.critic(embeddings)
        action = dist.sample()

        probs = dist.log_prob(action)

        return action, probs, value, embeddings

    def save(self):
        to_save = dict(
            actor = dict(
                network = self.actor.state_dict(),
                optimizer = self.actor.optimizer.state_dict()
            ),
            critic = dict(
                network = self.critic.state_dict(),
                optimizer = self.critic.optimizer.state_dict()
            )
        )
        torch.save(
            to_save,
            os.path.join(
                self.path,
                f"{self.name}.pt"
            )
        )

    def load(self):
        chkpt = torch.load(
            os.path.join(
                self.path,
                f"{self.name}.pt"
            ),
            map_location=self.device,
            weights_only=True
        )
        self.actor.load_state_dict(
            chkpt['actor']['network']
        )
        self.actor.optimizer.load_state_dict(
            chkpt['actor']['optimizer']
        )
        self.critic.load_state_dict(
            chkpt['critic']['network']
        )
        self.critic.optimizer.load_state_dict(
            chkpt['critic']['optimizer']
        )

    def learn(self):
        total_loss_arr = []
        def calculate_total_loss():
            actor_contrib = self.actor_coef*self.actor_loss
            critic_contrib = self.critic_coef*self.critic_loss
            entropy_contrib = self.entropy_coef*self.entropy
            loss = actor_contrib + critic_contrib - entropy_contrib
            return loss

        for _ in tqdm(range(self.epochs), disable=not self.verbose, desc="Learning Epoch"):
            state_arr, action_arr, old_probs_arr, vals_arr, reward_arr, dones_arr, batches = self.memory.recall()

            advantage = np.zeros(len(reward_arr))
            for t in range(len(reward_arr)-1):
                discount = 1
                a_t = 0
                for k in range(t, len(reward_arr)-1):
                    a_t += discount*(reward_arr[k]+self.gamma*vals_arr[k+1]\
                            *(1-int(dones_arr[k]))-vals_arr[k])
                    discount *= self.gamma*self.gae_lambda
                advantage[t] = a_t

            for batch in batches:
                states = torch.tensor(
                    state_arr[batch]
                ).to(self.device).squeeze(1)
                old_probs = torch.tensor(old_probs_arr[batch]).to(self.device)
                actions = torch.tensor(action_arr[batch]).to(self.device)
                batch_values = torch.tensor(vals_arr[batch]).to(self.device)
                batch_advantages = torch.tensor(
                    advantage[batch]
                ).to(self.device)
        
                self.actor.optimizer.zero_grad()
                self.critic.optimizer.zero_grad()

                dist = self.actor(states)
                value = self.critic(states)

                self.entropy = dist.entropy().mean()

                new_probs = dist.log_prob(actions)
                prob_ratio = (new_probs-old_probs).exp()
                weighted_probs = batch_advantages*prob_ratio
                weighted_clipped_probs = torch.clamp(
                    prob_ratio,
                    min=1-self.policy_clip,
                    max=1+self.policy_clip
                )*batch_advantages

                self.actor_loss = torch.min(
                    weighted_probs,
                    weighted_clipped_probs
                ).mean()
                actor_ridge = sum(p.pow(2).sum() for p in self.actor.parameters())
                self.actor_loss += self.actor_ridge_lambda*actor_ridge

                returns = batch_advantages+batch_values
                self.critic_loss = ((returns-value)**2).mean()
                critic_ridge = sum(p.pow(2).sum() for p in self.critic.parameters())
                self.critic_loss += self.critic_ridge_lambda*critic_ridge

                self.total_loss = calculate_total_loss()
                self.total_loss.backward()

                if self.actor_clip_grad_norm is not None:
                    torch.nn.utils.clip_grad_norm_(
                        self.actor.parameters(),
                        max_norm=self.actor_clip_grad_norm
                    )

                if self.critic_clip_grad_norm is not None:
                    torch.nn.utils.clip_grad_norm_(
                        self.critic.parameters(),
                        max_norm=self.critic_clip_grad_norm
                    )

                self.actor.optimizer.step()
                self.critic.optimizer.step()
                total_loss_arr.append(self.total_loss.detach())

        self.memory.clear()
        return torch.tensor(total_loss_arr).mean()
