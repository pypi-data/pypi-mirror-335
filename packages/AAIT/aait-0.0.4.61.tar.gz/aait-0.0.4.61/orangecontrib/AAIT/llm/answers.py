import copy
import os
import GPUtil
import psutil
import ntpath

from gpt4all import GPT4All
from Orange.data import Domain, StringVariable, Table


if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.llm import prompt_management
else:
    from orangecontrib.AAIT.llm import prompt_management


def check_gpu(model_path, argself):
    """
    Checks if the GPU has enough VRAM to load a model.

    Args:
        model_path (str): Path to the model file.
        argself (OWWidget): OWQueryLLM object.

    Returns:
        bool: True if the model can be loaded on the GPU, False otherwise.
    """
    argself.error("")
    argself.warning("")
    argself.information("")
    argself.can_run = True
    token_weight = 0.13
    if model_path is None:
        argself.use_gpu = False
        return
    if not model_path.endswith(".gguf"):
        argself.use_gpu = False
        argself.can_run = False
        argself.error("Model is not compatible. It must be a .gguf format.")
        return
    # Calculate the model size in MB with a 1500 MB buffer
    model_size = os.path.getsize(model_path) / (1024 ** 3) * 1000
    model_size += token_weight * int(argself.n_ctx)
    # If there is no GPU, set use_gpu to False
    if len(GPUtil.getGPUs()) == 0:
        argself.use_gpu = False
        argself.information("Running on CPU. No GPU detected.")
        return
    # Else
    else:
        # Get the available VRAM on the first GPU
        gpu = GPUtil.getGPUs()[0]
        free_vram = gpu.memoryFree
    # If there is not enough VRAM on GPU
    if free_vram < model_size:
        # Set use_gpu to False
        argself.use_gpu = False
        # Check for available RAM
        available_ram = psutil.virtual_memory().available / 1024 / 1024
        if available_ram < model_size:
            argself.can_run = False
            argself.error(f"Cannot run. Both GPU and CPU are too small for this model (required: {model_size / 1000:.2f}GB).")
            return
        else:
            argself.warning(f"Running on CPU. GPU seems to be too small for this model (available: {free_vram/1000:.2f}GB || required: {model_size/1000:.2f}GB).")
            return
    # If there is enough space on GPU
    else:
        try:
            # Load the model and test it
            # model = GPT4All(model_name=model_path, model_path=model_path, n_ctx=int(argself.n_ctx),
            #                 allow_download=False, device="cuda")
            # answer = model.generate("What if ?", max_tokens=3)
            # # If it works, set use_gpu to True
            argself.use_gpu = True
            argself.information("Running on GPU.")
            return
        # If importing Llama and reading the model doesn't work
        except Exception as e:
            # Set use_gpu to False
            argself.use_gpu = False
            argself.warning(f"GPU cannot be used. (detail: {e})")
            return


def generate_answers(table, model_path, use_gpu=False, n_ctx=4096, progress_callback=None, argself=None):
    """
    open a model base on llama/gpy4all api
    return input datatable + answer column
    """
    if table is None:
        return

    # Copy of input data
    data = copy.deepcopy(table)
    attr_dom = list(data.domain.attributes)
    metas_dom = list(data.domain.metas)
    class_dom = list(data.domain.class_vars)

    # Load model
    if os.path.exists(model_path):
        if use_gpu:
            model = GPT4All(model_name=model_path, model_path=model_path, n_ctx=n_ctx,
                            allow_download=False, device="cuda")
        else:
            model = GPT4All(model_name=model_path, model_path=model_path, n_ctx=n_ctx,
                            allow_download=False)
    else:
        print(f"Model could not be found: {model_path} does not exist")
        return

    # Generate answers on column named "prompt"
    try:
        rows = []
        for i, row in enumerate(data):
            features = list(data[i])
            metas = list(data.metas[i])
            prompt = row["prompt"].value

            system_prompt = row["system prompt"].value if "system prompt" in data.domain else ""
            assistant_prompt = row["assistant prompt"].value if "assistant prompt" in data.domain else ""

            prompt = prompt_management.apply_prompt_template(model_path, user_prompt=prompt, assistant_prompt=assistant_prompt, system_prompt=system_prompt)
            answer = run_query(prompt, model=model, argself=argself, progress_callback=progress_callback)
            if answer == "":
                answer = f"Error: The answer could not be generated. The model architecture you tried to use it most likely not supported yet.\n\nModel name: {ntpath.basename(model_path)}"
            metas += [answer]
            rows.append(features + metas)
            if progress_callback is not None:
                progress_value = float(100 * (i + 1) / len(data))
                progress_callback((progress_value, "\n\n\n\n"))
            if argself is not None:
                if argself.stop:
                    break
    except ValueError as e:
        print("An error occurred when trying to generate an answer:", e)
        return


    # Generate new Domain to add to data
    answer_dom = [StringVariable("Answer")]

    # Create and return table
    domain = Domain(attributes=attr_dom, metas=metas_dom + answer_dom, class_vars=class_dom)
    out_data = Table.from_list(domain=domain, rows=rows)
    return out_data


class StopCallback:
    def __init__(self, stop_sequences):
        self.stop_sequences = stop_sequences
        self.recent_tokens = ""
        self.returning = True  # Store the last valid token before stopping

    def __call__(self, token_id, token):
        if not self.returning:
            return False
        self.recent_tokens += token

        # Check if any stop sequence appears
        for stop_seq in self.stop_sequences:
            if stop_seq in self.recent_tokens:
                self.returning = False  # Stop the generation, but allow the last token

        return True  # Continue generation


def run_query(prompt, model, max_tokens=4096, temperature=0, top_p=0, top_k=40, repeat_penalty=1.15,
              argself=None, progress_callback=None):
    stop_sequences = ["<|endoftext|>", "### User", "<|im_end|>", "<|im_start|>", "<|im_end>", "<im_end|>", "<im_end>"]
    callback_instance = StopCallback(stop_sequences)

    answer = ""
    for token in model.generate(prompt=prompt, max_tokens=max_tokens, temp=temperature, top_p=top_p, top_k=top_k,
                                repeat_penalty=repeat_penalty, streaming=True, callback=callback_instance):
        answer += token
        if progress_callback is not None:
            progress_callback((None, token))
        if argself is not None and argself.stop:
            return answer

    # Remove stop sequences from the final answer
    for stop in stop_sequences:
        answer = answer.replace(stop, "")

    return answer
