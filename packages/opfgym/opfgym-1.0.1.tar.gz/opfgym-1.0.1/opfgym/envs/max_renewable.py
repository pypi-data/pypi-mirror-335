
import pandapower as pp

from opfgym import opf_env
from opfgym.simbench.build_simbench_net import build_simbench_net


class MaxRenewable(opf_env.OpfEnv):
    """
    The goal is to learn to set active power of the biggest generators and
    storage systems to maximize active power feed-in to the external grid.

    Actuators: Active/reactive power of the bigger generators and storages.

    Sensors: Active+reactive power of all loads; max active power of all gens;
        active power of non-controllable storages.

    Objective: Maximize active power feed-in to external grid.

    Constraints: Voltage band, line/trafo load, min/max active power limits
        (automatically considered).
    """

    def __init__(self, simbench_network_name='1-HV-mixed--1-sw',
                 gen_scaling=0.8, load_scaling=0.8,
                 min_storage_power=10, min_sgen_power=24,
                 *args, **kwargs):

        self.min_sgen_power = min_sgen_power
        self.min_storage_power = min_storage_power

        net, profiles = self._define_opf(
            simbench_network_name, gen_scaling=gen_scaling,
            load_scaling=load_scaling, *args, **kwargs)

        # Define the RL problem
        # See all load power values, sgen max active power...
        obs_keys = [
            ('sgen', 'max_p_mw', net.sgen.index),
            ('load', 'p_mw', net.load.index),
            ('load', 'q_mvar', net.load.index),
            ('storage', 'p_mw', net.storage.index[~net.storage.controllable])
        ]

        # TODO: This is a workaround. Better would be to have identical obs and state keys.
        state_keys = [
            ('sgen', 'p_mw', net.sgen.index),
            ('load', 'p_mw', net.load.index),
            ('load', 'q_mvar', net.load.index),
            ('storage', 'p_mw', net.storage.index[~net.storage.controllable])
        ]

        # ... and control all sgens' active power values + some storage systems
        act_keys = [
            ('sgen', 'p_mw', net.sgen.index[net.sgen.controllable]),
            ('storage', 'p_mw', net.storage.index[net.storage.controllable])
        ]

        super().__init__(net, act_keys, obs_keys, state_keys=state_keys,
                         profiles=profiles,
                         *args, **kwargs)

    def _define_opf(self, simbench_network_name, *args, **kwargs):
        net, profiles = build_simbench_net(
            simbench_network_name, *args, **kwargs)

        # Drop redundant ext grids (results in problems with OPF)
        if len(net.ext_grid) > 1:
            net.ext_grid = net.ext_grid.iloc[0:1]

        # Less strict constraint than default (otherwise, too restrictive)
        net.trafo['max_loading_percent'] = 100

        net.load['controllable'] = False
        net.ext_grid['vm_pu'] = 1.0

        # Use sampled data for the non-controlled storage systems
        net.storage['controllable'] = net.storage.max_max_p_mw > self.min_storage_power
        net.storage['q_mvar'] = 0.0
        net.storage['max_q_mvar'] = 0.0
        net.storage['min_q_mvar'] = 0.0
        # Assume that storage systems are completely usable
        # (for example, do not consider state of charge)
        net.storage['max_p_mw'] = net.storage['max_max_p_mw']
        net.storage['min_p_mw'] = net.storage['min_min_p_mw']

        net.sgen['controllable'] = net.sgen.max_max_p_mw > self.min_sgen_power
        net.sgen['min_p_mw'] = 0.0  # max will be set later in sampling
        net.sgen['q_mvar'] = 0.0
        net.sgen['max_q_mvar'] = 0.0
        net.sgen['min_q_mvar'] = 0.0

        # OPF objective: Maximize active power feed-in to external grid
        active_power_costs = 30/1000  # /1000 to achieve smaller scale
        for idx in net.sgen.index:
            pp.create_poly_cost(net, idx, 'sgen',
                                cp1_eur_per_mw=-active_power_costs)

        return net, profiles

    def _sampling(self, *args, **kwargs):
        super()._sampling(*args, **kwargs)

        # Set constraints of current time step (required for pandapower OPF)
        self.net.sgen['max_p_mw'] = self.net.sgen.p_mw * self.net.sgen.scaling + 1e-6


if __name__ == '__main__':
    env = MaxRenewable()
    print('Max renewable environment created')
    print('Number of buses: ', len(env.net.bus))
    print('Observation space:', env.observation_space.shape)
    print('Action space:', env.action_space.shape, f'(Generators: {sum(env.net.sgen.controllable)}, Storage: {sum(env.net.storage.controllable)})')
