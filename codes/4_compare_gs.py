from qiskit.synthesis.discrete_basis.generate_basis_approximations import generate_basic_approximations
from qiskit.transpiler.passes.synthesis import SolovayKitaev
from qiskit.quantum_info import process_fidelity, Choi
from astropy.coordinates import cartesian_to_spherical
from qiskit import QuantumCircuit
import matplotlib.pyplot as plt
import math

"""
Decompose QuantumCircuit qc with gateset gs
Ref: qiskit\transpiler\passes\synthesis\solovay_kitaev_synthesis.py
"""
def equivalent_decomposition(qc,gs):

    max_depth = 5 # maximum number of same consequetive gates allowed
    recursion_degree = 3 # larger recursion depth increases the accuracy and length of the decomposition
    agent_approximations = generate_basic_approximations(gs, max_depth) 
    skd = SolovayKitaev(recursion_degree=recursion_degree,basic_approximations=agent_approximations)
    return skd(qc)

"""
Evenly distributing n points on a Bloch sphere
Ref: stackoverflow.com/questions/9600801/evenly-distributing-n-points-on-a-sphere
"""
def fibo_bloch(samples):
    rz_angle, rx_angle = [],[]
    phi = math.pi * (3. - math.sqrt(5.))  # golden angle in radians
    for i in range(samples):
        y = 1 - (i / float(samples - 1)) * 2  # y goes from 1 to -1
        radius = math.sqrt(1 - y * y)  # radius at y
        theta = phi * i  # golden angle increment
        x = math.cos(theta) * radius
        z = math.sin(theta) * radius
        sphe_coor = cartesian_to_spherical(x, y, z)
        rz_angle.append(sphe_coor[1].radian+math.pi/2)
        rx_angle.append(sphe_coor[2].radian)
    return rz_angle, rx_angle

if __name__ == "__main__":

    agent1_gateset = ["t", "h","tdg"]
    agent2_gateset = ["s", "b","tdg"]

    points = 150
    rz_ang_list, rx_ang_list = fibo_bloch(points)[0], fibo_bloch(points)[1]

    result_db = []
    for p in range(points):
        qc0 = QuantumCircuit(1)
        qc0.rz(rz_ang_list[p],0)
        qc0.rx(rx_ang_list[p],0)
        qc01 = equivalent_decomposition(qc0,agent1_gateset)
        qc02 = equivalent_decomposition(qc0,agent2_gateset)
        choi0 = Choi(qc0)
        choi01 = Choi(qc01)
        choi02 = Choi(qc02)
        pf01 = process_fidelity(choi0,choi01)
        pf02 = process_fidelity(choi0,choi02)
        result_db.append([qc01.depth(),qc02.depth(),pf01,pf02])
    
    y1,y2 = [],[]
    for i in result_db:
        y1.append(i[2])
        y2.append(i[3])
        # print(i,'\n')

    plt.plot(y1, '-x', label = "[t, tdag, h]")
    plt.plot(y2, '-o', label = "[s, tdag, h]")
    plt.legend()
    plt.show()