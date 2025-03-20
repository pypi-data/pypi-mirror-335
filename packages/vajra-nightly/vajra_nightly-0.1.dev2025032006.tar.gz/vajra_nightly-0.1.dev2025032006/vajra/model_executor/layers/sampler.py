"""A layer that samples the next tokens from the model's outputs."""

from typing import List, Tuple

import flashinfer
import torch
import torch.nn as nn

from vajra.datatypes import SequenceMetadata  # type: ignore
from vajra.datatypes import SamplerOutput, SamplerOutputs, Sequence  # type: ignore
from vajra.model_executor.parallel_utils import gather_from_tensor_model_parallel_region

_SAMPLING_EPS = 1e-5
_MAX_TOP_K_ROUND = 32


class Sampler(nn.Module):
    """Samples the next tokens from the model's outputs.

    This layer does the following:
    1. Discard the hidden states that are not used for sampling (i.e., all
        tokens except the final one in each prompt).
    2. Compute the logits for the next tokens.
    3. Apply presence and frequency penalties.
    4. Apply temperature scaling.
    5. Apply top-p and top-k truncation.
    6. Sample the next tokens.
    Here, each sequence group within the batch can have different sampling
    parameters (e.g., sampling method, temperature, top-p, top-k, etc.).
    """

    def __init__(self, embedding: torch.Tensor, vocab_size: int) -> None:
        super().__init__()
        self.embedding = embedding
        self.vocab_size = vocab_size

    def forward(
        self,
        logits: torch.Tensor,
        seqs: List[Sequence],
        seq_metadata_list: List[SequenceMetadata],
    ) -> SamplerOutputs:
        # Get the hidden states that we use for sampling.
        logits = _prune_hidden_states(logits, seq_metadata_list)

        # Get the logits for the next tokens.
        logits = _get_logits(logits, self.embedding, self.vocab_size)

        # Apply temperature scaling.
        temperatures = _get_temperatures(seqs)
        if any(t != 1.0 for t in temperatures):
            t = torch.tensor(temperatures, dtype=logits.dtype, device=logits.device)
            # Use in-place division to avoid creating a new tensor.
            logits.div_(t.unsqueeze(dim=1))

        # Apply top-p and top-k truncation.
        top_ps, top_ks = _get_top_p_top_k(seqs, self.vocab_size)
        assert len(top_ps) == len(top_ks) == logits.shape[0]

        # Sample the next tokens.
        return _sample(logits, top_ks, top_ps, seq_metadata_list)


def _get_logits(
    hidden_states: torch.Tensor, embedding: torch.Tensor, vocab_size: int
) -> torch.Tensor:
    # Get the logits for the next tokens.
    logits = torch.matmul(hidden_states, embedding.t())
    # Start async gather without waiting
    logits = gather_from_tensor_model_parallel_region(logits)
    logits = logits[:, :vocab_size]
    return logits


def _prune_hidden_states(
    hidden_states: torch.Tensor,
    seq_metadata_list: List[SequenceMetadata],
) -> torch.Tensor:
    last_token_indices = []
    token_idx = 0
    for seq_metadata in seq_metadata_list:
        num_q_tokens = seq_metadata.num_q_tokens
        last_token_indices.append(token_idx + num_q_tokens - 1)
        token_idx += num_q_tokens

    last_token_indices_tensor = torch.tensor(
        last_token_indices, dtype=torch.long, device=hidden_states.device
    )
    return hidden_states.index_select(0, last_token_indices_tensor)


def _get_temperatures(seqs: List[Sequence]) -> List[float]:
    # Collect the temperatures for the logits.
    temperatures: List[float] = []
    for seq in seqs:
        temperature = seq.sampling_params.temperature
        if temperature < _SAMPLING_EPS:
            # NOTE: Zero temperature means deterministic sampling
            # (i.e., greedy sampling or beam search).
            # Set the temperature to 1 to avoid division by zero.
            temperature = 1.0
        temperatures.append(temperature)
    return temperatures


def _get_top_p_top_k(
    seqs: List[Sequence],
    vocab_size: int,
) -> Tuple[List[float], List[int]]:
    top_ps: List[float] = []
    top_ks: List[int] = []
    for seq in seqs:
        top_p = seq.sampling_params.top_p
        # k should not be greater than the vocab size.
        top_k = min(seq.sampling_params.top_k, vocab_size)
        # k=-1 means no truncation.
        top_k = vocab_size if top_k == -1 else top_k
        top_ps.append(top_p)
        top_ks.append(top_k)
    return top_ps, top_ks


def _sample(
    logits: torch.Tensor,
    top_ks: List[int],
    top_ps: List[float],
    seq_metadata_list: List[SequenceMetadata],
) -> SamplerOutputs:
    k = torch.tensor(top_ks, dtype=torch.int, device=logits.device)
    p = torch.tensor(top_ps, dtype=torch.float32, device=logits.device)
    sample_results = flashinfer.sampling.top_k_top_p_sampling_from_logits(logits, k, p)
    sample_results_list = sample_results.cpu().tolist()

    outputs: SamplerOutputs = []

    for seq_idx, sample_result in enumerate(sample_results_list):
        seq_id = seq_metadata_list[seq_idx].seq_id
        schedule_id = seq_metadata_list[seq_idx].schedule_id
        outputs.append(SamplerOutput(schedule_id, seq_id, (sample_result,)))

    return outputs
