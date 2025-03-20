import numpy as np
import torch
import torch.nn as nn
from matplotlib import pyplot as plt

from src.nystrom_ncut import NystromNCut, affinity_from_features, SampleConfig, subsample_features

# from ncut_pytorch.src import rgb_from_umap_sphere
# from ncut_pytorch.src.new_ncut_pytorch import NewNCUT

# from ncut_pytorch.ncut_pytorch.backbone_text import load_text_model

from sklearn.decomposition import PCA
from sklearn.manifold import TSNE


if __name__ == "__main__":
    # from src.nystrom_ncut.visualize_utils import rgb_from_3d_lab_cube
    # M = torch.randn((100, 3))
    # print(rgb_from_3d_lab_cube(M))
    # raise Exception()

    # torch.manual_seed(1212)
    # M = torch.randn((7, 3))
    # W = torch.nn.functional.cosine_similarity(M[:, None], M[None, :], dim=-1)
    # A = torch.exp(W - 1)
    # D_s2 = torch.sum(A, dim=-1, keepdim=True) ** -0.5
    # # print(A)
    # print(A * D_s2 * D_s2.mT)
    #
    # ncut = NCut(n_components=7, eig_solver="svd")
    # V, L = ncut.fit_transform(M)
    # print(V @ torch.diag(L) @ V.mT)
    # raise Exception()

    # print(load_text_model("meta-llama/Meta-Llama-3.1-8B").cuda())
    # print(AutoModelForCausalLM.from_pretrained(
    #     "meta-llama/Meta-Llama-3.1-8B",
    #     token="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",
    # ))
    # # print(transformers.pipeline(
    # #     "text-generation",
    # #     model="meta-llama/Meta-Llama-3.1-8B",
    # #     model_kwargs={"torch_dtype": torch.bfloat16},
    # #     token="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",
    # #     device="cpu",
    # # ))
    # raise Exception(

    torch.set_printoptions(precision=8, sci_mode=False, linewidth=400)
    torch.set_default_dtype(torch.float64)
    torch.manual_seed(1212)
    np.random.seed(1212)


    n, d = 10000, 2
    num_sample = 30

    M = torch.randn((n, d))
    M[:int(0.9 * n)] += 3
    M[int(0.9 * n):] -= 3

    distance = "rbf"

    A = affinity_from_features(M, distance=distance)
    R = torch.diag(torch.sum(A, dim=-1) ** -0.5)
    L = R @ A @ R

    n_components = 30   # num_sample
    eig_solver = "svd_lowrank"

    nc = NystromNCut(
        n_components=n_components,
        sample_config=SampleConfig(method="random", num_sample=num_sample),
        distance=distance,
        eig_solver=eig_solver,
    )

    torch.seed()
    indices = subsample_features(M, distance_type=distance, config=SampleConfig(method="fps", num_sample=num_sample))
    samples = nn.Parameter(M[indices])

    optimizer = torch.optim.AdamW((samples,), lr=1e-1)

    output_dir = "../output/anchor_features_descent"
    relative_losses, absolute_losses = [], []
    for it in range(1000):
        if it % 10 == 0:
            plt.scatter(*M.mT, color="red")
            plt.scatter(*samples.mT.detach(), color="black")
            plt.title(f"Iteration {it}")

            plt.savefig(f"{output_dir}/iteration{it}.png")
            plt.show()

        all_points = torch.cat((samples, M), dim=0)

        X, eigs = nc.fit_transform(all_points, precomputed_sampled_indices=torch.arange(num_sample))
        X = X[num_sample:]

        _L = X @ torch.diag(eigs) @ X.mT

        relative_loss = torch.linalg.norm(_L / L - 1) ** 2
        with torch.no_grad():
            absolute_loss = torch.linalg.norm(_L - L) ** 2

        optimizer.zero_grad()
        relative_loss.backward()
        optimizer.step()

        print(f"Relative: {relative_loss.item()}, Absolute: {absolute_loss.item()}")
        relative_losses.append(relative_loss.item())
        absolute_losses.append(absolute_loss.item())

    torch.save(torch.tensor(relative_losses), f"{output_dir}/relative_losses.pt")
    torch.save(torch.tensor(absolute_losses), f"{output_dir}/absolute_losses.pt")

    raise Exception()


    # C = L[num_sample:, num_sample:]
    #
    # _A = L[:num_sample, :num_sample]
    # _B = L[:num_sample, num_sample:]
    # extrapolated_C = _B.mT @ torch.inverse(_A) @ _B
    #
    # RE = torch.abs(extrapolated_C / C - 1)
    # print(torch.max(RE).item(), torch.mean(RE).item(), torch.min(RE).item())

    n_components = 30   # num_sample
    eig_solver = "svd_lowrank"

    def rel_error(X, eigs):
        _L = X @ torch.diag(eigs) @ X.mT
        return torch.abs(_L / L - 1)

    def print_re(re):
        print(f"max: {re.max().item()}, mean: {re.mean().item()}, min: {re.min().item()}")

    max_rel = []
    for _ in range(1):
        nc = NCut(
            n_components=n_components,
            # sample_config=SampleConfig(method="random", num_sample=num_sample),
            sample_config=SampleConfig(method="fps_recursive", num_sample=num_sample, n_iter=10),
            distance=distance,
            eig_solver=eig_solver,
        )
        X, eigs = nc.fit_transform(M)

        re = rel_error(X, eigs)
        max_rel.append(re.max().item())

        if _ % 100 == 0:
            print_re(re)
        # print_re(re0)

    # plt.hist(max_rel, bins=30)
    # plt.show()

    # plt.imshow(re0)
    # plt.colorbar()
    # plt.show()
    #
    # plt.scatter(torch.arange(n), torch.linalg.norm(X0, dim=-1))
    # plt.show()
    raise Exception()


    #
    # # plt.scatter(torch.arange(n), torch.linalg.norm(X0, dim=-1))
    # # plt.show()
    # # raise Exception()
    #
    # def align_to(X, eigs):
    #     sign = torch.sign(torch.sum(X0 * X, dim=0))
    #     return X * sign, eigs
    #
    # Xs = []
    # n_trials = 20
    # sum_X, sum_eigs = 0.0, 0.0
    # for _ in range(n_trials):
    #     nc = NCUT(n_components=n_components, num_sample=num_sample, distance=distance, eig_solver=eig_solver)
    #     X, eigs = align_to(*nc.fit_transform(M))
    #     Xs.append(X)
    #
    #     re = rel_error(X, eigs)
    #     print(f"max: {re.max().item()}, mean: {re.mean().item()}, min: {re.min().item()}")
    #
    #     # print(X[:3, :10])
    #     # print(eigs[:10])
    #
    #     sum_X = sum_X + X
    #     sum_eigs = sum_eigs + eigs
    #
    # # print(torch.diag(Xs[0].mT @ Xs[1]))
    # # raise Exception()
    #
    # print("=" * 120)
    # mean_X, mean_eigs = sum_X / n_trials, sum_eigs / n_trials
    # mean_re = rel_error(mean_X, mean_eigs)
    # print(f"max: {mean_re.max().item()}, mean: {mean_re.mean().item()}, min: {mean_re.min().item()}")
    #
    # raise Exception()



    ncs = [
        NCUT(n_components=n_components, num_sample=n, distance=distance, eig_solver=eig_solver),
        NCUT(n_components=n_components, num_sample=num_sample, distance=distance, eig_solver=eig_solver),
        # OldNCUT(num_eig=n_components, num_sample=num_sample, knn=10, distance=distance, eig_solver=eig_solver, make_orthogonal=True),
    ]

    for NC in ncs:
        torch.manual_seed(1212)
        np.random.seed(1212)
        X, eigs = NC.fit_transform(M)

        RE = rel_error(X, eigs)
        print(f"max: {RE.max().item()}, mean: {RE.mean().item()}, min: {RE.min().item()}")

    # torch.manual_seed(1212)
    # np.random.seed(1212)
    #
    # aX, R = axis_align(X)
    # print(aX[:3])
    # print(R)
    # print(R @ R.mT)




    # import time
    # n_trials = 10
    #
    # with torch.no_grad():
    #     start_t = time.perf_counter()
    #     for _ in range(n_trials):
    #         X, eigs = NC.fit_transform(M)
    #     end_t = time.perf_counter()
    #     print(X.min().item(), X.max().item(), eigs)
    #     print(f"{1e3 * (end_t - start_t) / n_trials}ms")
    #
    #     start_t = time.perf_counter()
    #     for _ in range(n_trials):
    #         nX, neigs = nNC.fit_transform(M)
    #     end_t = time.perf_counter()
    #     print(nX.min().item(), nX.max().item(), neigs)
    #     print(f"{1e3 * (end_t - start_t) / n_trials}ms")
    # raise Exception()

    # assert torch.all(torch.isclose(X, torch.Tensor([
    #     [0.320216, 0.144101, -0.110744, -0.560543, -0.007982],
    #     [0.297634, 0.662867, 0.146107, 0.277893, 0.553959],
    #     [0.324994, -0.057295, 0.052916, 0.391666, -0.460911],
    #     [0.301703, -0.460709, 0.528563, 0.222525, 0.325546],
    #     [0.316614, 0.043475, -0.526899, 0.100665, -0.030259],
    #     [0.325425, -0.127884, 0.294540, -0.012173, -0.303528],
    #     [0.318136, -0.288952, -0.065148, -0.470192, 0.244805],
    #     [0.309522, -0.352693, -0.473237, 0.234057, 0.276185],
    #     [0.320464, 0.229301, 0.281134, -0.308938, -0.169746],
    #     [0.326147, 0.213536, -0.112246, 0.155114, -0.341439]
    # ]), atol=1e-6)), "Failed assertion"

    # torch.manual_seed(1212)
    # np.random.seed(1212)
    # X_2d, rgb = rgb_from_umap_sphere(X)
    # # X_3d, rgb = rgb_from_cosine_tsne_3d(X)
    # print(rgb)
