import numpy as np


def moving_average(x: np.ndarray, w: int) -> np.ndarray:
    return np.convolve(x, np.ones(w), "valid") / w


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def softmax(x: np.ndarray) -> np.ndarray:
    return np.exp(x) / np.nansum(np.exp(x))
