
import time
import numpy as np
import pickle

from smartsim import Client


def simulate(seed):

    # mimic computationally expensive kernel
    time.sleep(2)
    # conduct simulation of a simple 2D function
    # f(x) = x**2
    np.random.seed(seed)
    n = 20
    x = np.random.uniform(-15.0, 15.0, size = n)
    y = x**2 + 2*np.random.randn(n, )
    X = np.reshape(x ,[n, 1])
    y = np.reshape(y ,[n ,])

    return X, y

def run_simulations(steps, client):

    i = 0
    while i < int(steps):
        X, y = simulate(i)
        print("sending data for key", str(i), flush=True)
        client.send_data(str(i) + "_X", X)
        client.send_data(str(i) + "_y", y)
        i+=1


if __name__ == "__main__":
    client = Client()
    client.setup_connections()
    run_simulations(20, client)
