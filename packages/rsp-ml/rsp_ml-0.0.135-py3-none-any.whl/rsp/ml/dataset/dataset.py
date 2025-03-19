import urllib.request
from torch.utils.data import Dataset, DataLoader
from torch.utils.data.sampler import Sampler
from pathlib import Path
from platformdirs import user_cache_dir
from tqdm import tqdm
from glob import glob
from threading import Thread
from huggingface_hub import hf_hub_download, list_repo_files
import xml.etree.ElementTree as ET
import numpy as np
import os
import json
import pkg_resources
import urllib
import tarfile
import cv2 as cv
import csv
import torch
import rsp.ml.multi_transforms.multi_transforms as multi_transforms
import time
import pandas as pd
import gdown
import shutil
import zipfile

try:
    import rsp.common.console as console
except Exception as e:
    print(e)

#__example__ from rsp.ml.dataset import TUCRID
#__example__ from rsp.ml.dataset import ReplaceBackgroundRGBD
#__example__ import rsp.ml.multi_transforms as multi_transforms
#__example__ import cv2 as cv
#__example__
#__example__ backgrounds = TUCRID.load_backgrounds_color()
#__example__ transforms = multi_transforms.Compose([
#__example__     ReplaceBackgroundRGBD(backgrounds),
#__example__     multi_transforms.Stack()
#__example__ ])
#__example__ 
#__example__ ds = TUCRID('train', transforms=transforms)
#__example__ 
#__example__ for X, T in ds:
#__example__   for x in X.permute(0, 2, 3, 1):
#__example__     img_color = x[:, :, :3].numpy()
#__example__     img_depth = x[:, :, 3].numpy()
#__example__ 
#__example__     cv.imshow('color', img_color)
#__example__     cv.imshow('depth', img_depth)
#__example__ 
#__example__     cv.waitKey(30)
class TUCRID(Dataset):
    """
    Dataset class for the Robot Interaction Dataset by University of Technology Chemnitz (TUCRID).
    """
    REPO_ID = 'SchulzR97/TUCRID'
    CACHE_DIRECTORY = Path(user_cache_dir('rsp-ml', 'Robert Schulz')).joinpath('dataset', 'TUCRID')
    COLOR_DIRECTORY = CACHE_DIRECTORY.joinpath('color')
    DEPTH_DIRECTORY = CACHE_DIRECTORY.joinpath('depth')
    BACKGROUND_DIRECTORY = CACHE_DIRECTORY.joinpath('background')
    PHASES = ['train', 'val']

    def __init__(
            self,
            phase:str,
            load_depth_data:bool = True,
            sequence_length:int = 30,
            num_classes:int = 10,
            transforms:multi_transforms.Compose = multi_transforms.Compose([]),
            cache_dir:str = None
    ):
        """
        Initializes a new instance.

        Parameters
        ----------
        phase : str
            Dataset phase [train|val]
        load_depth_data : bool, default = True
            Load depth data
        sequence_length : int, default = 30
            Length of the sequences
        num_classes : int, default = 10
            Number of classes
        transforms : rsp.ml.multi_transforms.Compose = default = rsp.ml.multi_transforms.Compose([])
            Transformations, that will be applied to each input sequence. See documentation of `rsp.ml.multi_transforms` for more details.
        """
        assert phase in TUCRID.PHASES, f'Phase "{phase}" not in {TUCRID.PHASES}'

        if cache_dir is not None:
            TUCRID.CACHE_DIRECTORY = Path(cache_dir)
            TUCRID.COLOR_DIRECTORY = TUCRID.CACHE_DIRECTORY.joinpath('color')
            TUCRID.DEPTH_DIRECTORY = TUCRID.CACHE_DIRECTORY.joinpath('depth')
            TUCRID.BACKGROUND_DIRECTORY = TUCRID.CACHE_DIRECTORY.joinpath('background')

        self.phase = phase
        self.load_depth_data = load_depth_data
        self.sequence_length = sequence_length
        self.num_classes = num_classes
        self.transforms = transforms

        self.__download__()
        self.__load__()
        pass

    def __len__(self):
        return len(self.sequences)
    
    def __getitem__(self, idx):
        id = self.sequences['id'][idx]
        action = self.sequences['action'][idx]
        link = self.sequences['link'][idx]

        color_files = sorted(glob(f'{TUCRID.COLOR_DIRECTORY}/{link}/*.jpg'))
        assert len(color_files) >= self.sequence_length, f'Not enough frames for {id}.'

        if len(color_files) > self.sequence_length:
            start_idx = np.random.randint(0, len(color_files) - self.sequence_length)
            end_idx = start_idx + self.sequence_length
        else:
            start_idx = 0
            end_idx = start_idx + self.sequence_length

        color_images = []
        depth_images = []
        for color_file in color_files[start_idx:end_idx]:

            color_file = Path(color_file)

            img = cv.imread(str(color_file))
            color_images.append(img)

            if self.load_depth_data:
                depth_file = TUCRID.DEPTH_DIRECTORY.joinpath(f'{link}/{color_file.name}')
                img = cv.imread(str(depth_file), cv.IMREAD_UNCHANGED)
                depth_images.append(img)
        
        X = torch.tensor(np.array(color_images), dtype=torch.float32) / 255
        if self.load_depth_data:
            X_depth = torch.tensor(np.array(depth_images), dtype=torch.float32).unsqueeze(3) / 255
            X = torch.cat([X, X_depth], dim=3)
        X = X.permute(0, 3, 1, 2)
        T = torch.zeros((self.num_classes), dtype=torch.float32)
        T[action] = 1

        self.transforms.__reset__()
        X = self.transforms(X)
        
        return X, T

    def __download__(self):                        
        TUCRID.CACHE_DIRECTORY.mkdir(exist_ok=True, parents=True)

        TUCRID.__download_metadata__()

        TUCRID.__download_backgrounds__()

        TUCRID.__download_sequences__(self.load_depth_data)

    def __download_file__(filename, retries = 10):
        attempts = 0
        while True:
            try:
                hf_hub_download(
                    repo_id=TUCRID.REPO_ID,
                    repo_type='dataset',
                    local_dir=TUCRID.CACHE_DIRECTORY,
                    filename=str(filename)
                )
                break
            except Exception as e:
                if attempts < retries:
                    attempts += 1
                else:
                    raise e

    def __download_metadata__():
        for phase in TUCRID.PHASES:
            if not f'{phase}.json' in os.listdir(TUCRID.CACHE_DIRECTORY):
                TUCRID.__download_file__(f'{phase}.json')

    def __download_backgrounds__():
        # color
        background_color_dir = TUCRID.BACKGROUND_DIRECTORY.joinpath('color')
        if not background_color_dir.exists() or len(os.listdir(background_color_dir)) == 0:
            TUCRID.__download_file__('background/color.tar.gz')
            background_color_tarfile = TUCRID.BACKGROUND_DIRECTORY.joinpath('color.tar.gz')
            with tarfile.open(background_color_tarfile, 'r:gz') as tar:
                tar.extractall(background_color_dir)
            os.remove(background_color_tarfile)

        # depth
        background_depth_dir = TUCRID.BACKGROUND_DIRECTORY.joinpath('depth')
        if not background_depth_dir.exists() or len(os.listdir(background_depth_dir)) == 0:
            TUCRID.__download_file__('background/depth.tar.gz')
            background_depth_tarfile = TUCRID.BACKGROUND_DIRECTORY.joinpath('depth.tar.gz')
            with tarfile.open(background_depth_tarfile, 'r:gz') as tar:
                tar.extractall(background_depth_dir)
            os.remove(background_depth_tarfile)

    def __download_sequences__(load_depth_data):
        repo_files = [Path(file) for file in list_repo_files(TUCRID.REPO_ID, repo_type='dataset')]
        color_files = [file for file in repo_files if file.parent.name == 'color']

        prog = tqdm(color_files, leave=False)
        for color_file in prog:
            prog.set_description(f'Downloading {color_file}')
            local_dir = TUCRID.COLOR_DIRECTORY.joinpath(color_file.name.replace('.tar.gz', ''))
            if local_dir.exists() and len(os.listdir(local_dir)) > 0:
                continue
            TUCRID.__download_file__(color_file)
            tar_color = TUCRID.COLOR_DIRECTORY.joinpath(color_file.name)
            with tarfile.open(tar_color, 'r:gz') as tar:
                tar.extractall(local_dir)
            os.remove(tar_color)

        if load_depth_data:
            depth_files = [file for file in repo_files if file.parent.name == 'depth']
            prog = tqdm(depth_files)
            for depth_file in prog:
                prog.set_description(f'Downloading {depth_file}')
                local_dir = TUCRID.DEPTH_DIRECTORY.joinpath(depth_file.name.replace('.tar.gz', ''))
                if local_dir.exists() and len(os.listdir(local_dir)) > 0:
                    continue
                TUCRID.__download_file__(depth_file)
                tar_depth = TUCRID.DEPTH_DIRECTORY.joinpath(depth_file.name)
                with tarfile.open(tar_depth, 'r:gz') as tar:
                    tar.extractall(local_dir)
                os.remove(tar_depth)

    def __load__(self):
        with open(TUCRID.CACHE_DIRECTORY.joinpath(f'{self.phase}.json'), 'r') as f:
            self.sequences = pd.DataFrame(json.load(f))

        self.action_labels = self.sequences[['action', 'label']].drop_duplicates().sort_values('action')['label'].tolist()

    def get_uniform_sampler(self):
        groups = self.sequences.groupby('action')

        action_counts = groups.size().to_numpy()
        action_weights = 1. / (action_counts / action_counts.sum())
        action_weights = action_weights / action_weights.sum()

        for action, prob in enumerate(action_weights):
            self.sequences.loc[self.sequences['action'] == action, 'sample_prob'] = prob

        class UniformSampler(Sampler):
            def __init__(self, probs, len):
                self.probs = probs
                self.len = len

            def __iter__(self):
                indices = torch.tensor(self.probs).multinomial(self.len, replacement=True).tolist()
                for idx in indices:
                    yield idx

            def __len__(self):
                return self.len
            
        return UniformSampler(self.sequences['sample_prob'].to_numpy(), len(self.sequences))

    def load_backgrounds(load_depth_data:bool = True):
        """
        Loads the background images.

        Parameters
        ----------
        load_depth_data : bool, default = True
            If set to `True`, the depth images will be loaded as well.
        """
        bg_color_dir = TUCRID.BACKGROUND_DIRECTORY.joinpath('color')
        bg_depth_dir = TUCRID.BACKGROUND_DIRECTORY.joinpath('depth')

        if not bg_color_dir.exists() or len(os.listdir(bg_color_dir)) == 0:
            TUCRID.__download_backgrounds__()
        if load_depth_data and (not bg_depth_dir.exists() or len(os.listdir(bg_depth_dir)) == 0):
            TUCRID.__download_backgrounds__()

        bg_color_files = sorted(glob(f'{bg_color_dir}/*'))

        backgrounds = []
        for fname_color in bg_color_files:
            fname_color = Path(fname_color)
            bg_color = cv.imread(str(fname_color))

            if load_depth_data:
                fname_depth = TUCRID.BACKGROUND_DIRECTORY.joinpath('depth', fname_color.name.replace('_color', '_depth'))
                bg_depth = cv.imread(str(fname_depth), cv.IMREAD_UNCHANGED)
                backgrounds.append((bg_color, bg_depth))
            else:
                backgrounds.append((bg_color,))
        return backgrounds

