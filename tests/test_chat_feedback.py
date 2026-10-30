"""Regression tests without network calls or a running Streamlit server."""
import ast
from pathlib import Path
import unittest
from unittest.mock import Mock

APP = Path(__file__).resolve().parents[1] / "ChatBot" / "ChatBOT Teste.py"


class ChatFeedbackTests(unittest.TestCase):
    def setUp(self):
        self.tree = ast.parse(APP.read_text(encoding="utf-8"))
        functions = [node for node in self.tree.body
                     if isinstance(node, ast.FunctionDef)
                     and node.name == "get_bot_response_with_status"]
        self.st = Mock()
        self.status = self.st.empty.return_value
        self.respond = Mock(return_value="Resposta pronta")
        namespace = {"st": self.st, "get_bot_response": self.respond}
        exec(compile(ast.Module(body=functions, type_ignores=[]), str(APP), "exec"), namespace)
        self.run_response = namespace["get_bot_response_with_status"]

    def test_indicator_visible_during_request_and_removed_after_success(self):
        history = [{"role": "user", "content": "Olá"}]

        def respond(received):
            self.assertIs(received, history)
            self.status.info.assert_called_once_with("Pensando...")
            self.status.empty.assert_not_called()
            return "Resposta pronta"

        self.respond.side_effect = respond
        self.assertEqual(self.run_response(history), "Resposta pronta")
        self.status.empty.assert_called_once_with()
        self.assertEqual(history, [{"role": "user", "content": "Olá"}])

    def test_unexpected_error_clears_indicator_and_allows_next_request(self):
        self.respond.side_effect = [RuntimeError("private details"), "Recuperado"]
        reply = self.run_response([])
        self.assertIn("Tente enviar", reply)
        self.assertNotIn("private details", reply)
        self.status.empty.assert_called_once_with()
        self.assertEqual(self.run_response([]), "Recuperado")
        self.assertEqual(self.status.empty.call_count, 2)

    def test_empty_response_reports_error_and_clears_indicator(self):
        for response in ("", "  ", None):
            with self.subTest(response=response):
                self.respond.return_value = response
                self.status.reset_mock()
                self.assertIn("Tente enviar", self.run_response([]))
                self.status.empty.assert_called_once_with()

    def test_existing_api_error_message_preserved(self):
        self.respond.return_value = "Limite de requisições atingido. Aguarde um instante e tente novamente."
        self.assertEqual(self.run_response([]), self.respond.return_value)
        self.status.empty.assert_called_once_with()

    def test_remaining_tabs_work_without_multiple_bet_state(self):
        tabs = next(node for node in self.tree.body
                    if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, ast.Attribute)
                    and node.value.func.attr == "tabs")
        self.st.tabs.return_value = ["chat", "simulation", "history"]
        namespace = {"st": self.st}
        exec(compile(ast.Module(body=[tabs], type_ignores=[]), str(APP), "exec"), namespace)
        self.st.tabs.assert_called_once_with(["Chat", "Simulação", "Histórico de Bets"])
        self.assertEqual(namespace["tab_history"], "history")
        names = [node.id for node in ast.walk(self.tree) if isinstance(node, ast.Name)]
        attributes = [node.attr for node in ast.walk(self.tree) if isinstance(node, ast.Attribute)]
        self.assertFalse(any(name.startswith("multi_") or name == "tab_multi" for name in names))
        self.assertNotIn("multi_bets", attributes)


if __name__ == "__main__":
    unittest.main()
