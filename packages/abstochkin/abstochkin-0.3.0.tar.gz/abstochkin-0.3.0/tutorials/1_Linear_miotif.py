#  Copyright (c) 2025, Alex Plakantonakis.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from abstochkin import AbStochKin
from abstochkin.process import Process, RegulatedProcess

k_b = 0.02
k_d = 0.02
k_s = 1

S_max = 20

t_max = 100
dt = 0.02

reps = 1

# Simulation parameters for S = 0
simulation_params = [
    dict(processes=[
        Process.from_string(" -> R", k=k_b),
        Process.from_string("R -> ", k=k_d)
    ],
        p0={"R": 0},
        t_max=t_max,
        dt=dt,
        n=reps)
]

for s in range(1, S_max + 1):
    procs = [
        Process.from_string(" -> R", k=k_b),
        RegulatedProcess.from_string(" -> R", k=k_s, regulating_species='S', K50=1, nH=1, alpha=1 + s - 1 / s),
        Process.from_string("R -> ", k=k_d)
    ]
    simulation_params.append(dict(processes=procs, p0={'S': s, "R": 0}, t_max=t_max, dt=dt, n=reps))

linear_SR = AbStochKin()
linear_SR.simulate_series_in_parallel(simulation_params)
