from Components import Component
from Powertrain_env import Powertrain
from Helpers import *
import Characteristics

import time
import random
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
import torch
import torch.nn as nn

import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update({
    'axes.titlesize': 14,
    'axes.labelsize': 24,
    'xtick.labelsize': 24,
    'ytick.labelsize': 24,
    'legend.fontsize': 14
})

from stable_baselines3 import SAC
from stable_baselines3.common.utils import set_random_seed, get_latest_run_id
from stable_baselines3.common.logger import configure
from stable_baselines3.common.callbacks import BaseCallback

from Flightsim import ActionFeasibilityWrapper, FlightSimulation, set_seed

def SACtraining(env, directory, model_name, option, replay_name, seed, year):
    model_path = os.path.join(directory, 'Saved Models', model_name)
    device = 'cuda'
    if option == 'init':
        log_path = os.path.join(directory, 'Logs')
        layers = dict(net_arch=[256, 256, 256, 256], activation_fn=nn.LeakyReLU)
        model = SAC('MultiInputPolicy', env, seed=seed, device=device, policy_kwargs=layers, learning_starts=100000, verbose=1, tensorboard_log=log_path)
        model.learn(total_timesteps=100000)
        model.save(model_path)
        model.save_replay_buffer(os.path.join(directory, 'Saved Models', replay_name))
    elif option == 'train':
        env.training = True
        env.norm_reward = True
        learning_rate = 0.0001
        smoothing_coefficient = 0.01
        gradient_steps = 16
        batch_size = 2048
        train_freq = (1, "episode")
        model = SAC.load(model_path, env=env, seed=seed, device=device,  custom_objects={"buffer_size": 100000, "train_freq": train_freq, "gradient_steps": gradient_steps, "learning_rate": learning_rate, "tau": smoothing_coefficient, "batch_size": batch_size})

        model.load_replay_buffer(os.path.join(directory, "Saved Models", replay_name))

        print(model.policy)
        print(next(model.policy.parameters()).is_cuda)

        # 1. Force the model's internal schedule to the new value
        model.learning_rate = learning_rate
        model.lr_schedule = lambda _: learning_rate

        # 2. Update the actual PyTorch optimizers (Actor and Critic)
        # This forces the "0.0003" you saw in your printout to become "0.0001"
        for param_group in model.actor.optimizer.param_groups:
            param_group['lr'] = learning_rate

        for param_group in model.critic.optimizer.param_groups:
            param_group['lr'] = learning_rate

        # 3. Optional: If using automatic entropy, update that optimizer too
        if hasattr(model, 'ent_coef_optimizer') and model.ent_coef_optimizer is not None:
            for param_group in model.ent_coef_optimizer.param_groups:
                param_group['lr'] = learning_rate

        model.gamma = 0.99
        model.batch_size = batch_size
        model.learning_starts = 0
        model.gradient_steps = gradient_steps

        if seed == 1:
            print('Starting 10,000 steps for year:', year)
            model.learn(total_timesteps=10000)
            model_path = os.path.join(directory, 'Saved Models', f"{year}_v{seed+1}")
        elif seed == 2:
            print('Starting 20,000 steps for year:', year)
            model.learn(total_timesteps=20000)
            model_path = os.path.join(directory, 'Saved Models', f"{year}_v{seed+1}")
        elif seed == 3:
            print('Starting 40,000 steps for year:', year)
            model.learn(total_timesteps=40000)
            model_path = os.path.join(directory, 'Saved Models', f"{year}_v{seed+1}")
        elif seed == 4:
            print('Starting 80,000 steps for year:', year)
            model.learn(total_timesteps=80000)
            model_path = os.path.join(directory, 'Saved Models', f"{year}_v{seed+1}")
        elif seed == 5:
            print('Starting 150,000 steps for year:', year)
            model.learn(total_timesteps=150000)
            model_path = os.path.join(directory, 'Saved Models', f"{year}_v{seed+1}")
        model.save(model_path)
        model.save_replay_buffer(os.path.join(directory, 'Saved Models', replay_name))
    elif option == 'test':
        pt = Powertrain()
        pt_obs = pt.reset()
        pt_done = False
        while not pt_done:
            pt_action = pt.action_space.sample()
            obs, reward, pt_done, info = pt.step(pt_action)
        powerpaths, A_obj, components = pt.matrix()

        pt.describe()
        seeds = []
        rewards = []

        iterations = 1
        for i in range(0,iterations):
            if i%1000 == 0:
                print(i)
            seeds.append(i)
            obs = env.reset()
            done = False
            j=0
            while not done:
                action = env.action_space.sample()
                # for l in range(0, n_cp):
                #     action[l] = actions[n_cp * j + l]
                obs, reward, done, _, info = env.step(action)
                j+=1
            print(reward)
            rewards.append(reward)
        rewards = sorted(rewards)
        plt.figure(figsize=(10, 6))
        plt.scatter(seeds, rewards)
        plt.xlabel('Percentile')
        plt.ylabel('Reward')
        plt.grid()
        plt.tight_layout()
        plt.show()

def initialize_training(start_seed, end_seed, CARGO, FP2050, year, directory, test):
    CHARACTERISTICS = getattr(Characteristics, f"CHARACTERISTICS{year}")
    stopping = False
    for i in range(start_seed, end_seed+1):
        if year == 2030:
            time.sleep(30)
        elif year == 2040:
            time.sleep(60)
        elif year == 2050:
            time.sleep(90)
        else:
            raise ValueError('Wrong year')
        if stopping:
            break
        seed = i
        set_seed(seed)
        Component.set_characteristics(CHARACTERISTICS)
        env = ActionFeasibilityWrapper(FlightSimulation(CHARACTERISTICS, CARGO, FP2050))

        replay_name = f"{year}.pkl"
        if seed == 0:
            model_name = f"{year}_v{seed+1}"
            option = 'init'
        else:
            model_name = f"{year}_v{seed}"
            option = 'train'
        if test == True:
            option = 'test'
            stopping = True
            print('Testing')
        SACtraining(env, directory, model_name, option, replay_name, seed, year)

if __name__ == '__main__':
    initialize_training(0, 5, True, False, 2030, 'Training', False)