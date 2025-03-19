import torch
import torch.jit
import huggingface_hub
import os
from enum import Enum
from pathlib import Path

class MODELS(Enum):
    TUCARC3D = 'TUC-AR-C3D'

class WEIGHTS(Enum):
    TUCAR = 'tuc-ar.pth'
    UCF101 = 'ufc101.pth'
    NTURGB_CS = 'ntu-rgb_cs.pth'

#__example__ #import rsp.ml.model as model
#__example__
#__example__ action_recognition_model = model.load_model(MODEL.TUCARC3D, WEIGHTS.TUCAR)
def load_model(
        model:MODELS,
        weights:WEIGHTS
    ) -> torch.nn.Module:
    """
    Loads a pretrained PyTorch model from HuggingFace.

    Parameters
    ----------
    model : MODELS
        ID of the model
    weights : WEIGHTS
        ID of the weights

    Returns
    -------
    torch.nn.Module
        Pretrained PyTorch model
    """
    if isinstance(model, MODELS):
        model = model.value
    if isinstance(weights, WEIGHTS):
        weights = weights.value

    api = huggingface_hub.HfApi()
    model_path = api.hf_hub_download(f'SchulzR97/{model}', filename=weights)

    model = torch.jit.load(model_path)

    return model

def publish_model(
        model:torch.nn.Module,
        model_id:str,
        weights_id:str,
        repos_dir:str = 'repos',
        token:str = None
    ):
    if token is not None:
        os.environ["HUGGINGFACEHUB_API_TOKEN"] = token
        huggingface_hub.login(token)
    repos_dir = Path(repos_dir)
    model_dir = repos_dir.joinpath(model_id)
    model_dir.mkdir(exist_ok=True, parents=True)
    weights_path = model_dir.joinpath(weights_id)

    repo = huggingface_hub.Repository(local_dir=model_dir, clone_from=f'SchulzR97/{model_id}')

    scripted_model = torch.jit.script(model)
    scripted_model.save(weights_path)

    repo.push_to_hub()


#__example__ #import rsp.ml.model as model
#__example__
#__example__ model_weight_files = model.list_model_weights()
def list_model_weights():
    """
    Lists all available weight files.

    Returns
    -------
    List[Tuple(str, str)]
        List of (MODEL:str, WEIGHT:str)
    """
    weight_files = []
    username = 'SchulzR97'
    for model in huggingface_hub.list_models(author=username):
        for file in huggingface_hub.list_repo_files(model.id):
            appendix = file.split('.')[-1]
            if appendix not in ['bin', 'pt', 'pth']:
                continue
            model_id = model.id.replace(f'{username}/', '')
            weight_id = file
            weight_files.append((model_id, weight_id))
            print(weight_files[-1])
    return weight_files

if __name__ == '__main__':
    model = torch.nn.Linear(1, 2)
    publish_model(model, MODELS.TUCARC3D.value, 'test.pth')

    list_model_weights()

    model = load_model(MODELS.TUCARC3D, WEIGHTS.TUCAR)