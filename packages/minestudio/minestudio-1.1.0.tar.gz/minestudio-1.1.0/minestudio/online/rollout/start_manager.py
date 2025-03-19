from numpy import roll
from omegaconf import OmegaConf
import hydra
import logging
from minestudio.online.rollout.rollout_manager import RolloutManager
from minestudio.online.utils.rollout import get_rollout_manager
import ray
import wandb
import uuid
import torch

def start_rolloutmanager(policy_generator, env_generator, online_cfg):
    ray.init(address="localhost:9899", ignore_reinit_error=True, namespace="online")
    logger = logging.getLogger("Main")
    torch.backends.cudnn.benchmark = False # type: ignore

    rollout_manager = get_rollout_manager()
    rollout_manager_kwargs = dict(
        policy_generator = policy_generator,
        env_generator = env_generator,
        resume = online_cfg.train_config.resume,
        discount=online_cfg.train_config.discount,
        use_normalized_vf=online_cfg.train_config.use_normalized_vf,
        **online_cfg.rollout_config
    )

    print("rollout_manager_kwargs", rollout_manager_kwargs)
    if rollout_manager is not None:
        if (ray.get(rollout_manager.get_saved_config.remote()) != rollout_manager_kwargs):
            logger.warning("Rollout manager config changed, killing and restarting rollout manager")
            ray.kill(rollout_manager)
            rollout_manager = None
        else:
            logger.info("Reusing existing rollout manager")

    if rollout_manager is None:
        if online_cfg.detach_rollout_manager:
            rollout_manager = RolloutManager.options(name="rollout_manager", lifetime="detached").remote(**rollout_manager_kwargs) # type: ignore
        else :
            rollout_manager = RolloutManager.options(name="rollout_manager").remote(**rollout_manager_kwargs) # type: ignore
        ray.get(rollout_manager.start.remote())

if __name__ == "__main__":
    logger = logging.getLogger("Main")
    logger.info("Starting rollout manager")
    start_rolloutmanager(None, None, None)
    logger.info("Rollout manager started")
    ray.shutdown()
    logger.info("Ray shutdown")