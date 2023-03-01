# -*- coding: utf-8 -*-
"""
@author: nicholasye
"""

import os
import sys

sys.path.append(os.getcwd())

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from src.components.electrical_component import (Capacitor, Inductor, Resistor, Switch, Diode, DC_Voltage_Source)
from src.components.electrical_dictionary_generate import generate_components_dict, generate_components_order
from src.components.electrical_matrix_generate import build_nodal_Y_matrix, build_Ih_nodal_matrix, build_Y_transfer_matrix, build_E_transfer_matrix, build_component_Y_matrix, build_component_U_matrix
from src.components.simulation_result_generate import generate_node_u_result, generate_component_i_result, generate_component_u_result, get_component_u, get_component_i


########## Simulation Parameter Setting

DeltaT: float = 5e-9  # Time interval
Start_time: float = 0.0  # Simulation presented start time
End_time: float = 0.0001  # Simulation presented end time


########## Circuit Component Parameter Setting

## Resistor
R1: Resistor = Resistor(R_name="R1", R_impedance=5)

## Inductor
L1: Inductor = Inductor(L_name="L1", L_impedance=0.000029, DeltaT=DeltaT)

## Capacitor
C1: Capacitor = Capacitor(C_name="C1", C_impedance=0.0000011, DeltaT=DeltaT)

## Vsource
V1: DC_Voltage_Source = DC_Voltage_Source(V_name="V1", V_voltage=48, V_IR=0.00001)

## Switch
S1: Switch = Switch(S_name="S1", S_impedance=1, DeltaT=DeltaT, S_frequency=1/500000, S_duty=0.5)

## Diode
D1: Diode = Diode(D_name="D1", D_impedance=0.8, D_character=1)

## Components_Order
components_list: list = [R1, L1, C1, V1, S1, D1]

## Generate a dictionary to store all the components and their characters
components_dict: dict = generate_components_dict(components_list)


########## Circuit Matrix Parameter Setting

## Initialize Buck Connecting Matrix
buck_connect_matrix: dict = {
    "U1": {"U1": 0, "U2": ["S1"], "U3": 0, "U4": ["V1"]},
    "U2": {"U1": 0, "U2": 0, "U3": ["L1"], "U4": ["D1"]},
    "U3": {"U1": 0, "U2": 0, "U3": 0, "U4": ["C1", "R1"]},
    "U4": {"U1": 0, "U2": 0, "U3": 0, "U4": 0},
}

circuit_connect_matrix: dict = buck_connect_matrix


########## Node Analysis Parameter Setting

## Define the total node number of the circuit.
node_number: int = len(circuit_connect_matrix)  # Number of nodes

## Build up nodal admittance matrix. And slice (node_number*node_number) matrix into (node_number-1*node_number-1) matrix then calculate the inverse matrix
nodal_Y: np.ndarray = build_nodal_Y_matrix(circuit_connect_matrix, components_dict, node_number)
nodal_Y_slice: np.ndarray = nodal_Y[:-1, :-1]
inv_nodal_Y_slice: np.ndarray = np.linalg.inv(nodal_Y_slice)

## node_V: Voltage matrix of circuit
node_V: np.ndarray = np.zeros((node_number-1, 1), dtype=np.float64)

## node_ih: History matrix of circuit of each element without resistor(cannot store current)
### The components should be element_dict without Resistor
### node_ih is used to store the current of each component in the circuit
components_order: list = generate_components_order(circuit_connect_matrix, node_number)
print(f"Components_order: {components_order}")

## Build up transfer matrix
ih_nodal_matrix: np.ndarray = build_Ih_nodal_matrix(circuit_connect_matrix, node_number, components_order)
ih_nodal_matrix_slice: np.ndarray = ih_nodal_matrix[:-1, :]

## Initialize the node_ih array
node_ih: np.ndarray = np.zeros((len(components_order), 1), dtype=np.float64)
## Update the initial value of node_ih
node_ih[0] = V1.history_current

## Y_transfer: Y transfer matrix of circuit for simulation
Y_transfer: np.ndarray = build_Y_transfer_matrix(circuit_connect_matrix, components_dict, node_number, components_order)
Y_transfer_slice: np.ndarray = Y_transfer[:, :-1]

## E_transfer: E transfer matrix of circuit for simulation
E_transfer: np.ndarray = build_E_transfer_matrix(components_dict, components_order)

## component_Y_matrix: Y matrix of circuit for calculating components currents
component_Y_matrix: np.ndarray = build_component_Y_matrix(circuit_connect_matrix, components_dict, node_number, components_order)
component_Y_matrix_slice: np.ndarray = component_Y_matrix[:, :-1]

## component_U_matrix: U transfer matrix of circuit for calculating components voltage
component_U_matrix = build_component_U_matrix(circuit_connect_matrix, node_number, components_order)
component_U_matrix_slice = component_U_matrix[:, :-1]

## Calculate the initial value
node_V = np.dot(inv_nodal_Y_slice, np.dot(ih_nodal_matrix_slice, node_ih))
component_i = np.dot(component_Y_matrix_slice, node_V) - node_ih
component_U = np.dot(component_U_matrix_slice, node_V)


########## Simulation Result Storage

result_nodes_V: list = []
result_node_ih: list = []
result_components_i: list = []
result_components_U: list = []


########## Simulation 

## Simulation equations
### node_ih[k] = Y_transfer_slice * node_V[k-1] + E_transfer * node_ih[k-1]
### node_V[k] = inv_nodal_Y_slice * ih_nodal_matrix_slice * node_ih[k]
### component_i[k] = component_Y_matrix_slice * node_V[k] - node_ih[k]
### component_U[k] = component_U_matrix_slice * node_V[k]

