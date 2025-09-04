# Llama Model Fine-Tuning & Deployment Utility

This repository provides a complete workflow for fine-tuning, quantizing, and deploying Llama-based large language models (LLMs) using Docker, and Google Cloud Platform (GCP). It is designed for scalable, cloud-based training and efficient model serving.

## Features

- **Fine-tuning**: Easily fine-tune Llama models on your custom datasets using Hugging Face Transformers and TorchTune.
- **Quantization**: Compress and optimize your fine-tuned models for fast, resource-efficient inference.
- **Cloud Integration**: Automate data/model transfer and deployment with GCP (VM metadata, storage, and Artifact Registry).
- **Dockerized Workflow**: Build, tag, and push Docker images for both training and inference.
- **Ollama Support**: Serve quantized models using Ollama for API-based inference.

## Project Structure

```
.
├── com/
│   ├── mhire/
│   │   ├── fine_tuning/
│   │   │   ├── fine_tuning.py         # Fine-tuning logic
│   │   │   └── quantize.py            # Model quantization
│   │   ├── startup_fine_tuning.py     # Orchestrates the workflow
│   │   └── utility/                   # GCP, Docker, logging utilities
├── config.yaml                        # Training configuration
├── requirements.txt                   # Python dependencies
├── Dockerfile                         # Training Docker image
├── Modelfile                          # Ollama model config
├── ollama_docker/
│   └── Dockerfile                     # Ollama inference Docker image
├── start_up_script/
│   ├── start_training_docker          # VM startup script for training
│   └── start_up_script_llm_inference.sh # VM startup script for inference
└── entrypoint.sh                      # Entrypoint for Docker container
```

## Workflow Overview

### 1. Build & Deploy Training Docker Image

1. Build the Docker image:
  ```sh
  docker build -t <your-registry>/repo-name:latest .
  ```
2. Push the image to your registry:
  ```sh
  docker push <your-registry>/repo-name:latest
  ```

### 2. Fine-Tune the Model

- Launch a VM and run the training startup script (`start_training_docker`).
- The script will:
  - Download the base model and dataset from GCP storage
  - Fine-tune the model using your configuration
  - Save and optionally zip the fine-tuned model
  - Upload results/logs to GCP storage

### 3. Quantize the Model

- Run `quantize.py` to quantize the fine-tuned model for efficient inference.
- The quantized model will be saved as `model_file.gguf`.

### 4. Prepare Inference Docker Image

- Place `Modelfile`, `Dockerfile`, and `model_file.gguf` in the inference directory (e.g., `ollama_docker/`).
- Build and push the inference Docker image as above.

### 5. Deploy for Inference

- Use `start_up_script_llm_inference.sh` to launch the inference container and expose the API endpoint.
- Integrate with your application as needed.

## Requirements

- Python 3.8+
- Docker
- GCP account (for cloud automation)
- Sufficient GPU resources for training

## Customization

- Update `config.yaml` for your model, dataset, and training parameters.
- Replace dataset/model paths with your own in the startup scripts and configs.

## License

This project is open-source and intended for research and production use. Please review the LICENSE file for details.