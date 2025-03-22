import lightning
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from diffusionlab.distributions.gmm import IsoHomoGMMDistribution
from diffusionlab.distributions.empirical import EmpiricalDistribution
from diffusionlab.models import DiffusionModel
from diffusionlab.diffusions import OrnsteinUhlenbeckProcess
from diffusionlab.schedulers import UniformScheduler
from diffusionlab.samplers import EulerMaruyamaSampler
from diffusionlab.vector_fields import VectorField, VectorFieldType

lightning.seed_everything(42)


class TConditionedMLP(nn.Module):
    def __init__(self, D: int, M: int):
        super().__init__()
        self.t_embedding = nn.Parameter(torch.randn((M,)))
        self.w1 = nn.Linear(D, M)
        self.relu1 = nn.ReLU()
        self.w2 = nn.Linear(M, M)
        self.relu2 = nn.ReLU()
        self.w3 = nn.Linear(M, D)

    def forward(self, x: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        t_emb = t[:, None] * self.t_embedding[None, :]
        x = self.w1(x)
        x = self.relu1(x) + t_emb
        x = self.w2(x)
        x = self.relu2(x)
        x = self.w3(x)
        return x


D = 2
K = 4

t_min = 0.01
t_max = 0.99
L = 100

stochastic_sampler = False

scheduler = UniformScheduler()
train_ts_hparams = {"t_min": t_min, "t_max": t_max, "L": L}
diffusion_process = OrnsteinUhlenbeckProcess()
sampler = EulerMaruyamaSampler(diffusion_process, stochastic_sampler)

means = torch.randn(K, D) * 3
var = torch.tensor(0.5)
priors = torch.ones(K) / K
dist_params = {"means": means, "var": var, "priors": priors}
dist = IsoHomoGMMDistribution()

N_train = 100
N_val = 50
N_batch = 50
X_train, y_train = dist.sample(N_train, dist_params, {})
X_val, y_val = dist.sample(N_val, dist_params, {})
train_dataloader = DataLoader(
    TensorDataset(X_train, y_train), batch_size=N_batch, shuffle=True
)
val_dataloader = DataLoader(
    TensorDataset(X_val, y_val), batch_size=N_batch, shuffle=False
)

emp_dist = EmpiricalDistribution()
emp_dist_hparams = {"labeled_data": train_dataloader}

M = 100
net = TConditionedMLP(D, M)
optimizer = torch.optim.Adam(net.parameters(), lr=1e-3)
lr_scheduler = torch.optim.lr_scheduler.ConstantLR(optimizer, factor=1.0)


model = DiffusionModel(
    net=net,
    diffusion_process=diffusion_process,
    train_scheduler=scheduler,
    vector_field_type=VectorFieldType.X0,
    optimizer=optimizer,
    lr_scheduler=lr_scheduler,
    batchwise_metrics={},
    batchfree_metrics={},
    train_ts_hparams=train_ts_hparams,
    t_loss_weights=lambda t: torch.ones_like(t),
    t_loss_probs=lambda t: torch.ones_like(t) / L,
    N_noise_draws_per_sample=10,
)

N_epochs = 1000
trainer = lightning.Trainer(max_epochs=N_epochs, accelerator="cpu")
trainer.fit(model, train_dataloader, val_dataloader)

sampling_vector_field = VectorField(model, vector_field_type=model.vector_field_type)
# sampling_vector_field = VectorField(
#     lambda x, t: dist.eps(
#         x, t, diffusion_process, dist.batch_dist_params(x.shape[0], dist_params), {}
#     ),
#     vector_field_type=VectorFieldType.EPS,
# )  # if you want to use the true eps function
# sampling_vector_field = VectorField(
#     lambda x, t: emp_dist.eps(x, t, diffusion_process, {}, emp_dist_hparams),
#     vector_field_type=VectorFieldType.EPS,
# )  # if you want to use the empirical eps function

N_sample = 20
X0 = torch.randn(N_sample, D)
Zs = torch.randn(L - 1, N_sample, D, device=X0.device)
X_sample = sampler.sample(sampling_vector_field, X0, Zs, model.train_ts)

distances = torch.cdist(X_sample, X_train).min(dim=1)
print(distances)
