# Copyright 2022-2023 OmniSafe Team. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Implementation of the Saute version of the TRPO algorithm."""


from omnisafe.adapter.saute_adapter import SauteAdapter
from omnisafe.algorithms import registry
from omnisafe.algorithms.on_policy.base.trpo import TRPO
from omnisafe.utils import distributed


@registry.register
class TRPOSaute(TRPO):
    """The Saute version of the TRPO algorithm.

    A simple combination of the Saute RL and the Trust Region Policy Optimization algorithm.

    References:
        - Title: Saute RL: Almost Surely Safe Reinforcement Learning Using State Augmentation
        - Authors: Aivar Sootla, Alexander I. Cowen-Rivers, Taher Jafferjee, Ziyan Wang,
            David Mguni, Jun Wang, Haitham Bou-Ammar.
        - URL: `TRPOSaute <https://arxiv.org/abs/2202.06558>`_
    """

    def _init_env(self) -> None:
        """Initialize the environment.

        OmniSafe uses :class:`omnisafe.adapter.SauteAdapter` to adapt the environment to the algorithm.

        User can customize the environment by inheriting this method.

        Examples:
            >>> def _init_env(self) -> None:
            ...     self._env = CustomAdapter()
        """
        self._env: SauteAdapter = SauteAdapter(
            self._env_id,
            self._cfgs.train_cfgs.vector_env_nums,
            self._seed,
            self._cfgs,
        )
        assert (self._cfgs.algo_cfgs.steps_per_epoch) % (
            distributed.world_size() * self._cfgs.train_cfgs.vector_env_nums
        ) == 0, 'The number of steps per epoch is not divisible by the number of environments.'
        self._steps_per_epoch: int = (
            self._cfgs.algo_cfgs.steps_per_epoch
            // distributed.world_size()
            // self._cfgs.train_cfgs.vector_env_nums
        )

    def _init_log(self) -> None:
        """Log the TRPOSaute specific information.

        +------------------+-----------------------------------+
        | Things to log    | Description                       |
        +==================+===================================+
        | Metrics/EpBudget | The safety budget of the episode. |
        +------------------+-----------------------------------+
        """
        super()._init_log()
        self._logger.register_key('Metrics/EpBudget')
