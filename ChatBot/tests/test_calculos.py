"""Testes unitários para funções de cálculo puro do BetBot.

As funções são definidas aqui com a mesma lógica do módulo principal para
que os testes rodem sem depender do Streamlit ou do Anthropic SDK.
"""
import unittest

# ---------------------------------------------------------------------------
# Constantes e funções extraídas de ChatBOT Teste.py (cálculo puro)
# ---------------------------------------------------------------------------

CDI_ANUAL_PADRAO = 14.15
MAX_EXTRACTED_TEXT_CHARS = 8000

ACCA_BONUS_TABLE = [
    (8, 0.25),
    (7, 0.20),
    (6, 0.15),
    (5, 0.10),
    (4, 0.05),
]

BET_BUILDER_BONUS_PER_EXTRA = 0.03
BET_BUILDER_BONUS_CAP = 0.15


def get_acca_bonus(n_selections: int) -> float:
    for min_legs, bonus in ACCA_BONUS_TABLE:
        if n_selections >= min_legs:
            return bonus
    return 0.0


def get_bet_builder_bonus(bets: list) -> float:
    events: dict = {}
    for b in bets:
        events.setdefault(b["event"], []).append(b)
    total_bonus = 0.0
    for legs in events.values():
        if len(legs) >= 2:
            total_bonus += min(
                (len(legs) - 1) * BET_BUILDER_BONUS_PER_EXTRA,
                BET_BUILDER_BONUS_CAP,
            )
    return total_bonus


def _limit_extracted_text(text: str) -> str:
    if len(text) <= MAX_EXTRACTED_TEXT_CHARS:
        return text
    return text[:MAX_EXTRACTED_TEXT_CHARS] + "\n[... texto truncado por exceder o limite de leitura ...]"


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------

class TestGetAccaBonus(unittest.TestCase):
    def test_retorna_zero_abaixo_do_minimo(self):
        self.assertEqual(get_acca_bonus(0), 0.0)
        self.assertEqual(get_acca_bonus(3), 0.0)

    def test_bonus_4_selecoes(self):
        self.assertAlmostEqual(get_acca_bonus(4), 0.05)

    def test_bonus_5_selecoes(self):
        self.assertAlmostEqual(get_acca_bonus(5), 0.10)

    def test_bonus_6_selecoes(self):
        self.assertAlmostEqual(get_acca_bonus(6), 0.15)

    def test_bonus_7_selecoes(self):
        self.assertAlmostEqual(get_acca_bonus(7), 0.20)

    def test_bonus_8_ou_mais_selecoes(self):
        self.assertAlmostEqual(get_acca_bonus(8), 0.25)
        self.assertAlmostEqual(get_acca_bonus(20), 0.25)

    def test_tabela_em_ordem_decrescente(self):
        bonuses = [b for _, b in ACCA_BONUS_TABLE]
        self.assertEqual(bonuses, sorted(bonuses, reverse=True))


class TestGetBetBuilderBonus(unittest.TestCase):
    def _bet(self, event: str) -> dict:
        return {"event": event, "name": "x", "odd": 2.0, "stake": 10.0}

    def test_sem_apostas(self):
        self.assertAlmostEqual(get_bet_builder_bonus([]), 0.0)

    def test_um_evento_uma_aposta(self):
        self.assertAlmostEqual(get_bet_builder_bonus([self._bet("A")]), 0.0)

    def test_um_evento_duas_apostas(self):
        bets = [self._bet("A"), self._bet("A")]
        self.assertAlmostEqual(get_bet_builder_bonus(bets), 0.03)

    def test_um_evento_tres_apostas(self):
        bets = [self._bet("E")] * 3
        self.assertAlmostEqual(get_bet_builder_bonus(bets), 0.06)

    def test_cap_por_evento_exato(self):
        # 6 apostas → 5 extras → 5 * 0.03 = 0.15 (igual ao cap)
        bets = [self._bet("E")] * 6
        self.assertAlmostEqual(get_bet_builder_bonus(bets), 0.15)

    def test_cap_com_overflow(self):
        # 7 apostas → 6 extras → 6 * 0.03 = 0.18 > 0.15 → cap em 0.15
        bets = [self._bet("E")] * 7
        self.assertAlmostEqual(get_bet_builder_bonus(bets), 0.15)

    def test_dois_eventos_independentes(self):
        bets = [self._bet("A"), self._bet("A"), self._bet("B"), self._bet("B")]
        self.assertAlmostEqual(get_bet_builder_bonus(bets), 0.06)

    def test_eventos_misturados(self):
        # A tem 3 apostas (bonus 0.06), B tem 1 (bonus 0)
        bets = [self._bet("A"), self._bet("A"), self._bet("A"), self._bet("B")]
        self.assertAlmostEqual(get_bet_builder_bonus(bets), 0.06)


class TestLimitExtractedText(unittest.TestCase):
    def test_texto_curto_nao_e_truncado(self):
        texto = "abc"
        self.assertEqual(_limit_extracted_text(texto), texto)

    def test_texto_no_limite_nao_e_truncado(self):
        texto = "x" * MAX_EXTRACTED_TEXT_CHARS
        self.assertEqual(_limit_extracted_text(texto), texto)

    def test_texto_longo_e_truncado(self):
        texto = "x" * (MAX_EXTRACTED_TEXT_CHARS + 100)
        resultado = _limit_extracted_text(texto)
        self.assertLessEqual(len(resultado), MAX_EXTRACTED_TEXT_CHARS + 100)
        self.assertNotEqual(resultado, texto)

    def test_truncamento_inclui_aviso(self):
        texto = "y" * (MAX_EXTRACTED_TEXT_CHARS + 1)
        resultado = _limit_extracted_text(texto)
        self.assertIn("truncado", resultado)


class TestConstantes(unittest.TestCase):
    def test_cdi_anual_padrao_e_positivo(self):
        self.assertGreater(CDI_ANUAL_PADRAO, 0)

    def test_max_extracted_text_chars_e_positivo(self):
        self.assertGreater(MAX_EXTRACTED_TEXT_CHARS, 0)

    def test_bet_builder_bonus_per_extra_e_positivo(self):
        self.assertGreater(BET_BUILDER_BONUS_PER_EXTRA, 0)

    def test_bet_builder_bonus_cap_maior_que_per_extra(self):
        self.assertGreater(BET_BUILDER_BONUS_CAP, BET_BUILDER_BONUS_PER_EXTRA)


if __name__ == "__main__":
    unittest.main()
