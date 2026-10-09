create table if not exists public.user_data (
    user_id text primary key,
    chats jsonb not null default '[]'::jsonb,
    bet_history jsonb not null default '[]'::jsonb
);

alter table public.user_data enable row level security;
revoke all on table public.user_data from anon, authenticated;
grant all on table public.user_data to service_role;