class TUCHRI(Dataset):
    """
    Dataset class for the Robot Interaction Dataset by University of Technology Chemnitz (TUCHRI).
    """
    REPO_ID = 'SchulzR97/TUC-HRI'
    CACHE_DIRECTORY = Path(user_cache_dir('rsp-ml', 'Robert Schulz')).joinpath('dataset', 'TUCHRI')
    COLOR_DIRECTORY = CACHE_DIRECTORY.joinpath('color')
    DEPTH_DIRECTORY = CACHE_DIRECTORY.joinpath('depth')
    PHASES = ['train', 'val']

    def __init__(
            self,
            phase:str,
            load_depth_data:bool = True,
            sequence_length:int = 30,
            num_classes:int = 10,
            transforms:multi_transforms.Compose = multi_transforms.Compose([]),
            cache_dir:str = None
    ):
        """
        Initializes a new instance.

        Parameters
        ----------
        phase : str
            Dataset phase [train|val]
        load_depth_data : bool, default = True
            Load depth data
        sequence_length : int, default = 30
            Length of the sequences
        num_classes : int, default = 10
            Number of classes
        transforms : rsp.ml.multi_transforms.Compose = default = rsp.ml.multi_transforms.Compose([])
            Transformations, that will be applied to each input sequence. See documentation of `rsp.ml.multi_transforms` for more details.
        """
        assert phase in TUCRID.PHASES, f'Phase "{phase}" not in {TUCRID.PHASES}'

        if cache_dir is not None:
            TUCHRI.CACHE_DIRECTORY = Path(cache_dir)
            TUCHRI.COLOR_DIRECTORY = TUCHRI.CACHE_DIRECTORY.joinpath('color')
            TUCHRI.DEPTH_DIRECTORY = TUCHRI.CACHE_DIRECTORY.joinpath('depth')

        self.phase = phase
        self.load_depth_data = load_depth_data
        self.sequence_length = sequence_length
        self.num_classes = num_classes
        self.transforms = transforms

        #self.__download__()
        self.__load__()
        pass

    def __len__(self):
        return len(self.sequences)
    
    def __getitem__(self, idx):
        id = self.sequences['id'][idx]
        action = self.sequences['action'][idx]
        link = self.sequences['link'][idx]

        color_files = sorted(glob(f'{TUCHRI.COLOR_DIRECTORY}/{link}/*.jpg'))
        assert len(color_files) >= self.sequence_length, f'Not enough frames for {id}.'

        if len(color_files) > self.sequence_length:
            start_idx = np.random.randint(0, len(color_files) - self.sequence_length)
            end_idx = start_idx + self.sequence_length
        else:
            start_idx = 0
            end_idx = start_idx + self.sequence_length

        color_images = []
        depth_images = []
        for color_file in color_files[start_idx:end_idx]:

            color_file = Path(color_file)

            img = cv.imread(str(color_file))
            color_images.append(img)

            if self.load_depth_data:
                depth_file = TUCHRI.DEPTH_DIRECTORY.joinpath(f'{link}/{color_file.name}')
                img = cv.imread(str(depth_file), cv.IMREAD_UNCHANGED)
                depth_images.append(img)
        
        X = torch.tensor(np.array(color_images), dtype=torch.float32) / 255
        if self.load_depth_data:
            X_depth = torch.tensor(np.array(depth_images), dtype=torch.float32).unsqueeze(3) / 255
            X = torch.cat([X, X_depth], dim=3)
        X = X.permute(0, 3, 1, 2)
        T = torch.zeros((self.num_classes), dtype=torch.float32)
        T[action] = 1

        self.transforms.__reset__()
        X = self.transforms(X)
        
        return X, T

    def __download__(self):                        
        TUCHRI.CACHE_DIRECTORY.mkdir(exist_ok=True, parents=True)

        TUCHRI.__download_metadata__()

        TUCHRI.__download_sequences__(self.load_depth_data)

    def __download_file__(filename, retries = 10):
        attempts = 0
        while True:
            try:
                hf_hub_download(
                    repo_id=TUCHRI.REPO_ID,
                    repo_type='dataset',
                    local_dir=TUCHRI.CACHE_DIRECTORY,
                    filename=str(filename)
                )
                break
            except Exception as e:
                if attempts < retries:
                    attempts += 1
                else:
                    raise e

    def __download_metadata__():
        for phase in TUCHRI.PHASES:
            if not f'{phase}.json' in os.listdir(TUCHRI.CACHE_DIRECTORY):
                TUCHRI.__download_file__(f'{phase}.json')

    def __download_sequences__(load_depth_data):
        repo_files = [Path(file) for file in list_repo_files(TUCHRI.REPO_ID, repo_type='dataset')]
        color_files = [file for file in repo_files if file.parent.name == 'color']

        prog = tqdm(color_files, leave=False)
        for color_file in prog:
            prog.set_description(f'Downloading {color_file}')
            local_dir = TUCHRI.COLOR_DIRECTORY.joinpath(color_file.name.replace('.tar.gz', ''))
            if local_dir.exists() and len(os.listdir(local_dir)) > 0:
                continue
            TUCHRI.__download_file__(color_file)
            tar_color = TUCHRI.COLOR_DIRECTORY.joinpath(color_file.name)
            with tarfile.open(tar_color, 'r:gz') as tar:
                tar.extractall(local_dir)
            os.remove(tar_color)

        if load_depth_data:
            depth_files = [file for file in repo_files if file.parent.name == 'depth']
            prog = tqdm(depth_files)
            for depth_file in prog:
                prog.set_description(f'Downloading {depth_file}')
                local_dir = TUCHRI.DEPTH_DIRECTORY.joinpath(depth_file.name.replace('.tar.gz', ''))
                if local_dir.exists() and len(os.listdir(local_dir)) > 0:
                    continue
                TUCHRI.__download_file__(depth_file)
                tar_depth = TUCHRI.DEPTH_DIRECTORY.joinpath(depth_file.name)
                with tarfile.open(tar_depth, 'r:gz') as tar:
                    tar.extractall(local_dir)
                os.remove(tar_depth)

    def __load__(self):
        with open(TUCHRI.CACHE_DIRECTORY.joinpath(f'{self.phase}.json'), 'r') as f:
            self.sequences = pd.DataFrame(json.load(f))

        self.action_labels = self.sequences[['action', 'label']].drop_duplicates().sort_values('action')['label'].tolist()

    def get_uniform_sampler(self):
        groups = self.sequences.groupby('action')

        action_counts = groups.size().to_numpy()
        action_weights = 1. / (action_counts / action_counts.sum())
        action_weights = action_weights / action_weights.sum()

        for action, prob in enumerate(action_weights):
            self.sequences.loc[self.sequences['action'] == action, 'sample_prob'] = prob

        class UniformSampler(Sampler):
            def __init__(self, probs, len):
                self.probs = probs
                self.len = len

            def __iter__(self):
                indices = torch.tensor(self.probs).multinomial(self.len, replacement=True).tolist()
                for idx in indices:
                    yield idx

            def __len__(self):
                return self.len
            
        return UniformSampler(self.sequences['sample_prob'].to_numpy(), len(self.sequences))

    def load_backgrounds(load_depth_data:bool = True):
        """
        Loads the background images.

        Parameters
        ----------
        load_depth_data : bool, default = True
            If set to `True`, the depth images will be loaded as well.
        """
        bg_color_dir = TUCHRI.BACKGROUND_DIRECTORY.joinpath('color')
        bg_depth_dir = TUCHRI.BACKGROUND_DIRECTORY.joinpath('depth')

        if not bg_color_dir.exists() or len(os.listdir(bg_color_dir)) == 0:
            TUCHRI.__download_backgrounds__()
        if load_depth_data and (not bg_depth_dir.exists() or len(os.listdir(bg_depth_dir)) == 0):
            TUCHRI.__download_backgrounds__()

        bg_color_files = sorted(glob(f'{bg_color_dir}/*'))

        backgrounds = []
        for fname_color in bg_color_files:
            fname_color = Path(fname_color)
            bg_color = cv.imread(str(fname_color))

            if load_depth_data:
                fname_depth = TUCHRI.BACKGROUND_DIRECTORY.joinpath('depth', fname_color.name.replace('_color', '_depth'))
                bg_depth = cv.imread(str(fname_depth), cv.IMREAD_UNCHANGED)
                backgrounds.append((bg_color, bg_depth))
            else:
                backgrounds.append((bg_color,))
        return backgrounds

