""" Integration tests for all example environments. """

import numpy as np

from opfgym.examples import *
from .sanity_check import env_sanity_check


def test_custom_constraint_integration():
    dummy_env = AddCustomConstraint()
    for _ in range(3):
        dummy_env.reset()
        act = dummy_env.action_space.sample()
        obs, reward, terminated, truncated, info = dummy_env.step(act)

    assert isinstance(obs, np.ndarray)
    assert isinstance(reward, float)
    assert terminated
    assert isinstance(info, dict)
    assert env_sanity_check(dummy_env)
    # Not solvable with the pandapower OPF
    assert not dummy_env.run_optimal_power_flow()

def test_constraint_satisfaction_integration():
    dummy_env = ConstraintSatisfaction()
    for _ in range(3):
        dummy_env.reset()
        act = dummy_env.action_space.sample()
        obs, reward, terminated, truncated, info = dummy_env.step(act)

    assert isinstance(obs, np.ndarray)
    assert isinstance(reward, float)
    assert terminated
    assert isinstance(info, dict)
    assert env_sanity_check(dummy_env)

def test_stochastic_obs_integration():
    dummy_env = StochasticObs()
    for _ in range(3):
        dummy_env.reset()
        act = dummy_env.action_space.sample()
        obs, reward, terminated, truncated, info = dummy_env.step(act)

    assert isinstance(obs, np.ndarray)
    assert isinstance(reward, float)
    assert terminated
    assert isinstance(info, dict)
    assert env_sanity_check(dummy_env)

def test_security_constrained_integration():
    dummy_env = SecurityConstrained()
    for _ in range(3):
        dummy_env.reset()
        act = dummy_env.action_space.sample()
        obs, reward, terminated, truncated, info = dummy_env.step(act)

    assert isinstance(obs, np.ndarray)
    assert isinstance(reward, float)
    assert terminated
    assert isinstance(info, dict)
    assert env_sanity_check(dummy_env)
    # Not solvable with the pandapower OPF
    assert not dummy_env.run_optimal_power_flow()

def test_mixed_act_integration():
    dummy_env = MixedContinuousDiscrete()
    for _ in range(3):
        dummy_env.reset()
        act = dummy_env.action_space.sample()
        obs, reward, terminated, truncated, info = dummy_env.step(act)

    assert isinstance(obs, np.ndarray)
    assert isinstance(reward, float)
    assert terminated
    assert isinstance(info, dict)
    assert env_sanity_check(dummy_env)
    # Not solvable with the pandapower OPF
    assert not dummy_env.run_optimal_power_flow()

def test_partial_obs_integration():
    dummy_env = PartiallyObservable()
    for _ in range(3):
        dummy_env.reset()
        act = dummy_env.action_space.sample()
        obs, reward, terminated, truncated, info = dummy_env.step(act)

    assert isinstance(obs, np.ndarray)
    assert isinstance(reward, float)
    assert terminated
    assert isinstance(info, dict)
    assert env_sanity_check(dummy_env)


def test_net_reconfig_integration():
    dummy_env = NetworkReconfiguration()
    for _ in range(3):
        dummy_env.reset()
        act = dummy_env.action_space.sample()
        obs, reward, terminated, truncated, info = dummy_env.step(act)

    assert isinstance(obs, np.ndarray)
    assert isinstance(reward, float)
    assert terminated
    assert isinstance(info, dict)
    assert env_sanity_check(dummy_env)
    # Not solvable with the pandapower OPF
    assert not dummy_env.run_optimal_power_flow()


def test_multi_stage_integration():
    dummy_env = MultiStageOpf()
    for _ in range(3):
        dummy_env.reset()
        terminated, truncated = (False, False)
        while not terminated and not truncated:
            act = dummy_env.action_space.sample()
            obs, reward, terminated, truncated, info = dummy_env.step(act)

    assert isinstance(obs, np.ndarray)
    assert isinstance(reward, float)
    assert isinstance(info, dict)
    assert env_sanity_check(dummy_env)
    # Not solvable with the pandapower OPF
    assert not dummy_env.run_optimal_power_flow()


def test_non_simbench_integration():
    dummy_env = NonSimbenchNet()
    for _ in range(3):
        dummy_env.reset()
        act = dummy_env.action_space.sample()
        obs, reward, terminated, truncated, info = dummy_env.step(act)

    assert isinstance(obs, np.ndarray)
    assert isinstance(reward, float)
    assert terminated
    assert isinstance(info, dict)
    assert env_sanity_check(dummy_env)
