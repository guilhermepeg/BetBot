"""Validação e criação das seleções do simulador de apostas."""

DEFAULT_SIM_ODD = 0.0
DEFAULT_SIM_STAKE = 0.0
MIN_VALID_ODD = 1.01


def validate_selection(name, odd, stake) -> list:
    """Retorna a lista de mensagens de erro (vazia se a seleção for válida)."""
    errors = []
    if not str(name or "").strip():
        errors.append("Informe o nome da seleção.")
    if odd is None or odd < MIN_VALID_ODD:
        errors.append(f"Informe uma odd maior ou igual a {MIN_VALID_ODD:.2f} (0 não é válido).")
    if stake is None or stake <= 0:
        errors.append("Informe um valor apostado maior que 0.")
    return errors


def build_selection(name, odd, stake) -> dict:
    """Cria a seleção com exatamente os valores informados; erro se inválidos."""
    errors = validate_selection(name, odd, stake)
    if errors:
        raise ValueError(" ".join(errors))
    return {"name": str(name).strip(), "odd": float(odd), "stake": float(stake)}