#__example__ from rsp.ml.dataset import HMDB51
#__example__ import rsp.ml.multi_transforms as multi_transforms
#__example__ import cv2 as cv
#__example__ 
#__example__ transforms = multi_transforms.Compose([
#__example__     multi_transforms.Color(1.5, p=0.5),
#__example__     multi_transforms.Stack()
#__example__ ])
#__example__ ds = HMDB51('train', fold=1, transforms=transforms)
#__example__ 
#__example__ for X, T in ds:
#__example__   for x in X.permute(0, 2, 3, 1):
#__example__     img_color = x[:, :, :3].numpy()
#__example__     img_depth = x[:, :, 3].numpy()
#__example__ 
#__example__     cv.imshow('color', img_color)
#__example__     cv.imshow('depth', img_depth)
#__example__ 
#__example__     cv.waitKey(30)
class HMDB51(Dataset):
    """
    Dataset class for HMDB51.
    """
    def __init__(
            self,
            split:str,
            fold:int = None,
            cache_dir:str = None,
            force_reload:bool = False,
            target_size = (400, 400),
            sequence_length:int = 30,
            transforms:multi_transforms.Compose = multi_transforms.Compose([]),
            verbose:bool = True
    ):
        """
        Initializes a new instance.

        Parameters
        ----------
        split : str
            Dataset split [train|val|test]
        fold : int
            Fold number. The dataset is split into 3 folds. If fold is None, all folds will be loaded.
        cache_dir : str, default = None
            Directory to store the downloaded files. If set to `None`, the default cache directory will be used
        force_reload : bool, default = False
            If set to `True`, the dataset will be reloaded
        target_size : (int, int), default = (400, 400)
            Size of the frames. The frames will be resized to this size.
        sequence_length : int, default = 30
            Length of the sequences
        transforms : rsp.ml.multi_transforms.Compose = default = rsp.ml.multi_transforms.Compose([])
            Transformations, that will be applied to each input sequence. See documentation of `rsp.ml.multi_transforms` for more details.
        verbose : bool, default = False
            If set to `True`, the progress will be printed.
        """
        self.download_link = f'https://drive.google.com/uc?id=1iMQo02o9iEuawhGcicBvzqbZxvtoLCok'
        self.split = split
        self.fold = fold
        self.force_reload = force_reload
        self.target_size = target_size
        self.sequence_length = sequence_length
        self.transforms = transforms
        self.verbose = verbose

        if cache_dir is None:
            self.__cache_dir__ = Path(user_cache_dir("rsp-ml", "Robert Schulz")).joinpath('dataset', 'HMDB51')
        else:
            self.__cache_dir__ = Path(cache_dir).joinpath('HMDB51')
        self.__cache_dir__.mkdir(parents=True, exist_ok=True)

        self.__download__()
        self.__list_files__()

    def __len__(self):
        return len(self.__files__)
    
    def __getitem__(self, index):
        action, fname = self.__files__[index]

        cap = cv.VideoCapture(fname)
        cnt = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
        width = cap.get(cv.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv.CAP_PROP_FRAME_HEIGHT)

        if cnt-self.sequence_length <= 0:
            start_idx = 0
        else:
            start_idx = np.random.randint(0, cnt-self.sequence_length)
        end_idx = start_idx + self.sequence_length

        frames = []
        cap.set(cv.CAP_PROP_POS_FRAMES, start_idx)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv.resize(frame, self.target_size)
            frames.append(frame)
            if len(frames) >= self.sequence_length:
                break

        X = torch.tensor(np.array(frames), dtype=torch.float32).permute(0, 3, 1, 2) / 255
        T = torch.zeros((len(self.action_labels)), dtype=torch.float32)
        T[action] = 1

        if X.shape[0] < self.sequence_length:
            if self.verbose:
                try:
                    console.warn(f'Seuqnce length was {X.shape[0]}. Expected {self.sequence_length}. Automatic expanding...')
                except:
                    print(f'Seuqnce length was {X.shape[0]}. Expected {self.sequence_length}. Automatic expanding...')
            X = torch.concat([X, torch.zeros((self.sequence_length-X.shape[0], X.shape[1], X.shape[2], X.shape[3]), dtype=torch.float32)])

        X = self.transforms(X)

        return X, T

    def __download__(self):
        zip_file = f'{self.__cache_dir__.parent}/HMDB51.zip'
        if not os.path.isdir(f'{self.__cache_dir__}') or len(os.listdir(self.__cache_dir__)) == 0 or self.force_reload:
            if not os.path.isfile(zip_file):
                if self.verbose:
                    try:
                        console.print_c('Downloading HMDB51 dataset...', color=console.color.GREEN)
                    except:
                        print('Downloading HMDB51 dataset...')
                gdown.download(self.download_link, zip_file, quiet=not self.verbose)
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                try:
                    console.print_c('Extracting zip file...', color=console.color.GREEN)
                except:
                    print('Extracting zip file...')
                zip_ref.extractall(self.__cache_dir__.parent)
            if os.path.isdir(f'{self.__cache_dir__.parent}/__MACOSX'):
                shutil.rmtree(f'{self.__cache_dir__.parent}/__MACOSX')
            os.remove(zip_file)

    def __list_files__(self):
        self.__files__ = []

        self.action_labels = sorted([Path(folder).name for folder in glob(f'{self.__cache_dir__}/sequences/*')])

        if self.fold is None:
            split_files = glob(f'{self.__cache_dir__}/splits/*_split*.txt')
        else:
            split_files = glob(f'{self.__cache_dir__}/splits/*_split{self.fold}.txt')

        for split_file in split_files:
            split_file = Path(split_file)
            end_idx = split_file.name.find('_test_split')
            label = split_file.name[:end_idx]
            action_idx = self.action_labels.index(label)

            with open(split_file, 'r') as file:
                lines = [line for line in file.read().split('\n') if len(line) > 0]
                for line in lines:
                    fname = line.split(' ')[0]
                    fname = f'{self.__cache_dir__}/sequences/{label}/{fname}'
                    split_idx = int(line.split(' ')[1])
                    if self.split == 'train' and split_idx == 1:
                        self.__files__.append((action_idx, fname))
                    elif self.split == 'val' and split_idx == 2:
                        self.__files__.append((action_idx, fname))
                    elif self.split == 'test' and split_idx == 0:
                        self.__files__.append((action_idx, fname))
                pass
            pass

