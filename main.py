from jobs.first_opt import OptimizeLD


"""
Overall to-do list
TODO:
- Structure Optimization problem for L/D at angle of attack
    - Create necessary XFOIL interactions for this to take place

"""


if __name__ == "__main__":

    """
    TODO: Set this up to where different runs can be run from this file without
    having to change anything in this file specifically
    """

    Optimization = OptimizeLD()

    Optimization.run_process()