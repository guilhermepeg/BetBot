# BetBot

Assistente de IA para apostas esportivas, construído com Streamlit e Claude (Anthropic).

## Variáveis de ambiente

O app funciona sem nenhuma configuração (dados apenas em memória). Para habilitar funcionalidades extras, configure as variáveis abaixo via `st.secrets` (arquivo `.streamlit/secrets.toml`) ou variáveis de ambiente do sistema.

### Anthropic (obrigatório para o chatbot)

| Variável | Descrição |
|---|---|
| `ANTHROPIC_API_KEY` | Chave de API do Anthropic para acesso ao modelo Claude |

### Supabase (opcional — persistência de histórico)

Quando configuradas, o app salva e carrega os chats e o histórico de bets de cada usuário a partir de um banco Supabase. Sem essas variáveis, tudo funciona normalmente, mas os dados são perdidos ao recarregar a página.

| Variável | Descrição |
|---|---|
| `SUPABASE_URL` | URL do projeto Supabase (ex.: `https://xyzabc.supabase.co`) |
| `SUPABASE_SERVICE_KEY` | Chave `service_role` do Supabase (**nunca a chave `anon`**) |

#### Configuração via `st.secrets`

Crie o arquivo `.streamlit/secrets.toml` (não suba para o git):

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
SUPABASE_URL = "https://xyzabc.supabase.co"
SUPABASE_SERVICE_KEY = "eyJ..."
```

#### Schema do banco

Execute o arquivo [`ChatBot/supabase_schema.sql`](ChatBot/supabase_schema.sql) no SQL Editor do Supabase para criar a tabela necessária.
