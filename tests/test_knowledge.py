import ast
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'ChatBot'))
import knowledge_base as kb


class KnowledgeTests(unittest.TestCase):
    def tearDown(self):
        kb.knowledge_context.cache_clear()

    def test_complete_source_and_fingerprint(self):
        data = json.loads(kb.KNOWLEDGE_PATH.read_text(encoding='utf-8'))
        self.assertEqual(data['sha256'], hashlib.sha256(
            kb.KNOWLEDGE_PATH.with_suffix('.pdf').read_bytes()).hexdigest())
        self.assertEqual([e['id'] for e in data['entries']], list(range(1, 33)))
        context = kb.build_system_prompt('EXISTING RULES')
        self.assertTrue(context.startswith('EXISTING RULES'))
        embedded = json.loads(context.split('<conteudo_iii>\n', 1)[1].split('\n</conteudo_iii>')[0])
        self.assertEqual(embedded, data)

    def test_path_independent_of_working_directory(self):
        import os
        previous = os.getcwd()
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            try:
                os.chdir(directory)
                self.assertIn('conteudo_iii', kb.knowledge_context())
            finally:
                os.chdir(previous)

    def test_incomplete_corpus_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            path = Path(directory) / 'bad.json'
            path.write_text('{"entries": []}', encoding='utf-8')
            with patch.object(kb, 'KNOWLEDGE_PATH', path):
                with self.assertRaises(ValueError):
                    kb.knowledge_context()

    def test_real_request_builder_preserves_history_and_attachments(self):
        # Execute the actual request functions without starting Streamlit's UI.
        tree = ast.parse((ROOT / 'ChatBot/ChatBOT Teste.py').read_text(encoding='utf-8'))
        functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)
                     and n.name in ('build_api_messages', 'get_bot_response')]
        client = Mock()
        client.messages.create.return_value.content = [Mock(text='resposta')]
        namespace = dict(_get_client=lambda: client, SYSTEM_PROMPT='existing rules',
                         build_system_prompt=kb.build_system_prompt,
                         anthropic=type('Errors', (), dict(AuthenticationError=type('Auth', (Exception,), {}),
                                                         RateLimitError=type('Rate', (Exception,), {}))))
        exec(compile(ast.Module(body=functions, type_ignores=[]), '<request>', 'exec'), namespace)
        history = [dict(role='assistant', content='olá'),
                   dict(role='user', content='Estou no prejuízo, dobro o valor para sair dessa?',
                        attachments=[dict(kind='pdf', data='cGRm', name='test.pdf')]),
                   dict(role='assistant', content='Não persiga perdas.'),
                   dict(role='user', content='E se eu já tiver perdido trezentos reais?')]
        self.assertEqual(namespace['get_bot_response'](history), 'resposta')
        request = client.messages.create.call_args.kwargs
        self.assertEqual(len(request['messages']), 3)
        self.assertEqual(request['messages'][0]['content'][0]['type'], 'document')
        self.assertIn('perseguição de perdas', request['system'])
        self.assertIn('custos irrecuperáveis', request['system'])
        self.assertEqual(len(history), 4)
        with patch.object(kb, 'KNOWLEDGE_PATH', Path('missing.json')):
            kb.knowledge_context.cache_clear()
            client.messages.create.reset_mock()
            self.assertIn('erro ao consultar', namespace['get_bot_response'](history))
            client.messages.create.assert_not_called()
        namespace['_get_client'] = lambda: None
        self.assertIn('Chave de API não configurada', namespace['get_bot_response'](history))


if __name__ == '__main__':
    unittest.main()
