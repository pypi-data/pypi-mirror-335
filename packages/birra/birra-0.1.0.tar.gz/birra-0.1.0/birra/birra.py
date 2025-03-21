import numpy as np
from scipy.stats import rankdata
from pysmooth import smooth
import pandas as pd
import argparse


def birra(data, prior=0.05, n_bins=50, n_iter=10, return_all=False, cor_stop=1):
    if not isinstance(data, np.ndarray) or data.ndim != 2:
        raise ValueError("data must be a 2D numpy array")

    n_genes, n_datasets = data.shape
    prior_or = prior / (1 - prior)
    n_pos = int(np.floor(n_genes * prior))
    data_normalized = data / n_genes

    bayes_factors = np.zeros((n_bins, n_datasets))
    binned_data = np.ceil(data_normalized * n_bins).astype(int)
    # Ensure bins are within [1, n_bins]
    np.clip(binned_data, 1, n_bins, out=binned_data)

    agg_ranks = np.mean(data_normalized, axis=1)

    for iter in range(n_iter):
        prev_agg_ranks = agg_ranks.copy()

        ranks = rankdata(agg_ranks, method="min")  # min rank for ties
        pos_mask = ranks <= n_pos
        neg_mask = ~pos_mask

        # Compute Bayes factors for each bin and dataset
        for i in range(n_datasets):
            for j in range(1, n_bins + 1):
                current_bins = binned_data[:, i] <= j
                tpr = np.sum(pos_mask[current_bins])
                fpr = np.sum(neg_mask[current_bins])
                bayes_factors[j - 1, i] = np.log(
                    (tpr + 1) / (fpr + 1) / prior_or
                )

        # Apply smoothing and reverse cummax to each column
        for i in range(n_datasets):
            col = bayes_factors[:, i].copy()
            smoothed = smooth(
                x=col, kind="3RS3R", twiceit=False, endrule="Tukey"
            )
            rev_cummax = np.maximum.accumulate(smoothed[::-1])[::-1]
            bayes_factors[:, i] = rev_cummax

        # Adjust the highest BF in each bin to the second highest
        if n_datasets >= 2:
            for bin_row in range(n_bins):
                row_data = bayes_factors[bin_row, :]
                sorted_indices = np.argsort(-row_data)
                if len(sorted_indices) >= 2:
                    first_idx = sorted_indices[0]
                    second_idx = sorted_indices[1]
                    bayes_factors[bin_row, first_idx] = row_data[second_idx]

        flat_bins = binned_data.ravel(order="F")
        dataset_indices = np.repeat(np.arange(n_datasets), n_genes)
        selected_bf = bayes_factors[flat_bins - 1, dataset_indices]
        bayes_data = selected_bf.reshape(n_datasets, n_genes).T

        row_sums = np.sum(bayes_data, axis=1)
        agg_ranks = rankdata(-row_sums, method="average")

        if cor_stop is not None and not np.isnan(cor_stop):
            cprev = np.corrcoef(agg_ranks, prev_agg_ranks)[0, 1]
            if cprev >= cor_stop - 1e-15:
                print("Converged")
                break

    if return_all:
        return {"result": agg_ranks, "data": bayes_data, "BF": bayes_factors}
    else:
        return agg_ranks


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    ranked_effects = pd.read_csv(args.input)

    data_matrix = ranked_effects.values.astype(float)

    result = birra(
        data=data_matrix, prior=0.05, n_bins=50, n_iter=10, return_all=False
    )

    pd.DataFrame({"aggregate_rank": result}).to_csv(args.output, index=False)
