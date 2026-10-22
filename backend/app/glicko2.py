"""Glicko-2 (Glickman, 2012) para actualizar un rating tras una sola partida o puzzle."""

import math

SCALE = 173.7178
TAU = 0.5
EPSILON = 0.000001

DEFAULT_RATING = 1500.0
DEFAULT_RD = 350.0
DEFAULT_VOL = 0.06
MIN_RD = 45.0  # como Lichess: evita que el rating se congele


def _g(phi: float) -> float:
    return 1 / math.sqrt(1 + 3 * phi**2 / math.pi**2)


def _e(mu: float, mu_j: float, phi_j: float) -> float:
    return 1 / (1 + math.exp(-_g(phi_j) * (mu - mu_j)))


def update(
    rating: float, rd: float, vol: float, opp_rating: float, opp_rd: float, score: float
) -> tuple[float, float, float]:
    """score: 1 victoria/acierto, 0.5 tablas, 0 derrota/fallo."""
    mu = (rating - 1500) / SCALE
    phi = rd / SCALE
    mu_j = (opp_rating - 1500) / SCALE
    phi_j = opp_rd / SCALE

    g = _g(phi_j)
    e = _e(mu, mu_j, phi_j)
    v = 1 / (g**2 * e * (1 - e))
    delta = v * g * (score - e)

    # Nueva volatilidad (algoritmo de Illinois)
    a = math.log(vol**2)

    def f(x: float) -> float:
        ex = math.exp(x)
        return ex * (delta**2 - phi**2 - v - ex) / (2 * (phi**2 + v + ex) ** 2) - (x - a) / TAU**2

    big_a = a
    if delta**2 > phi**2 + v:
        big_b = math.log(delta**2 - phi**2 - v)
    else:
        k = 1
        while f(a - k * TAU) < 0:
            k += 1
        big_b = a - k * TAU
    f_a, f_b = f(big_a), f(big_b)
    while abs(big_b - big_a) > EPSILON:
        big_c = big_a + (big_a - big_b) * f_a / (f_b - f_a)
        f_c = f(big_c)
        if f_c * f_b <= 0:
            big_a, f_a = big_b, f_b
        else:
            f_a /= 2
        big_b, f_b = big_c, f_c
    new_vol = math.exp(big_a / 2)

    phi_star = math.sqrt(phi**2 + new_vol**2)
    new_phi = 1 / math.sqrt(1 / phi_star**2 + 1 / v)
    new_mu = mu + new_phi**2 * g * (score - e)

    new_rd = max(MIN_RD, min(DEFAULT_RD, new_phi * SCALE))
    return new_mu * SCALE + 1500, new_rd, new_vol
