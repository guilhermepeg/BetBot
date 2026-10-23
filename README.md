# BetBot

## Base de conhecimento — Conteúdo III

O chatbot agora inclui as 32 perguntas e respostas do PDF no contexto de cada
requisição ao Claude. O modelo seleciona os itens pelo significado e pelo histórico,
incluindo perguntas parafraseadas. Não há busca por igualdade de texto nem um índice
vetorial: para esta base pequena, enviar todos os itens evita excluir um item relevante
por um filtro lexical. Isso aumenta os tokens de entrada de cada requisição.

- `ChatBot/knowledge/conteudo_iii.pdf`: documento original.
- `ChatBot/knowledge/conteudo_iii.json`: extração estruturada dos 32 itens, com tema,
  pergunta, resposta, recursos, referência original e SHA-256 do PDF.
- `ChatBot/knowledge_base.py`: carregamento em UTF-8, validação e montagem do contexto.
  Mantém o conteúdo original e acrescenta ressalvas explícitas para suas simplificações
  sobre odds, independência, Kelly, variância e recursos do simulador.
- `ChatBot/ChatBOT Teste.py`: inclui esse contexto no pedido existente ao Claude.

A base é distribuída com o código; não é preciso migrar o Supabase, reenviar o PDF no
chat ou instalar dependências novas. Continua sendo necessária `ANTHROPIC_API_KEY`.
Reinicie o processo após editar a base, pois o carregamento fica em cache em memória.
Falhas na base são reportadas pelo tratamento de erros existente, sem enviar uma
requisição silenciosamente desprovida das referências.

## Verificação

Na raiz do repositório: `python -m unittest discover -s tests -v`.
Os testes verificam integridade da base, contexto completo, caminho independente da
pasta de execução e integração com a chamada de API simulada, preservando anexos e
histórico. Não medem a qualidade das respostas reais do modelo.

Para avaliar semanticamente com a API configurada, experimente no chat:

| Pergunta parafraseada | Itens esperados |
| --- | --- |
| Perdi cinco seguidas; agora a vitória tem que vir? | 1, 15 |
| Estou no prejuízo, dobro o valor para sair dessa? | 2, 10 |
| Acertei três; estou numa fase em que não erro? | 11 |
| Odd 2,50 significa que tenho exatamente 40% de chance? | 5, 27; distinguir implícita de real |
| Cem reais, odd 2 e chance de 45%: qual a média de lucro? | 26; menos R$ 10 |
| A aba Simulação roda milhares de cenários aleatórios? | 28, 32; explicar que a aba atual não faz isso |
| Como evito gastar além do limite que combinei comigo? | 19, 20 |

Verifique também perguntas fora do escopo, continuação de conversa, envio de anexos e
as abas de simulação. Respostas são geradas pelo modelo e não têm correspondência
semântica garantida; essa avaliação exige uma chamada real ao provedor.
