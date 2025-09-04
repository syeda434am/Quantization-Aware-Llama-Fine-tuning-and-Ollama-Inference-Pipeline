from transformers import AutoModelForCausalLM, AutoTokenizer
from optimum.gptq import GPTQQuantizer, load_quantized_model
import torch
from accelerate import init_empty_weights

def quantize():
    # Load model and tokenizer
    model_name = f"/llm/fine_tuned_model_files"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16)

    # Initialize the GPTQ quantizer
    quantizer = GPTQQuantizer(
        bits=4,
        dataset="c4",
        block_name_to_quantize="model.decoder.layers",
        model_seqlen=2048
    )

    # Quantize the model
    quantized_model = quantizer.quantize_model(model, tokenizer)

    # Save the quantized model
    save_folder = "/llm/model_file.gguf"
    quantizer.save(model, save_folder)

    # Load the quantized model
    with init_empty_weights():
        empty_model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16)
    empty_model.tie_weights()
    quantized_model = load_quantized_model(empty_model, save_folder=save_folder, device_map="auto")
