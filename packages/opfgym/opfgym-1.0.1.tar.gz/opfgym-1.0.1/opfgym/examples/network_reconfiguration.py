""" Simple example that shows how to use switches and transformer tap changers
as actuators for network reconfiguration and voltage control.
Notice that the discrete settings are implemented as continuous RL actions,
which requires RL algorithms like DDPG, TD3, SAC, PPO, etc.
Warning: This environment is not solvable with the pandapower OPF.
Also, it is only an example with arbitrary objective and actuators. """


import numpy as np
import pandapower as pp

from opfgym import opf_env
from opfgym.simbench.build_simbench_net import build_simbench_net


class NetworkReconfiguration(opf_env.OpfEnv):
    def __init__(self, simbench_network_name='1-HV-urban--0-sw',
                 controllable_switch_idxs=(1, 3),
                 *args, **kwargs):
        self.controllable_switch_idxs = np.array(controllable_switch_idxs)

        net, profiles = self._define_opf(
            simbench_network_name, *args, **kwargs)

        # Define the RL problem
        # Observe all load power values, sgen active power
        obs_keys = [
            ('sgen', 'p_mw', net.sgen.index),
            ('load', 'p_mw', net.load.index),
            ('load', 'q_mvar', net.load.index),
        ]

        # ... and control some selected switches in the system
        act_keys = [('switch', 'closed', net.switch.index[net.switch.controllable]),
                    ('trafo', 'tap_pos', net.trafo.index[net.trafo.controllable])]

        super().__init__(net, act_keys, obs_keys, profiles=profiles,
                         optimal_power_flow_solver=False, *args, **kwargs)

    def _define_opf(self, simbench_network_name, *args, **kwargs):
        net, profiles = build_simbench_net(
            simbench_network_name, *args, **kwargs)

        # Add additional column to the network that states which switches are controllable
        net.switch.loc[:, 'controllable'] = False
        net.switch.loc[self.controllable_switch_idxs, 'controllable'] = True
        # Define the maximum and minimum values of the switches (action constraints)
        # In the current state
        net.switch['min_closed'] = 0
        net.switch['max_closed'] = 1
        # And overall (technical limit)
        net.switch['min_min_closed'] = 0
        net.switch['max_max_closed'] = 1

        # Define the transformer tap positions as controllable
        net.trafo['controllable'] = True
        net.trafo['min_tap_pos'] = -1
        net.trafo['max_tap_pos'] = 1
        net.trafo['min_min_tap_pos'] = -1
        net.trafo['max_max_tap_pos'] = 1

        # Set everything else to uncontrollable
        for unit_type in ('load', 'sgen', 'gen', 'storage'):
            net[unit_type]['controllable'] = False

        # Objective: Minimize the active power losses
        for idx in net.ext_grid.index:
            pp.create_poly_cost(net, idx, 'ext_grid', cp1_eur_per_mw=1)

        return net, profiles


if __name__ == '__main__':
    env = NetworkReconfiguration()
    for _ in range(5):
        env.reset()
        env.step(env.action_space.sample())
