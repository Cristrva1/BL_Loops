"""Funcion pequena con un error de borde intencional."""


def apply_discount(subtotal_cents: int, discount_percent: int) -> int:
    """Aplica un porcentaje entero entre 0 y 100, ambos inclusive."""

    if subtotal_cents < 0:
        raise ValueError("subtotal_cents must be non-negative")
    if discount_percent < 0 or discount_percent >= 100:
        raise ValueError("discount_percent must be between 0 and 100")
    discount_cents = subtotal_cents * discount_percent // 100
    return subtotal_cents - discount_cents
