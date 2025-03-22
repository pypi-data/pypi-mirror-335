from ..default_models import ModelConfig, get_all_model_configs
from ..model_quality import QualityMetricsCollection, MMLU, MATH, GSM8K,  IFEval,  GPQA, Hellaswag, TLDR, TriviaQA, BIG_Bench

##### Mistral Models ########
# https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2/blob/main/config.json
mistral_7b_config = ModelConfig(model='mistralai/Mistral-7B',
    hidden_size=4096, num_attention_heads=32,
    num_key_value_heads=8, num_ffi = 2,
    intermediate_size=14336, num_decoder_layers=32,
    vocab_size=32000, max_model_len=32*1024, hidden_act="silu",
    model_quality=QualityMetricsCollection([MMLU(accuracy=62.5), Hellaswag(accuracy=81.0), GSM8K(accuracy=50.0), MATH(accuracy=12.7), TriviaQA(accuracy=62.5)]),
)
# https://huggingface.co/mistralai/Mixtral-8x7B-Instruct-v0.1/blob/main/config.json
mixtral_8x7b_config = ModelConfig(model='mistralai/Mixtral-8x7B',
    hidden_size=4096, num_attention_heads=32,
    num_key_value_heads=8, num_ffi = 2,
    intermediate_size=14336, num_decoder_layers=32,
    expert_top_k=2, num_experts=8,
    vocab_size=32000, max_model_len=32*1024, hidden_act="silu",
    model_quality=QualityMetricsCollection([MMLU(accuracy=70.6), Hellaswag(accuracy=84.4), GSM8K(accuracy=74.4), MATH(accuracy=28.4), TriviaQA(accuracy=71.5)]),
)


# https://huggingface.co/mistralai/Ministral-8B-Instruct-2410/blob/main/config.json
ministral_8b_config = ModelConfig(model='mistralai/Ministral-8B-Instruct-2410',
    hidden_size=4096, num_attention_heads=32,
    num_key_value_heads=8, num_ffi = 2,
    intermediate_size=12288, num_decoder_layers=36,
    vocab_size=131072, max_model_len=32*1024, hidden_act="silu",
    sliding_window=32*1024,
    model_quality=QualityMetricsCollection([MMLU(accuracy=65.0), GSM8K(accuracy=64.5), MATH(accuracy=54.5), TriviaQA(accuracy=65.5)]),
)

# https://huggingface.co/mistralai/Mistral-Nemo-Base-2407/blob/main/config.json
mistral_nemo_12b_config = ModelConfig(model='mistralai/Mistral-NeMo-12B-Instruct',
    hidden_size=5120, num_attention_heads=32,
    num_key_value_heads=8, num_ffi = 2,
    intermediate_size=14336, num_decoder_layers=40,
    vocab_size=131072, max_model_len=1024000, hidden_act="silu",
    model_quality=QualityMetricsCollection([MMLU(accuracy=68.0, shots=5), Hellaswag(accuracy=83.5, shots=0), TriviaQA(accuracy=73.8, shots=5)]),

)

# https://huggingface.co/mistralai/Mixtral-8x22B-Instruct-v0.1/blob/main/config.json
mixtral_8x22b_config = ModelConfig(model='mistralai/Mixtral-8x22B',
    hidden_size=6144, num_attention_heads=48,
    num_key_value_heads=8, num_ffi = 2,
    intermediate_size=16384, num_decoder_layers=56,
    expert_top_k=2, num_experts=8,
    vocab_size=32768, max_model_len=64*1024, hidden_act="silu",
    model_quality=QualityMetricsCollection([MMLU(accuracy=77.8), Hellaswag(accuracy=88.5), GSM8K(accuracy=88.4), MATH(accuracy=41.8), TriviaQA(accuracy=82.2)]),

)

# https://huggingface.co/mistralai/Mistral-Small-Instruct-2409/blob/main/config.json
mistral_small_config = ModelConfig(model='mistralai/Mistral-Small',
    hidden_size=6144, num_attention_heads=48,
    num_key_value_heads=8, num_ffi = 2,
    intermediate_size=16384, num_decoder_layers=56,
    vocab_size=32768, max_model_len=32*1024, hidden_act="silu",
)

# https://huggingface.co/mistralai/Mistral-Large-Instruct-2407/blob/main/config.json
mistral_large_config = ModelConfig(model='mistralai/Mistral-Large',
    hidden_size=12288, num_attention_heads=96,
    num_key_value_heads=8, num_ffi = 2,
    intermediate_size=28672, num_decoder_layers=88,
    vocab_size=32768, max_model_len=128*1024, hidden_act="silu",
    model_quality=QualityMetricsCollection([MMLU(accuracy=81.2), Hellaswag(accuracy=89.2), GSM8K(accuracy=91.21, shots=8), MATH(accuracy=45.0), TriviaQA(accuracy=82.7)]),

)


# ##### Embedding Models ########
# https://huggingface.co/intfloat/e5-mistral-7b-instruct/blob/main/config.json
e5_mistral_7b_config = ModelConfig(model='intfloat/e5-mistral-7b-instruct',
    hidden_size=4096, num_attention_heads=32,
    num_key_value_heads=8, num_ffi = 2,
    intermediate_size=14336, num_decoder_layers=32,
    vocab_size=32000, max_model_len=32*1024, hidden_act="silu",
)
mistral_models = get_all_model_configs(__name__)
mistral_models.update(
    {
    'mistral_7b': mistral_7b_config,
    'mistralai/Ministral-8B': ministral_8b_config,
    'mistralai/mistral-7b': mistral_7b_config,
    'mistralai/mixtral-8x7b': mixtral_8x7b_config,
    'mixtral_8x7b': mixtral_8x7b_config,
    'e5_mistral_7b': mistral_7b_config,
    })