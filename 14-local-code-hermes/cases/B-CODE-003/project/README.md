# Fixture B-CODE-003

Repara el error de borde de `apply_discount` sin cambiar su contrato público.

1. Reproduce los tests existentes.
2. Corrige únicamente `src/pricing.py`.
3. Conserva todos los tests y añade
   `test_discount_above_100_is_rejected` en `tests/test_pricing.py`.
4. Ejecuta `python -m unittest discover -s tests -v`.

No crees archivos adicionales ni uses red.