#__example__ from rsp.ml.dataset import Kinetics
#__example__ 
#__example__ ds = Kinetics(split='train', type=400)
#__example__
#__example__ for X, T in ds:
#__example__     print(X)
class Kinetics(Dataset):
    """
    Dataset class for the Kinetics dataset.
    """
    def __init__(
        self,
        split:str,
        sequence_length:int = 60,
        type:int = 400,
        frame_size = (400, 400),
        transforms:multi_transforms.Compose = multi_transforms.Compose([]),
        cache_dir:str = None,
        num_threads:int = 0,
        verbose:bool = True
    ):
        """
        Initializes a new instance.
        
        Parameters
        ----------
        split : str
            Dataset split [train|val]
        sequence_length : int, default = 60
            Length of the sequences
        type : int, default = 400
            Type of the kineticts dataset. Currently only 400 is supported.
        frame_size : (int, int), default = (400, 400)
            Size of the frames. The frames will be resized to this size.
        transforms : rsp.ml.multi_transforms.Compose = default = rsp.ml.multi_transforms.Compose([])
            Transformations, that will be applied to each input sequence. See documentation of `rsp.ml.multi_transforms` for more details.
        cache_dir : str, default = None
            Directory to store the downloaded files. If set to `None`, the default cache directory will be used
        num_threads : int, default = 0
            Number of threads to use for downloading the files.
        verbose : bool, default = True
            If set to `True`, the progress and additional information will be printed.
        """
        super().__init__()

        assert split in ['train', 'val'], f'{split} is not a valid split.'
        assert type in [400], f'{type} is not a valid type.'

        self.split = split
        self.type = type
        self.frame_size = frame_size
        self.sequence_length = sequence_length
        self.transforms = transforms
        self.num_threads = num_threads
        self.verbose = verbose

        if cache_dir is None:
            self.__cache_dir__ = Path(user_cache_dir("rsp-ml", "Robert Schulz")).joinpath('dataset', f'KINETICS{type}')
        else:
            self.__cache_dir__ = Path(cache_dir)
        self.__cache_dir__.mkdir(parents=True, exist_ok=True)

        self.__toTensor__ = multi_transforms.ToTensor()
        self.__stack__ = multi_transforms.Stack()

        self.__download__()
        self.__annotations__, self.action_labels = self.__load_annotations_labels__()
        self.__invalid_files__ = self.__get_invalid_files__()
        self.__files__ = self.__list_files__()

    def __getitem__(self, index):
        youtube_id, fname = self.__files__[index]

        annotation = self.__annotations__[youtube_id]

        if annotation['time_end'] - annotation['time_start'] > self.sequence_length:
            start_idx = np.random.randint(annotation['time_start'], annotation['time_end']-self.sequence_length)
            end_idx = start_idx + self.sequence_length
        else:
            start_idx = (annotation['time_end'] - annotation['time_start'])//2 - self.sequence_length//2
            end_idx = (annotation['time_end'] - annotation['time_start'])//2 + self.sequence_length//2

        cap = cv.VideoCapture(fname)
        cap.set(cv.CAP_PROP_POS_FRAMES, start_idx)

        frames = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv.resize(frame, self.frame_size)
            frames.append(frame)
            if len(frames) >= end_idx - start_idx:
                break
        frames = np.array(frames) / 255

        if len(frames) == 0:
            X = torch.zeros((self.sequence_length, 3, *self.frame_size), dtype=torch.float32)
            if self.verbose:
                console.warn(f'No frames found for {youtube_id}.')
        else:
            X = torch.tensor(frames, dtype=torch.float32).permute(0, 3, 1, 2)
        T = torch.zeros((len(self.action_labels)), dtype=torch.float32)
        cls = self.action_labels.index(annotation['label'])
        T[cls] = 1

        if X.shape[0] < self.sequence_length:
            if self.verbose:
                console.warn(f'Seuqnce length was {X.shape[0]}. Expected {self.sequence_length}. Automatic expanding...')
            X = torch.concat([X, torch.zeros((self.sequence_length-X.shape[0], X.shape[1], X.shape[2], X.shape[3]), dtype=torch.float32)])

        X = self.transforms(X)

        return X, T
    
    def __get_invalid_files__(self):
        valid_files_file = self.__cache_dir__.joinpath('valid_files.txt')
        invalid_files_file = self.__cache_dir__.joinpath('invalid_files.txt')

        if valid_files_file.exists():
            with open(str(valid_files_file), 'r') as file:
                lines = file.read().split('\n')
            valid_files = [line for line in lines if len(line) > 0]
        else:
            valid_files = []  

        if invalid_files_file.exists():
            with open(str(invalid_files_file), 'r') as file:
                lines = file.read().split('\n')
            invalid_files = [line for line in lines if len(line) > 0]
            # invalid_files = list(dict.fromkeys(invalid_files))
            # with open(str(invalid_files_file), 'w') as file:
            #     for line in invalid_files:
            #         file.write(f'{line}\n')
        else:
            invalid_files = []    

        videos_dir = self.__cache_dir__.joinpath('videos', self.split)
        links = glob(f'{videos_dir}/k{self.type}*/*.mp4')

        prog = tqdm(links, leave=False)
        for i, link in enumerate(prog):
            file = Path(link)
            link = f'/{file.parent.parent.parent.name}/{file.parent.parent.name}/{file.parent.name}/{file.name}'
            youtube_id = file.name[:-18]

            if youtube_id in invalid_files or youtube_id in valid_files:
                continue

            if not file.exists():
                with open(invalid_files_file, 'a') as file:
                    file.write(f'{youtube_id}\n')
                invalid_files.append(youtube_id)
                continue

            cap = cv.VideoCapture(str(file))
            if not cap.isOpened():
                with open(invalid_files_file, 'a') as file:
                    file.write(f'{youtube_id}\n')
                invalid_files.append(youtube_id)
                cap.release()
                continue

            idx_start = int(file.name[-17:-11])
            idx_end = int(file.name[-10:-4])
            cnt = int(cap.get(cv.CAP_PROP_FRAME_COUNT))

            ret, _ = cap.read()

            if not ret:
                with open(invalid_files_file, 'a') as file:
                    file.write(f'{youtube_id}\n')
                invalid_files.append(youtube_id)
                cap.release()
                continue

            cap.release()

            with open(valid_files_file, 'a') as file:
                file.write(f'{youtube_id}\n')
            valid_files.append(youtube_id)

            prog.set_description(f'Invalid files {len(invalid_files)} ({len(invalid_files)/(len(invalid_files)+len(valid_files))*100:.2f}%)')
            #break

        return invalid_files

    def __len__(self):
        return len(self.__files__)

    def __get_labels__(self):
        labels = {}
        df = pd.DataFrame(self.__annotations__)
        for i, (key, _) in enumerate(df.groupby('label')):
            key = key.replace('"', '')
            labels[key] = i
        return labels

    def __download__(self):
        def get_fname_resource(resource_name):
            fname = pkg_resources.resource_filename('rsp', resource_name)
            return Path(fname)
        
        def download_file(link, fname, retries = 10):
            attempt = 0
            while attempt < retries:
                try:
                    urllib.request.urlretrieve(link, fname)
                    break
                except urllib.error.ContentTooShortError as e:
                    attempt += 1
                except Exception as e:
                    attempt += 1

        def unpack(src, dest, remove = True):
            with tarfile.open(src, "r:gz") as tar:
                tar.extractall(path=dest)
            if remove:
                os.remove(src)

        anno_link_file = get_fname_resource(f'ml/dataset/links/kinetics/annotations/k{self.type}_annotations.txt')
        with open(anno_link_file, 'r') as file:
            links = file.read().split('\n')
            cache_anno_dir = Path(self.__cache_dir__).joinpath('annotations')
            cache_anno_dir.mkdir(parents=True, exist_ok=True)
            for link in links:
                fname = link.split('/')[-1]
                fname = cache_anno_dir.joinpath(f'k{self.type}_{fname}')
                if fname.exists():
                    continue
                download_file(link, fname)

        path_link_files = [
            get_fname_resource(f'ml/dataset/links/kinetics/paths/k{self.type}_train_path.txt'),
            get_fname_resource(f'ml/dataset/links/kinetics/paths/k{self.type}_test_path.txt'),
            get_fname_resource(f'ml/dataset/links/kinetics/paths/k{self.type}_val_path.txt')
        ]

        cache_archives_dir = self.__cache_dir__.joinpath('archives')
        cache_archives_dir.mkdir(parents=True, exist_ok=True)

        cache_videos_dir = self.__cache_dir__.joinpath('videos')
        cache_videos_dir.mkdir(parents=True, exist_ok=True)

        threads = []

        prog1 = tqdm(path_link_files, leave=False)
        for link_file in prog1:
            prog1.set_description(f'Downloading {link_file.stem}')

            with open(link_file, 'r') as file:
                links = file.read().split('\n')
            prog2 = tqdm(links, leave=False)
            for link in prog2:
                prog2.set_description(link)

                def process_link(link):
                    split, fname = link.split('/')[-2:]

                    video_dir = cache_videos_dir.joinpath(split, 'k' + str(self.type) + '_' + fname.split(".")[0])
                    if video_dir.exists():
                        #continue
                        return

                    archive_file = cache_archives_dir.joinpath(split, f'k{self.type}_{fname}')
                    archive_file.parent.mkdir(parents=True, exist_ok=True)
                    if not archive_file.exists():
                        download_file(link, archive_file)

                    video_dir.mkdir(parents=True, exist_ok=True)
                    try:
                        unpack(archive_file, video_dir, remove=True)
                    except Exception as e:
                        video_dir.rmdir()
                        os.remove(archive_file)
                        download_file(link, archive_file)
                        unpack(archive_file, video_dir, remove=True)

                if self.num_threads == 0:
                    process_link(link)
                else:
                    thread = Thread(target=process_link, args=(link,))
                    while len(threads) >= self.num_threads:
                        threads = [t for t in threads if t.is_alive()]
                        time.sleep(0.1)
                    thread.start()
                    threads.append(thread)

    def __load_annotations_labels__(self):
        annotations_file = self.__cache_dir__.joinpath('annotations', f'k{self.type}_{self.split}.csv')
        annotations = {}
        labels = []
        with open(annotations_file, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for i, row in enumerate(spamreader):
                if i == 0:
                    continue
                label, youtube_id, time_start, time_end, split, is_cc = row[0], row[1], int(row[2]), int(row[3]), row[4], int(row[5])
                label = label.replace('"', '')
                annotations[youtube_id] = {
                    'label': label,
                    #'youtube_id': youtube_id,
                    'time_start': time_start,
                    'time_end': time_end,
                    'split': split,
                    'is_cc': is_cc
                }
                if label not in labels:
                    labels.append(label)
        return annotations, sorted(labels)

    def __list_files__(self):
        videos_dir = self.__cache_dir__.joinpath('videos', self.split)
        links = glob(f'{videos_dir}/k{self.type}*/*.mp4')
        files = []#{}
        for link in links:
            youtube_id = Path(link).name[:-18]
            if youtube_id in self.__invalid_files__:
                continue
            files.append((youtube_id, link))
        return files

#__example__ from rsp.ml.dataset import UCF101
#__example__ import rsp.ml.multi_transforms as multi_transforms
#__example__ import cv2 as cv
#__example__ 
#__example__ transforms = multi_transforms.Compose([
#__example__     multi_transforms.Color(1.5, p=0.5),
#__example__     multi_transforms.Stack()
#__example__ ])
#__example__ ds = UCF101('train', fold=1, transforms=transforms)
#__example__ 
#__example__ for X, T in ds:
#__example__   for x in X.permute(0, 2, 3, 1):
#__example__     img_color = x[:, :, :3].numpy()
#__example__     img_depth = x[:, :, 3].numpy()
#__example__ 
#__example__     cv.imshow('color', img_color)
#__example__     cv.imshow('depth', img_depth)
#__example__ 
#__example__     cv.waitKey(30)
class UCF101(Dataset):
    def __init__(
            self,
            split:str,
            fold:int = None,
            cache_dir:str = None,
            force_reload:bool = False,
            target_size = (400, 400),
            sequence_length:int = 60,
            transforms:multi_transforms.Compose = multi_transforms.Compose([]),
            verbose:bool = True
        ):
        """
        Initializes a new instance.

        Parameters
        ----------
        split : str
            Dataset split [train|val|test]
        fold : int
            Fold number. The dataset is split into 3 folds. If fold is None, all folds will be loaded.
        cache_dir : str, default = None
            Directory to store the downloaded files. If set to `None`, the default cache directory will be used
        force_reload : bool, default = False
            If set to `True`, the dataset will be reloaded
        target_size : (int, int), default = (400, 400)
            Size of the frames. The frames will be resized to this size.
        sequence_length : int, default = 30
            Length of the sequences
        transforms : rsp.ml.multi_transforms.Compose = default = rsp.ml.multi_transforms.Compose([])
            Transformations, that will be applied to each input sequence. See documentation of `rsp.ml.multi_transforms` for more details.
        verbose : bool, default = False
            If set to `True`, the progress will be printed.
        """
        assert split in ['train', 'val'], f'{split} is not a valid split. Please use one of [train, val].'
        assert fold in [None, 1, 2, 3], f'{fold} is not a valid fold. Please use one of [None, 1, 2, 3].'

        self.download_link = f'https://drive.google.com/uc?id=1AgvxQl9ShkQyh83FGf-njBiwPKkrLkWw'
        self.split = split
        self.fold = fold
        self.force_reload = force_reload
        self.target_size = target_size
        self.sequence_length = sequence_length
        self.transforms = transforms
        self.verbose = verbose

        if cache_dir is None:
            self.__cache_dir__ = Path(user_cache_dir("rsp-ml", "Robert Schulz")).joinpath('dataset', 'UCF101')
        else:
            self.__cache_dir__ = Path(cache_dir).joinpath('UCF101')
        self.__cache_dir__.mkdir(parents=True, exist_ok=True)

        self.__download__()
        self.__list_files__()

    def __len__(self):
        return len(self.__files__)

    def __getitem__(self, index):
        action, fname = self.__files__[index]

        cap = cv.VideoCapture(fname)
        cnt = int(cap.get(cv.CAP_PROP_FRAME_COUNT))

        if cnt-self.sequence_length <= 0:
            start_idx = 0
        else:
            start_idx = np.random.randint(0, cnt-self.sequence_length)
        end_idx = start_idx + self.sequence_length

        frames = []
        cap.set(cv.CAP_PROP_POS_FRAMES, start_idx)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv.resize(frame, self.target_size)
            frames.append(frame)
            if len(frames) >= self.sequence_length:
                break

        X = torch.tensor(np.array(frames), dtype=torch.float32).permute(0, 3, 1, 2) / 255
        T = torch.zeros((len(self.action_labels)), dtype=torch.float32)
        T[action] = 1

        if X.shape[0] < self.sequence_length:
            if self.verbose:
                try:
                    console.warn(f'Seuqnce length was {X.shape[0]}. Expected {self.sequence_length}. Automatic expanding...')
                except:
                    print(f'Seuqnce length was {X.shape[0]}. Expected {self.sequence_length}. Automatic expanding...')
            X = torch.concat([X, torch.zeros((self.sequence_length-X.shape[0], X.shape[1], X.shape[2], X.shape[3]), dtype=torch.float32)])

        X = self.transforms(X)

        return X, T
    
    def __download__(self):
        zip_file = f'{self.__cache_dir__.parent}/UCF101.zip'
        if not os.path.isdir(f'{self.__cache_dir__}') or len(os.listdir(self.__cache_dir__)) == 0 or self.force_reload:
            if self.verbose:
                try:
                    console.print_c('Downloading UCF101 dataset...', color=console.color.GREEN)
                except:
                    print('Downloading UCF101 dataset...')
            if not os.path.isfile(zip_file):
                gdown.download(self.download_link, zip_file, quiet=not self.verbose)
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(self.__cache_dir__.parent)
            if os.path.isdir(f'{self.__cache_dir__.parent}/__MACOSX'):
                shutil.rmtree(f'{self.__cache_dir__.parent}/__MACOSX')
            os.remove(zip_file)

    def __list_files__(self):
        self.__files__ = []

        self.action_labels = sorted([Path(folder).name for folder in glob(f'{self.__cache_dir__}/sequences/*')])

        splitname = 'trainlist' if self.split == 'train' else 'testlist'
        if self.fold is None:
            split_files = glob(f'{self.__cache_dir__}/splits/{splitname}*.txt')
        else:
            split_files = glob(f'{self.__cache_dir__}/splits/{splitname}*{self.fold}.txt')

        for split_file in split_files:
            split_file = Path(split_file)

            with open(split_file, 'r') as file:
                lines = [line for line in file.read().split('\n') if len(line) > 0]
                for line in lines:
                    action = line.split(' ')[0].split('/')[0]
                    fname = line.split(' ')[0]
                    fname = f'{self.__cache_dir__}/sequences/{fname}'
                    action_idx = self.action_labels.index(action)
                    self.__files__.append((action_idx, fname))
                pass
            pass

#__example__ from rsp.ml.dataset import UTKinectAction3D
#__example__ import rsp.ml.multi_transforms as multi_transforms
#__example__ import cv2 as cv
#__example__ 
#__example__ transforms = multi_transforms.Compose([
#__example__     multi_transforms.Color(1.5, p=0.5),
#__example__     multi_transforms.Stack()
#__example__ ])
#__example__ ds = UTKinectAction3D('train', transforms=transforms)
#__example__ 
#__example__ for X, T in ds:
#__example__   for x in X.permute(0, 2, 3, 1):
#__example__     img_color = x[:, :, :3].numpy()
#__example__     img_depth = x[:, :, 3].numpy()
#__example__ 
#__example__     cv.imshow('color', img_color)
#__example__     cv.imshow('depth', img_depth)
#__example__ 
#__example__     cv.waitKey(30)
class UTKinectAction3D(Dataset):
    """
    Dataset class for the UTKinectAction3D dataset.

    Parameters
    ----------
    split : str
        Dataset split [train|val]
    cache_dir : str, default = None
        Directory to store the downloaded files. If set to `None`, the default cache directory will be used
    force_reload : bool, default = False
        If set to `True`, the dataset will be reloaded
    target_size : (int, int), default = (400, 400)
        Size of the frames. The frames will be resized to this size.
    sequence_length : int, default = 30
        Length of the sequences
    transforms : rsp.ml.multi_transforms.Compose = default = rsp.ml.multi_transforms.Compose([])
        Transformations, that will be applied to each input sequence. See documentation of `rsp.ml.multi_transforms` for more details.
    verbose : bool, default = False
        If set to `True`, the progress will be printed.
    """
    def __init__(
            self,
            split:str,
            cache_dir:str = None,
            force_reload:bool = False,
            target_size:tuple[int, int] = (400, 400),
            sequence_length:int = 30,
            transforms:multi_transforms.Compose = multi_transforms.Compose([]),
            verbose:bool = True
        ):
        assert split in ['train', 'val'], f'{split} is not a valid split. Please use one of [train, val].'

        self.downloadlink_rgb = 'https://cvrc.ece.utexas.edu/KinectDatasets/RGB.zip'
        self.downloadlink_depth = 'https://cvrc.ece.utexas.edu/KinectDatasets/depth.zip'
        self.downloadlink_labels = 'https://cvrc.ece.utexas.edu/KinectDatasets/actionLabel.txt'

        self.split = split
        self.force_reload = force_reload
        self.target_size = target_size
        self.sequence_length = sequence_length
        self.transforms = transforms
        self.verbose = verbose

        if cache_dir is None:
            self.__cache_dir__ = Path(user_cache_dir("rsp-ml", "Robert Schulz")).joinpath('dataset', 'UTKinectAction3D')
        else:
            self.__cache_dir__ = Path(cache_dir).joinpath('UTKinectAction3D')
        self.__cache_dir__.mkdir(parents=True, exist_ok=True)

        self.__download__()
        self.__list_files__()

    def __download__(self):
        # RGB
        zip_file_rgb = f'{self.__cache_dir__.parent}/UTKinectAction3D_rgb.zip'
        if not self.__cache_dir__.joinpath('RGB').exists() or\
                len(os.listdir(self.__cache_dir__.joinpath('RGB'))) == 0 or\
                self.force_reload:
            if not os.path.isfile(zip_file_rgb):
                print(f'Downloading {self.downloadlink_rgb}')
                urllib.request.urlretrieve(self.downloadlink_rgb, zip_file_rgb)
            zipfile.ZipFile(zip_file_rgb, 'r').extractall(self.__cache_dir__)
        if os.path.isfile(zip_file_rgb):
            os.remove(zip_file_rgb)

        # depth
        zip_file_depth = f'{self.__cache_dir__.parent}/UTKinectAction3D_depth.zip'
        if not self.__cache_dir__.joinpath('depth').exists() or\
                len(os.listdir(self.__cache_dir__.joinpath('depth'))) == 0 or\
                self.force_reload:
            if not os.path.isfile(zip_file_depth):
                print(f'Downloading {self.downloadlink_depth}')
                urllib.request.urlretrieve(self.downloadlink_depth, zip_file_depth)
            zipfile.ZipFile(zip_file_depth, 'r').extractall(self.__cache_dir__)
        if os.path.isfile(zip_file_depth):
            os.remove(zip_file_depth)

        # labels
        labels_txt = f'{self.__cache_dir__}/labels.txt'
        if not os.path.isfile(labels_txt) or self.force_reload:
            print(f'Downloading {self.downloadlink_labels}')
            urllib.request.urlretrieve(self.downloadlink_labels, labels_txt)

    def __list_files__(self):
        self.__sequences__ = []
        self.action_labels = []

        labels_txt = f'{self.__cache_dir__}/labels.txt'
        with open(labels_txt, 'r') as file:
            lines = [line for line in file.read().split('\n') if len(line) > 0]
        
        sub_dir = None
        for line in lines:
            line = line.replace('  ', ' ')
            if ':' in line:
                try:
                    subject = int(sub_dir[1:3])
                    if self.split == 'train' and subject <= 8 or\
                        self.split == 'val' and subject > 8:
                        action = line.split(':')[0]
                        if action not in self.action_labels:
                            self.action_labels.append(action)
                        start_idx = int(line.split(' ')[1])
                        end_idx = int(line.split(' ')[2])
                        self.__sequences__.append((sub_dir, action, start_idx, end_idx))
                except Exception as e:
                    pass
            else:
                sub_dir = line
        self.action_labels = sorted(self.action_labels)

    def __len__(self):
        return len(self.__sequences__)
    
    def __getitem__(self, index):
        sub_dir, action_label, start_idx, end_idx = self.__sequences__[index]
        action_idx = self.action_labels.index(action_label)
        
        def load_utkinect_depth_from_xml(file_path):
            """ Lädt eine UTKinect XML-Tiefendatei und konvertiert sie in ein 320x240 NumPy-Array """
            
            # XML-Datei parsen
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Höhe und Breite aus XML auslesen
            width = int(root.find(".//width").text)
            height = int(root.find(".//height").text)

            # Tiefendaten aus <data>-Tag holen (Werte sind durch Leerzeichen getrennt)
            depth_text = root.find(".//data").text.strip()
            depth_values = np.array(list(map(int, depth_text.split())), dtype=np.uint16)

            # In (Höhe, Breite) umformen
            depth_image = depth_values.reshape((height, width))

            return depth_image

        rgb_frames, depth_frames = [], []
        for i in range(start_idx, end_idx+1):
            rgb_file = self.__cache_dir__.joinpath('RGB', sub_dir, f'colorImg{i}.jpg')
            if rgb_file.exists() == False:
                continue
            rgb_img = cv.imread(str(rgb_file))
            rgb_img = cv.resize(rgb_img, (self.target_size[0], self.target_size[1]))

            depth_file = self.__cache_dir__.joinpath('depth', sub_dir, f'depthImg{i}.xml')
            depth_img = load_utkinect_depth_from_xml(depth_file)
            depth_img = cv.resize(depth_img, (self.target_size[0], self.target_size[1]))

            rgb_frames.append(rgb_img)
            depth_frames.append(depth_img)

        X_rgb = torch.tensor(np.array(rgb_frames), dtype=torch.float32).permute(0, 3, 1, 2) / 255
        X_depth = torch.tensor(np.array(depth_frames), dtype=torch.float32).unsqueeze(1) / 31800
        X = torch.cat([X_rgb, X_depth], dim=1)

        if X.shape[0] > self.sequence_length:
            start_idx = np.random.randint(0, X.shape[0]-self.sequence_length)
            X = X[start_idx:start_idx+self.sequence_length]
        if X.shape[0] < self.sequence_length:
            X = torch.cat([X, torch.zeros((self.sequence_length-X.shape[0], X.shape[1], X.shape[2], X.shape[3]), dtype=torch.float32)])

        X = self.transforms(X)

        T = torch.zeros((len(self.action_labels)), dtype=torch.float32)
        T[action_idx] = 1

        return X, T

if __name__ == '__main__':
    USE_DEPTH_DATA = True
    backgrounds = TUCRID.load_backgrounds(USE_DEPTH_DATA)
    tranforms_train = multi_transforms.Compose([
        multi_transforms.ReplaceBackground(
            backgrounds = backgrounds,
            hsv_filter=[(69, 87, 139, 255, 52, 255)],
            p = 0.8,
            rotate=180
        ),
        multi_transforms.Resize((400, 400), auto_crop=False),
        multi_transforms.Color(0.1, p = 0.2),
        multi_transforms.Brightness(0.7, 1.3),
        multi_transforms.Satturation(0.7, 1.3),
        multi_transforms.RandomHorizontalFlip(),
        multi_transforms.GaussianNoise(0.002),
        multi_transforms.Rotate(max_angle=3),
        multi_transforms.Stack()
    ])
    tucrid_train = TUCRID('train', load_depth_data=USE_DEPTH_DATA, transforms=tranforms_train)
    sampler_train = tucrid_train.get_uniform_sampler()

    dl_train = DataLoader(tucrid_train, batch_size=4, sampler=sampler_train)

    for X, T in dl_train:
        for seq_X, seq_T in zip(X, T):
            for x in seq_X:
                img = x[0:3].permute(1, 2, 0).numpy()
                img = np.array(img * 255, dtype=np.uint8)

                if x.shape[0] == 4:
                    img_depth = x[3].numpy()
                    img_depth = cv.applyColorMap((img_depth * 255).astype(np.uint8), cv.COLORMAP_COOL)
                    img = np.hstack([img, img_depth])

                cv.imshow('img', img)
                cv.waitKey(30)
    pass


    k400 = Kinetics('train', num_threads=2, cache_dir='/Volumes/USB-Freigabe/KINETICS400')#cache_dir='/Volumes/ROBERT512GB/KINETICS400')

    for i, (X, T) in enumerate(k400):
        print(i)
        pass