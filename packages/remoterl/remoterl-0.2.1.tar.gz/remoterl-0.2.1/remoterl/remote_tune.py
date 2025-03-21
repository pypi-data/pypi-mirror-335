# remote_tune.py
import gymnasium
# Set the Gymnasium logger to only show errors
gymnasium.logger.min_level = gymnasium.logger.WARN
gymnasium.logger.warn = lambda *args, **kwargs: None

from ray import tune
from typing import Callable

class CustomGymEnv:
    env_creator = gymnasium  # Default to the gymnasium module
    
    @staticmethod
    def make(name: str, **kwargs):
        # Use the env_creator's make method to create the environment.
        env = CustomGymEnv.env_creator.make(name, **kwargs)
        return env

    @staticmethod
    def make_vec(name: str, num_envs, **kwargs):
        # Use the env_creator's make_vec method to create a vectorized environment.
        env = CustomGymEnv.env_creator.make_vec(name, num_envs=num_envs, **kwargs)
        return env

def register_env(name: str, env_creator: Callable):
    CustomGymEnv.env_creator = env_creator
    tune.register_env(name, CustomGymEnv)