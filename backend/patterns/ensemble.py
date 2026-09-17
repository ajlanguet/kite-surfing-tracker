"""
YOUR TURN: multi-model consensus.

Once you ingest two forecast sources for the same valid_at (for example
Open-Meteo GFS and Open-Meteo ECMWF), write:

    def consensus(points) -> dict

that returns a single wind_speed_kt / wind_direction_deg.

A good first version is not machine learning:

1. Convert each (speed, direction) into u/v vectors.
2. Average the vectors.
3. Convert back to speed/direction.
4. Add a `agreement` score: how tight the models cluster.

Only after that is working should you weight models by historical bias
at that spot and lead time.
"""


def consensus(points):
    raise NotImplementedError("Average forecast vectors once you have two sources.")
