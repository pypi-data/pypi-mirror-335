# -*- coding: utf-8 -*-
"""
Created on Wed Mar 19 09:04:02 2025

@author: Shagedoorn1
"""
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from transfer_function import TransferFunction
def bode_plot(transfer_function, omega_range=np.logspace(-1, 6, 1000)):
    """
    Generate and display the Bode plot of the given system.
    
    A Bode plot consists of 2 subplots:
        1 magnitude (in decibels) vs frequency (in radians per second)
        2 phase (in degrees) vs frequency (in radians per second)
    
    Parameters:
        transfer_function (TransferFunction):
            A TransferFunction object, see transfer_function.py for details
        omega_range (numpy array):
            A range of frequencies for which the Bode plot is computed,
            default from 10^-1 to 10^6, with 1000 points.
    """
    magnitude, phase = transfer_function.calc_magnitude_and_phase(omega_range)
    
    plt.figure(figsize = (10, 6))
    plt.subplot(2, 1, 1)
    plt.semilogx(omega_range, magnitude)
    plt.title("Bode plot")
    plt.ylabel("Magnitude (dB)")
    plt.axhline(linewidth=1, color='Black')
    plt.grid(True)
    
    plt.subplot(2, 1, 2)
    plt.semilogx(omega_range, phase)
    plt.ylabel("phase (deg)")
    plt.xlabel("Frequency (rad/s)")
    plt.axhline(linewidth=1, color='Black')
    plt.axhline(y=-90, linewidth=1, color="Black")
    plt.grid(True)
    
    plt.show()

def pz_map(transfer_function):
    """
    Generate and display the Pole-Zero map of the given system.
    
    The map shows the poles and zeros of the transfer function in the complex
    plane
        - Poles are marked with an "X"
        - Zeros are marked with an "O"
    
    Parameters:
        transfer_function (TransferFunction):
            The transfer_function object that represents the system,
            see transfer_function.py for details.
    
    """
    poles = transfer_function.poles
    zeros = transfer_function.zeros
    i = 0
    j = 0
    reals = []
    comps = []
    plt.title("Pole-Zero map")
    plt.scatter(
        [sp.re(p) for p in poles],
        [sp.im(p) for p in poles],
        marker = 'x',
        s = 500,
        color = 'black',
        label = 'poles')
    while i < len(zeros):
        reals.append(sp.re(zeros[i]))
        comps.append(sp.im(zeros[i]))
        i += 1
    plt.scatter(
        [sp.re(z) for z in zeros],
        [sp.im(z) for z in zeros],
        marker = "o",
        s = 500,
        edgecolors = "black",
        facecolors = 'none',
        label = 'zeros')
    while j < len(poles):
        reals.append(sp.re(poles[j]))
        comps.append(sp.im(poles[j]))
        j += 1
    plt.xlim([float(min(reals)) - 1, float(max(reals)) + 1])
    plt.ylim([float(min(comps))-1, float(max(comps)) + 1])
    plt.axhline(linewidth=1, color='Black')
    plt.axvline(linewidth=1, color='Black')
    plt.xlabel(r"$\lambda$ re(s)")
    plt.ylabel(r"$j \omega$ im(s)")
    plt.legend(prop={'size': 15})
    plt.grid()
    plt.show()
    
if __name__ == "__main__":
    string1 = "y''+y'+y"
    string2 = "x'+x"
    o_range = np.logspace(-1,3,1000)
    Trans = TransferFunction(string1, string2)
    bode_plot(Trans, omega_range=np.logspace(-1,3,1000))
    pz_map(Trans)