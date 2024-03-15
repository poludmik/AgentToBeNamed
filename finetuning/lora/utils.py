from transformers.integrations import WandbCallback
import pandas as pd
from agenttobenamed.logger import *
import yaml

def decode_predictions(tokenizer, predictions):
    labels = tokenizer.batch_decode(predictions.label_ids)
    logits = predictions.predictions.argmax(axis=-1)
    prediction_text = tokenizer.batch_decode(logits)
    return {"labels": labels, "predictions": prediction_text}

class WandbPredictionProgressCallback(WandbCallback):
    """Custom WandbCallback to log model predictions during training.

    This callback logs model predictions and labels to a wandb.Table at each
    logging step during training. It allows to visualize the
    model predictions as the training progresses.

    Attributes:
        trainer (Trainer): The Hugging Face Trainer instance.
        tokenizer (AutoTokenizer): The tokenizer associated with the model.
        sample_dataset (Dataset): A subset of the validation dataset
          for generating predictions.
        num_samples (int, optional): Number of samples to select from
          the validation dataset for generating predictions. Defaults to 100.
        freq (int, optional): Frequency of logging. Defaults to 2.
    """
    def __init__(self, trainer, tokenizer, val_dataset,
                 num_samples=100, freq=1):
        """Initializes the WandbPredictionProgressCallback instance.

        Args:
            trainer (Trainer): The Hugging Face Trainer instance.
            tokenizer (AutoTokenizer): The tokenizer associated
              with the model.
            val_dataset (Dataset): The validation dataset.
            num_samples (int, optional): Number of samples to select from
              the validation dataset for generating predictions.
              Defaults to 100.
            freq (int, optional): Frequency of logging. Defaults to 2.
        """
        super().__init__()
        self.trainer = trainer
        self.tokenizer = tokenizer
        self.sample_dataset = val_dataset
        self.sample_dataset = self.sample_dataset.remove_columns("label")

    def on_evaluate(self, args, state, control, **kwargs):
        super().on_evaluate(args, state, control, **kwargs)
        # control the frequency of logging by logging the predictions
        # every `freq` epochs
        print(f"\nEpoch callback:", state.epoch)

        print(self.sample_dataset)

        predictions = self.trainer.predict(self.sample_dataset)
        # decode predictions and labels
        predictions = decode_predictions(self.tokenizer, predictions)
        # add predictions to a wandb.Table
        predictions_df = pd.DataFrame(predictions)
        print(predictions_df.head())
        predictions_df["epoch"] = state.epoch
        records_table = self._wandb.Table(dataframe=predictions_df)
        # log the table to wandb
        self._wandb.log({"sample_predictions": records_table})
        print(f"\nEpoch {state.epoch} completed. Logged predictions to W&B.")

def print_trainable_parameters(m):
    """
    Prints the number of trainable parameters in the model.
    """
    trainable_params = 0
    all_param = 0
    for _, param in m.named_parameters():
        all_param += param.numel()
        if param.requires_grad:
            trainable_params += param.numel()
    print(
        f"Trainable params: {YELLOW}{trainable_params}{RESET} || all params: {BLUE}{all_param}{RESET} || trainable: {YELLOW}{round(100 * trainable_params / all_param, 4)}{RESET}%"
    )


eos_token = "</s>"

def formatting_func(prompt):
    return prompt["text"]
    # output = []
    # for d, s in zip(prompt["input"], prompt["output"]):
    #     op = f"{d}# Code:\n    {s}{eos_token}"
    #     output.append(op)
    # return output


class DotDict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, dct):
        for key, value in dct.items():
            if hasattr(value, 'keys'):
                value = DotDict(value)
            self[key] = value

def load_config(yaml_file_path):
    with open(yaml_file_path, 'r') as file:
        return yaml.safe_load(file)