## Start simulation
for k in tqdm(range(int(End_time/DeltaT)), ascii=True, desc="Simulating"):
    # Update the all the switch status
    for key in components_list:
        ## Update the switch status depend on simulation time
        if key.name[0] == "S":
            components_dict[key.name][2] = key.update_character(k)
        ## Update the diode status depend on the voltage and current
        if key.name[0] == "D":
            u_D = get_component_u(component_U, components_order, key.name)
            i_D = get_component_i(component_i, components_order, key.name)
            components_dict[key.name][2] = key.update_character(u_D, i_D)

    # Update the Y_transfer_slice and E_transfer matrix
    Y_transfer = build_Y_transfer_matrix(circuit_connect_matrix, components_dict, node_number, components_order)
    Y_transfer_slice: np.ndarray = Y_transfer[:,:-1]
    E_transfer = build_E_transfer_matrix(components_dict, components_order)

    # Calculate ih(t) from t-1 status
    node_ih = np.dot(Y_transfer_slice, node_V) + np.dot(E_transfer, node_ih)

    # Store the data
    result_node_ih.append(node_ih)

    # Calculate U(t) and i(t)
    node_V = np.dot(inv_nodal_Y_slice, np.dot(ih_nodal_matrix_slice, node_ih))
    component_i = np.dot(component_Y_matrix_slice, node_V) - node_ih
    component_U = np.dot(component_U_matrix_slice, node_V)

    # Store the data
    result_nodes_V.append(node_V)
    result_components_i.append(component_i)
    result_components_U.append(component_U)


########## Generate the result

result_node_u1 = generate_node_u_result(result_nodes_V, 1)
result_node_u2 = generate_node_u_result(result_nodes_V, 2)
result_node_u3 = generate_node_u_result(result_nodes_V, 3)

result_i_V1 = generate_component_i_result(result_components_i, components_order, "V1")
result_i_S1 = generate_component_i_result(result_components_i, components_order, "S1")
result_i_D1 = generate_component_i_result(result_components_i, components_order, "D1")
result_i_L1 = generate_component_i_result(result_components_i, components_order, "L1")
result_i_C1 = generate_component_i_result(result_components_i, components_order, "C1")
result_i_R1 = generate_component_i_result(result_components_i, components_order, "R1")

result_u_V1 = generate_component_u_result(result_components_U, components_order, "V1")
result_u_S1 = generate_component_u_result(result_components_U, components_order, "S1")
result_u_D1 = generate_component_u_result(result_components_U, components_order, "D1")
result_u_L1 = generate_component_u_result(result_components_U, components_order, "L1")
result_u_C1 = generate_component_u_result(result_components_U, components_order, "C1")
result_u_R1 = generate_component_u_result(result_components_U, components_order, "R1")


########## Plot the result

## The time axis for plotting
time_axis: np.ndarray = np.arange(len(result_nodes_V)) * DeltaT

start_tick: int = int(Start_time / DeltaT)
end_tick: int = int(End_time / DeltaT)

## Plot curse setting
curse_start: float = Start_time
curse_end: float = End_time

## Plot setting
plt.figure()

## Plot the result in the same time
ax1 = plt.subplot(3,3,1)
plt.plot(time_axis, result_node_u1, 'b', label="Voltage of U1")
plt.xlabel("Time")
plt.ylabel("Voltage")
plt.xlim(curse_start, curse_end)
plt.legend()
plt.grid()

ax1 = plt.subplot(3,3,2)
plt.plot(time_axis, result_node_u2, 'b', label="Voltage of U2")
plt.xlabel("Time")
plt.ylabel("Voltage")
plt.xlim(curse_start, curse_end)
plt.legend()
plt.grid()

ax1 = plt.subplot(3,3,3)
plt.plot(time_axis, result_node_u3, 'b', label="Voltage of U3")
plt.xlabel("Time")
plt.ylabel("Voltage")
plt.xlim(curse_start, curse_end)
plt.legend()
plt.grid()

ax1 = plt.subplot(3,3,4)
plt.plot(time_axis, result_i_V1, 'b', label="Current of V1")
plt.xlabel("Time")
plt.ylabel("Current")
plt.xlim(curse_start, curse_end)
plt.legend()
plt.grid()

ax1 = plt.subplot(3,3,5)
plt.plot(time_axis, result_i_S1, 'b', label="Current of SW1")
plt.xlabel("Time")
plt.ylabel("Current")
plt.xlim(curse_start, curse_end)
plt.legend()
plt.grid()

ax1 = plt.subplot(3,3,6)
plt.plot(time_axis, result_i_D1, 'b', label="Current of D1")
plt.xlabel("Time")
plt.ylabel("Current")
plt.xlim(curse_start, curse_end)
plt.legend()
plt.grid()

ax1 = plt.subplot(3,3,7)
plt.plot(time_axis, result_i_L1, 'b', label="Current of L1")
plt.xlabel("Time")
plt.ylabel("Current")
plt.xlim(curse_start, curse_end)
plt.legend()
plt.grid()

ax1 = plt.subplot(3,3,8)
plt.plot(time_axis, result_i_C1, 'b', label="Current of C1")
plt.xlabel("Time")
plt.ylabel("Current")
plt.xlim(curse_start, curse_end)
plt.legend()
plt.grid()

ax1 = plt.subplot(3,3,9)
plt.plot(time_axis, result_i_R1, 'b', label="Current of R1")
plt.xlabel("Time")
plt.ylabel("Current")
plt.xlim(curse_start, curse_end)
plt.legend()
plt.grid()

plt.show()
