"""Parameter sets and schemas for the rectangle compression simulation"""


def schema(width=1.0, height=1.0, global_seed=1.0, displacement=-0.01):
    """Return nominal simulation variables dictionary

    :param float width: The rectangle width
    :param float height: The rectangle height
    :param float global_seed: The global mesh seed size
    :param float displacement: The rectangle top surface displacement

    :returns: nominal simulation variables
    :rtype: dict
    """
    simulation_variables = {
        'width': 1.0,
        'height': 1.0,
        'global_seed': 1.0,
        'displacement': -0.01
    }
    return simulation_variables
