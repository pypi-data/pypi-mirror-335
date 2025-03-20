from concurrent.futures import ProcessPoolExecutor
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from calc_dc_components_modify import calc_dc_components_modify
from calc_harmonic_coefficients_modify import calc_harmonic_coefficients_modify


def compute_harmonic_coefficients(ai, harmonic_index):
    """单独计算一个谐波的系数"""
    return calc_harmonic_coefficients_modify(ai, harmonic_index + 1, 0)


def fourier_approx_norm_modify(ai, n, m, normalized, option):
    EPS = 1e-10
    a = np.zeros(n)
    b = np.zeros(n)
    c = np.zeros(n)
    d = np.zeros(n)

    # 并行计算谐波系数
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(compute_harmonic_coefficients, [ai] * n, range(n)))
    
    # 收集计算结果
    for i, harmonic_coeff in enumerate(results):
        a[i] = harmonic_coeff[0]
        b[i] = harmonic_coeff[1]
        c[i] = harmonic_coeff[2]
        d[i] = harmonic_coeff[3]

    # 原有代码继续执行
    A0, C0, Tk, T = calc_dc_components_modify(ai, 0)

    # Normalization procedure
    if normalized:
        ro = option[0]
        sc = option[1]
        re = option[2]
        y_sy = option[3]
        x_sy = option[4]
        sta = option[5]
        trans = option[6]

        # Remove DC components
        if trans:
            A0 = 0
            C0 = 0

        if re:
            CrossProduct = a[0] * d[0] - c[0] * b[0]
            if CrossProduct < 0:
                b = -b
                d = -d

        tan_theta2 = 2 * (a[0] * b[0] + c[0] * d[0]) / (a[0]**2 + c[0]**2 - b[0]**2 - d[0]**2)
        theta1 = 0.5 * np.arctan(tan_theta2)
        if theta1 < 0:
            theta1 += np.pi / 2
        sin_2theta = np.sin(2 * theta1)
        cos_2theta = np.cos(2 * theta1)
        cos_theta_square = (1 + cos_2theta) / 2
        sin_theta_square = (1 - cos_2theta) / 2

        axis_theta1 = (a[0]**2 + c[0]**2) * cos_theta_square + (a[0] * b[0] + c[0] * d[0]) * sin_2theta + (b[0]**2 + d[0]**2) * sin_theta_square
        axis_theta2 = (a[0]**2 + c[0]**2) * sin_theta_square - (a[0] * b[0] + c[0] * d[0]) * sin_2theta + (b[0]**2 + d[0]**2) * cos_theta_square

        if axis_theta1 < axis_theta2:
            theta1 += np.pi / 2

        costh1 = np.cos(theta1)
        sinth1 = np.sin(theta1)
        a_star_1 = costh1 * a[0] + sinth1 * b[0]
        c_star_1 = costh1 * c[0] + sinth1 * d[0]
        psi1 = np.arctan(c_star_1 / a_star_1)
        
        if c_star_1>0 and a_star_1<0:
            psi1 = np.pi -psi1
        
        if c_star_1<0 and a_star_1<0:
            psi1 = np.pi + psi1

        if c_star_1<0 and a_star_1>0:
            psi1 = 2*np.pi - psi1



        E = np.sqrt(a_star_1**2 + c_star_1**2)

        if sc:
            a /= E
            b /= E
            c /= E
            d /= E

        cospsi1 = np.cos(psi1)
        sinpsi1 = np.sin(psi1)
        normalized_all = np.zeros((n, 4))

        if ro:
            for i in range(n):
                normalized = np.dot([[cospsi1, sinpsi1], [-sinpsi1, cospsi1]], [[a[i], b[i]], [c[i], d[i]]])
                normalized_all[i] = normalized.reshape(1, 4)
            a = normalized_all[:, 0]
            b = normalized_all[:, 1]
            c = normalized_all[:, 2]
            d = normalized_all[:, 3]

        normalized_all_1 = np.zeros((n, 4))

        if sta:
            for i in range(n):
                normalized_1 = np.dot([[a[i], b[i]], [c[i], d[i]]], [[np.cos(theta1 * (i + 1)), -np.sin(theta1 * (i + 1))], [np.sin(theta1 * (i + 1)), np.cos(theta1 * (i + 1))]])
                normalized_all_1[i, :] = normalized_1.reshape(1, 4)
            a = normalized_all_1[:, 0]
            b = normalized_all_1[:, 1]
            c = normalized_all_1[:, 2]
            d = normalized_all_1[:, 3]


        if y_sy:
            if n>1:
                if a[1] < -EPS:
                    for i in range(1, n):
                        signval = (-1) ** (((i + 1) % 2) + 1)
                        a[i] = signval * a[i]
                        d[i] = signval * d[i]
                        signval = (-1) ** ((i + 1) % 2)
                        b[i] = signval * b[i]
                        c[i] = signval * c[i]

        if x_sy:
            if n>1:
                if c[1] < -EPS:
                    b[1:] *= -1
                    c[1:] *= -1

    output = np.zeros((m, 2))

    for t in range(m):
        x_ = 0.0
        y_ = 0.0
        for i in range(n):
            x_ += (a[i] * np.cos(2 * (i + 1) * np.pi * (t) * Tk / (m - 1) / T) + b[i] * np.sin(2 * (i + 1) * np.pi * (t) * Tk / (m - 1) / T))
            y_ += (c[i] * np.cos(2 * (i + 1) * np.pi * (t) * Tk / (m - 1) / T) + d[i] * np.sin(2 * (i + 1) * np.pi * (t) * Tk / (m - 1) / T))
        output[t, 0] = A0 + x_
        output[t, 1] = C0 + y_

    return output, a, b, c, d
