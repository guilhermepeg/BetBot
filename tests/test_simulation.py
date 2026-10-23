from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'ChatBot'))
import sim_utils as su


class SimulationTests(unittest.TestCase):
    def test_defaults_are_zero(self):
        self.assertEqual(su.DEFAULT_SIM_ODD, 0.0)
        self.assertEqual(su.DEFAULT_SIM_STAKE, 0.0)

    def test_typed_values_are_used(self):
        bet = su.build_selection('  Palmeiras vence ', 3.5, 25.0)
        self.assertEqual(bet, {'name': 'Palmeiras vence', 'odd': 3.5, 'stake': 25.0})

    def test_zero_defaults_are_invalid(self):
        with self.assertRaises(ValueError):
            su.build_selection('Flamengo vence', su.DEFAULT_SIM_ODD, su.DEFAULT_SIM_STAKE)
        self.assertEqual(len(su.validate_selection('x', 0, 0)), 2)

    def test_invalid_inputs(self):
        self.assertTrue(su.validate_selection('', 2.0, 10.0))
        self.assertTrue(su.validate_selection('x', 1.0, 10.0))
        self.assertTrue(su.validate_selection('x', 2.0, 0))
        self.assertTrue(su.validate_selection(None, None, None))
        self.assertEqual(su.validate_selection('x', 2.0, 10.0), [])


try:
    from streamlit.testing.v1 import AppTest
except ImportError:
    AppTest = None


@unittest.skipIf(AppTest is None, 'streamlit não instalado')
class SimulationAppTests(unittest.TestCase):
    def setUp(self):
        self.at = AppTest.from_file(str(ROOT / 'ChatBot' / 'ChatBOT Teste.py'), default_timeout=30).run()

    def _add(self):
        [b for b in self.at.button if b.label == 'Adicionar'][0].click().run()

    def test_zero_defaults_and_validation_error(self):
        self.assertEqual(self.at.number_input(key='sim_odd').value, 0.0)
        self.assertEqual(self.at.number_input(key='sim_stake').value, 0.0)
        self._add()
        self.assertEqual(self.at.session_state.sim_bets, [])
        self.assertTrue(self.at.error)

    def test_typed_values_are_added(self):
        self.at.text_input(key='sim_name').input('Meu time')
        self.at.number_input(key='sim_odd').set_value(3.5)
        self.at.number_input(key='sim_stake').set_value(20.0)
        self._add()
        self.assertEqual(self.at.session_state.sim_bets,
                         [{'name': 'Meu time', 'odd': 3.5, 'stake': 20.0}])


if __name__ == '__main__':
    unittest.main()
