from torch import Tensor


class Query(Tensor):
    """
    Query tensor for attention mechanisms.

    Shape: (batch_size, n_head, seq_len_q, d_k)
    - n_head: Number of attention heads
    - seq_len_q: Query sequence length
    - d_k: Dimension of keys/queries (usually d_model // n_head)
    """


class Key(Tensor):
    """
    Key tensor for attention mechanisms.

    Shape: (batch_size, n_head, seq_len_k, d_k)
    - n_head: Number of attention heads
    - seq_len_k: Key sequence length
    - d_k: Dimension of keys/queries (usually d_model // n_head)
    """


class Value(Tensor):
    """
    Value tensor for attention mechanisms.

    Shape: (batch_size, n_head, seq_len_v, d_v)
    - n_head: Number of attention heads
    - seq_len_v: Value sequence length (usually same as seq_len_k)
    - d_v: Dimension of values (usually d_model // n_head)
    """


class Attn(Tensor):
    """
    Attention weights tensor.

    Shape: (batch_size, n_head, seq_len_q, seq_len_k)
    - n_head: Number of attention heads
    - seq_len_q: Query sequence length
    - seq_len_k: Key sequence length
    """


class QueriedValue(Tensor):
    """
    Output tensor after applying attention weights to values.

    Shape: (batch_size, n_head, seq_len_q, d_v)
    - n_head: Number of attention heads
    - seq_len_q: Query sequence length
    - d_v: Dimension of values
    """
