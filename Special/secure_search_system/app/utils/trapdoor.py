import numpy as np

def build_trapdoor(vector, S, M1, M2):
    q1, q2 = np.zeros_like(vector), np.zeros_like(vector)
    for i in range(len(vector)):
        if S[i] == 0:
            q1[i] = q2[i] = vector[i]
        else:
            r = np.random.rand()
            q1[i] = r
            q2[i] = vector[i] - r

    T1 = np.linalg.inv(M1) @ q1
    T2 = np.linalg.inv(M2) @ q2
    return (T1, T2)


def match_node(trapdoor, enc_vector):
    T1, T2 = trapdoor
    C1, C2 = enc_vector
    return np.dot(T1, C1) + np.dot(T2, C2)
