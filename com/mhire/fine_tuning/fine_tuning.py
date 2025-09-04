import json
import os
import traceback
import logging

from datetime import datetime
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments
from com.mhire.utility.util import log_error
# Configure the logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)


class FineTuneModel():
    def __init__(self):
        pass
    # Function to load or download the model
    def load_local_model(self, local_model_path):
        model, tokenizer = '', ''
        if local_model_path != "":
            logger.info(f"Loading model from {local_model_path}")
            model = AutoModelForCausalLM.from_pretrained(local_model_path)
            tokenizer = AutoTokenizer.from_pretrained(local_model_path)
            
        return model, tokenizer

    # Function to prepare the dataset
    def tokenize_dataset(self,tokenizer, jsonl_file_path):
    
        def read_jsonl(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return [json.loads(line) for line in f]

        dataset = read_jsonl(jsonl_file_path)

        # Tokenize data
        def tokenize_function(examples):
            # Tokenize the input text (prompt)
            inputs = tokenizer(examples['prompt'], padding="max_length", truncation=True)
            # Tokenize the label (completion)
            labels = tokenizer(examples['completion'], padding="max_length", truncation=True)

            # Use input_ids as labels
            inputs['labels'] = labels['input_ids'].copy()
            return inputs

        # Tokenize Dataset (assuming jsonl has the fields)
        tokenized_dataset = list(map(tokenize_function, dataset))
        return tokenized_dataset

    # Main function to fine-tune the model
    def fine_tune_model(self, model_local_path,  dataset_path):
        model, tokenizer = self.load_local_model(local_model_path=model_local_path)
        dataset = self.tokenize_dataset(tokenizer, dataset_path)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_model_path = f"{model_local_path}/finetuned_{timestamp}/"
        logger.info(f"After Training model will be saved at {output_model_path}")
        training_args = TrainingArguments(
            output_dir=output_model_path,
            #overwrite_output_dir=True,
            per_device_train_batch_size=1,
            num_train_epochs=1,
            logging_dir='./logs',
            logging_steps=1,
            #save_steps=10_000,
            #save_total_limit = 2
        )
        
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=dataset,
        )

        try:
            os.makedirs(output_model_path, exist_ok=True)
            logger.info(f"Training started")
            trainer.train()
            logger.info(f"Dir {output_model_path} created")
            model.save_pretrained(output_model_path)
            logger.info(f"Model saved after fine tuning")
            trainer.save_model(output_model_path)
            logger.info(f"Training saved")
            tokenizer.save_pretrained(output_model_path)
            logger.info(f"Tokenizer saved to {output_model_path}")
            
        except Exception as e:
            logger.info(traceback.format_exc())
            log_error(f"Training failed: {str(e)}")

