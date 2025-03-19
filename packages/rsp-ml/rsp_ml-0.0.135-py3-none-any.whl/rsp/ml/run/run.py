from datetime import datetime
from torch.utils.data import DataLoader
from glob import glob
from pathlib import Path
from tqdm import tqdm
import numpy as np
import json
import matplotlib.pyplot as plt
import pickle as pkl
import copy
import torch
import torch.nn as nn
import pandas as pd

try:
    import rsp.common.console as console
except Exception as e:
    print(e)

#__example__ from rsp.ml.run import Run
#__example__ import rsp.ml.metrics as m
#__example__
#__example__ metrics = [
#__example__     m.top_1_accuracy
#__example__ ]
#__example__ config = {
#__example__     m.top_1_accuracy.__name__: {
#__example__         'ymin': 0,
#__example__         'ymax': 1
#__example__     }
#__example__ }
#__example__ run = Run(id='run0001', metrics=metrics, config=config, ignore_outliers_in_chart_scaling=True)
#__example__
#__example__ for epoch in range(100):
#__example__     """here goes some training code, giving us inputs, predictions and targets"""
#__example__     acc = m.top_1_accuracy(predictions, targets)
#__example__     run.append(m.top_1_accuracy.__name__, 'train', acc)
class Run():
    """
    Run class to store and manage training
    """
    def __init__(
            self,
            id = None,
            moving_average_epochs = 1,
            metrics = None,
            device:str = None,
            ignore_outliers_in_chart_scaling:bool = False,
            config:dict = {}
        ):
        """
        Run class to store and manage training

        Parameters:
        ----------
        id : str, default = None
            Id of the run. If None, a new id is generated
        moving_average_epochs : int, default = 1
            Number of epochs to average over
        metrics : list, default = None
            List of metrics to compute. Each metric should be a function that takes Y and T as input.
        device : str, default = None
            torch device to run on
        ignore_outliers_in_chart_scaling : bool, default = False
            Ignore outliers when scaling charts
        config : dict, default = {}
            Configuration dictionary. Keys are metric names and values are dictionaries with keys 'ymin' and 'ymax'
        """
        if id is None:
            self.id = datetime.now().strftime('%Y%m%d%H%M%S%f')
            self.data = {
                'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            }
        else:
            self.id = id

        self.metrics = metrics
        self.ignore_outliers_in_chart_scaling = ignore_outliers_in_chart_scaling
        self.config = config
        self.config['time'] = {'ymin': 0}

        if device is None:
            if torch.cuda.is_available():
                self.device = 'cuda'
            elif torch.backends.mps.is_available():
                self.device = 'mps'
            else:
                self.device = 'cpu'
        else:
            self.device = device
            
        self.moving_average_epochs = moving_average_epochs
        self.__init_run_dir__()
        self.__load__()
    
    def append(self, key:str, phase:str, value:float):
        """
        Append value to key in phase.

        Parameters:
        ----------
        key : str
            Key to append to
        phase : str
            Phase to append to
        value : float
            Value to append
        """
        mavg_epochs = self.moving_average_epochs if self.moving_average_epochs > 0 else 1
        if not key in self.data:
            self.data[key] = {}
        if not phase in self.data[key]:
            self.data[key][phase] = {
                'val': [],
                'avg': []
            }
        if np.isnan(value):
            if len(self.data[key][phase]['val']) > 0:
                value = self.data[key][phase]['val'][-1]
            else:
                value = 0.

        self.data[key][phase]['val'].append(value)
        self.data[key][phase]['avg'].append(np.average(self.data[key][phase]['val'][-mavg_epochs:]))

    def plot(self):
        """
        Plot all keys to runs/{id}/plot/{key}.jpg
        """
        self.__init_run_dir__()

        def get_outlier_fence(data):
            df = pd.DataFrame({'data': data})
            q1 = df['data'].quantile(0.25)
            q3 = df['data'].quantile(0.75)
            iqr = q3 - q1
            fence_low = q1 - 1.2 * iqr
            fence_high = q3 + 1.2 * iqr
            return fence_low, fence_high

        for key in self.data:
            if key == 'start_time':
                continue
            key_str = key.replace('_', ' ')
            plot_file = self.directory_plot.joinpath(f'{key}.jpg')

            cmap = plt.get_cmap('tab20b')
            colors = cmap(np.linspace(0, 1, len(self.data[key])))

            ymin, ymax = 1e10, 0.
            for i, phase in enumerate(self.data[key]):
                if len(self.data[key][phase]['val']) == 0:
                    continue

                if self.ignore_outliers_in_chart_scaling:
                    val_fence = get_outlier_fence(self.data[key][phase]['val'])
                    avg_fence = get_outlier_fence(self.data[key][phase]['avg'])
                    ymin = min(ymin, min(val_fence[0], avg_fence[0]))
                    ymax = max(ymax, max(val_fence[1], avg_fence[1]))

                plt.plot(self.data[key][phase]['val'], color=colors[i], alpha=0.3 if key != 'time' else 1)
                if key != 'time':
                    plt.plot(self.data[key][phase]['avg'], label=phase, color=colors[i])

            #region chart scaling
            if not self.ignore_outliers_in_chart_scaling:
                _, _, ymin, ymax = plt.axis()

            if key in self.config:
                if 'ymin' in self.config[key]:
                    ymin = self.config[key]['ymin']
                if 'ymax' in self.config[key]:
                    ymax = self.config[key]['ymax']
            plt.ylim(ymin, ymax)
            #endregion

            plt.title(key_str)
            plt.xlabel('episode')
            if key == 'time':
                plt.ylabel(f'{key_str} [h]')
            elif key == 'time_per_sample':
                plt.ylabel(f'{key_str} [s]')
            else:
                plt.ylabel(key_str)
            
            plt.minorticks_on()
            plt.grid(which='minor', color='lightgray', linewidth=0.2)
            plt.grid(which='major', linewidth=.6)
            if key != 'time':
                plt.legend()
            plt.savefig(plot_file)
            plt.close()

    def recalculate_moving_average(self):
        """
        Recalculate moving average
        """
        mavg_epochs = self.moving_average_epochs if self.moving_average_epochs > 0 else 1
        for key in self.data:
            if key == 'start_time':
                continue
            for phase in self.data[key]:
                for i in range(len(self.data[key][phase]['val'])):
                    s_i = 0 if i + 1 - mavg_epochs < 0 else i + 1 - mavg_epochs
                    e_i = i + 1
                    test = self.data[key][phase]['val'][s_i:e_i]
                    self.data[key][phase]['avg'][i] = np.average(self.data[key][phase]['val'][s_i:e_i])
                self.data[key][phase]['avg'] = self.data[key][phase]['avg'][:len(self.data[key][phase]['val'])]

    def train_epoch(
            self,
            dataloader:DataLoader,
            model:torch.nn.Module,
            optimizer:torch.optim.Optimizer,
            criterion:torch.nn.Module,
            num_batches:int = None,
            return_YT:bool = False
        ):
        """
        Train one epoch.

        Parameters:
        ----------
        dataloader : DataLoader
            DataLoader to train on
        model : torch.nn.Module
            Model to train
        optimizer : torch.optim.Optimizer
            Optimizer to use
        criterion : torch.nn.Module
            Criterion to use
        num_batches : int, default = None
            Number of batches to train on. If None, train on all batches
        return_YT : bool, default = False
            Append Y and T to results
        
        Returns:
        -------
        results : dict
            Dictionary with results
        """
        results = self.__compute__(
            model = model,
            optimizer = optimizer,
            criterion = criterion,
            dataloader = dataloader,
            train = True,
            num_batches = num_batches,
            return_XYT = return_YT)
        for key in results:
            if key == 'X' or key == 'Y' or key == 'T':
                continue
            self.append(key, phase = 'train', value = results[key])

        return results
    
    def validate_epoch(
            self,
            dataloader:DataLoader,
            model:torch.nn.Module,
            optimizer:torch.optim.Optimizer,
            criterion:torch.nn.Module,
            num_batches:int = None,
            return_YT:bool = False
        ):
        """
        Validate one epoch.

        Parameters:
        ----------
        dataloader : DataLoader
            DataLoader to validate on
        model : torch.nn.Module
            Model to validate
        optimizer : torch.optim.Optimizer
            Optimizer to use
        criterion : torch.nn.Module
            Criterion to use
        num_batches : int, default = None
            Number of batches to validate on. If None, validate on all batches
        return_YT : bool, default = False
            Append Y and T to results

        Returns:
        -------
        results : dict
            Dictionary with results
        """
        results = self.__compute__(
            model = model,
            optimizer = optimizer,
            criterion = criterion,
            dataloader = dataloader,
            train = False,
            num_batches = num_batches,
            return_XYT = return_YT)
        for key in results:
            if key == 'X' or key == 'Y' or key == 'T':
                continue
            self.append(key, phase = 'val', value = results[key])

        return results

    def __compute__(
            self,
            model:nn.Module,
            optimizer:torch.optim.Optimizer,
            criterion:nn.Module,
            dataloader:DataLoader,
            num_batches:int,
            train:bool,
            return_XYT:bool = False
        ):
        start = datetime.now()
        iterator = iter(dataloader)
        if num_batches is None or hasattr(dataloader.dataset, '__len__') and num_batches > len(dataloader):
            num_batches = len(dataloader)
        if num_batches is None:
            num_batches = 1e10
        
        results = {
            'loss': []
        }
        if return_XYT:
            results['Y'] = []
            results['X'] = []
            results['T'] = []

        progress = tqdm(range(num_batches), desc='train' if train else 'val', total=num_batches, leave=False)
        for i in progress:
            if i >= num_batches:
                break
            
            try:
                X, T = next(iterator)
            except:
                break
            X:torch.Tensor = X.to(self.device)
            T:torch.Tensor = T.to(self.device)

            if train:
                optimizer.zero_grad()
                model.train()
                Y = model(X)
            else:
                model.eval()
                with torch.no_grad():
                    Y = model(X)
            
            loss:torch.Tensor = criterion(Y, T)

            for metric in self.metrics:
                val = metric(Y, T)
                if metric.__name__ not in results:
                    results[metric.__name__] = []
                results[metric.__name__].append(val)
            
            if train:
                loss.backward()
                optimizer.step()

            results['loss'].append(loss.item())
            if return_XYT:
                results['X'].append(X.detach())
                results['Y'].append(Y.detach())
                results['T'].append(T.detach())
        
        for key in results:
            if key == 'X' or key == 'Y' or key == 'T':
                results[key] = torch.cat(results[key], dim=0)
            else:
                results[key] = np.average(results[key])
        
        results['time'] = (datetime.now() - datetime.strptime(self.data['start_time'], '%Y-%m-%d %H:%M:%S.%f')).total_seconds() / 3600
        results['time_per_sample'] = (datetime.now() - start).total_seconds() / len(dataloader.dataset) / dataloader.batch_size

        self.epoch = self.len()

        return results

    def save(self):
        """
        Save data to runs/{id}/data.json
        """
        self.__init_run_dir__()
        with open(f'runs/{self.id}/data.json', 'w') as f:
            json.dump(self.data, f)

    def get_val(self, key:str, phase:str):
        """
        Get last value of key in phase

        Parameters:
        ----------
        key : str
            Key to get
        phase : str
            Phase to get from
        
        Returns:
        -------
        value : float
            Last value of key in phase. If key is not in data, returns np.nan
        """
        if key not in self.data:
            return np.nan
        return self.data[key][phase]['val'][-1]
    
    def get_avg(self, key:str, phase:str):
        """
        Get last average value of key in phase

        Parameters:
        ----------
        key : str
            Key to get
        phase : str
            Phase to get from
        
        Returns:
        -------
        value : float
            Last average value of key in phase. If key is not in data, returns np.nan
        """
        if key not in self.data:
            return np.nan
        return self.data[key][phase]['avg'][-1]
    
    def len(self):
        """
        Get length of longest phase
        """
        l = 0
        for key in self.data:
            if key == 'start_time':
                continue
            for phase in self.data[key]:
                l_temp = len(self.data[key][phase]['val'])
                if l_temp > l:
                    l = l_temp
        return l

    def __init_run_dir__(self):
        self.__directory_runs__ = Path('runs')
        self.__directory_runs__.mkdir(parents=True, exist_ok=True)

        self.directory = self.__directory_runs__.joinpath(self.id)
        self.directory.mkdir(parents=True, exist_ok=True)

        self.directory_plot = self.directory.joinpath('plot')
        self.directory_plot.mkdir(parents=True, exist_ok=True)

        self.file_data = self.directory.joinpath('data.json')

    def __load__(self):
        if self.file_data.exists():
            self.data = json.load(self.file_data.open('r'))
        else:
            self.data = {}
            self.data['start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.epoch = self.len()

    def __best_state_dict__(self, fname:str, id:str, suffix:str):
        sd_files = glob(f'{self.directory}/*{id}*{suffix}')

        best_acc = 0, None
        for sd_file in sd_files:
            if not '_acc' in sd_file:
                continue
            s_i = sd_file[:-len(suffix)].find('_acc') + 4
            acc = float(sd_file[s_i:-len(suffix)])
            if acc > best_acc[0]:
                best_acc = acc, Path(sd_file).name
        return best_acc

    def save_state_dict(self, state_dict, fname = 'state_dict.pt'):
        """
        Save state_dict to runs/{id}/{fname}

        Parameters:
        ----------
        state_dict : dict
            State dict to save
        fname : str, default = 'state_dict.pt'
            Filename to save to
        """
        self.__init_run_dir__()
        sd = copy.deepcopy(state_dict)
        for k, v in sd.items():
            if hasattr(v, 'cpu'):
                sd[k] = v.cpu()

        file_state_dict = self.directory.joinpath(fname)
        with file_state_dict.open('wb') as f:
            torch.save(sd, f)

    def save_best_state_dict(self, state_dict, new_acc:float, fname = 'state_dict.pt'):
        """
        Save state_dict if new_acc is better than previous best

        Parameters:
        ----------
        state_dict : dict
            State dict to save
        new_acc : float
            New accuracy
        epoch : int, default = None
            Epoch to save
        fname : str, default = 'state_dict.pt'
            Filename to save to
        """
        file_state_dict = self.directory.joinpath(fname)
        suffix = file_state_dict.suffix
        id = file_state_dict.name[:-len(suffix)]
        
        best_acc, best_file = self.__best_state_dict__(fname, id, suffix)

        if new_acc > best_acc:
            fname = f'{id}_e{self.epoch}_acc{new_acc:0.8f}{suffix}'
            self.save_state_dict(state_dict, fname)

    def load_state_dict(self, model:torch.nn.Module, fname = None):
        """
        Load state_dict from runs/{id}/{fname}

        Parameters:
        ----------
        model : torch.nn.Module
            Model to load state_dict into
        fname : str, default = None
            Filename to load from
        """
        if fname is None:
            fname = 'state_dict.pt'
        file_state_dict = self.directory.joinpath(fname)
        if file_state_dict.exists():
            with file_state_dict.open('rb') as f:
                model.load_state_dict(torch.load(f, weights_only = False))
        else:
            try:
                console.warn(f'File runs/{self.id}/{fname} not found.')
            except:
                print(f'File runs/{self.id}/{fname} not found.')
            return
        
    def load_best_state_dict(self, model:torch.nn.Module, fname = 'state_dict.pt', verbose:bool = False):
        """
        Load best state_dict from runs/{id}/{fname}

        Parameters:
        ----------
        model : torch.nn.Module
            Model to load state_dict into
        fname : str, default = 'state_dict.pt'
            Filename to load from
        verbose : bool, default = False
            Print loaded file
        """
        file_state_dict = self.directory.joinpath(fname)
        suffix = file_state_dict.suffix
        id = file_state_dict.name[:-len(suffix)]
        
        best_acc, best_file = self.__best_state_dict__(fname, id, suffix)
        if best_file is not None:
            self.load_state_dict(model, best_file)
            if not verbose:
                try:
                    console.success(f'Loaded {best_file}')
                except:
                    print(f'Loaded {best_file}')

    def pickle_dump(self, model:torch.nn.Module, fname = 'model.pkl'):
        """
        Pickle model to runs/{id}/{fname}

        Parameters:
        ----------
        model : torch.nn.Module
            Model to pickle
        fname : str, default = 'model.pkl'
            Filename to save to
        """
        self.__init_run_dir__()

        file_pkl = self.directory.joinpath(fname)
        with file_pkl.open('wb') as f:
            pkl.dump(model, f)

    def pickle_load(self, fname = 'model.pkl'):
        """
        Load model from runs/{id}/{fname}

        Parameters:
        ----------
        fname : str, default = 'model.pkl'
            Filename to load from
        """
        file_pkl = self.directory.joinpath(fname)
        if file_pkl.exists():
            with open(file_pkl, 'rb') as f:
                model = pkl.load(f)
        else:
            try:
                console.warn(f'File runs/{self.id}/{fname} not found.')
            except:
                print(f'File runs/{self.id}/{fname} not found.')
            return
        return model
    
if __name__ == '__main__':
    t1 = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
    test = datetime.strptime('2025-02-28 14:31:23.3234', '%Y-%m-%d %H:%M:%S.%f')

    run = Run('test')
    run.save_best_state_dict(torch.nn.Linear(10, 10).state_dict(), 0.919342, 80)
    run.save_best_state_dict(torch.nn.Linear(10, 10).state_dict(), 0.899342, 81)
    run.save_best_state_dict(torch.nn.Linear(10, 10).state_dict(), 0.999342, 82)

    run.load_best_state_dict(torch.nn.Linear(10, 10))
    pass