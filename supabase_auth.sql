create extension if not exists pgcrypto;

create table if not exists public."user" (
    id integer generated always as identity primary key,
    full_name varchar(120) not null,
    email varchar(255) not null unique,
    phone varchar(40),
    password_hash varchar(255) not null,
    role varchar(32) not null default 'client' check (role in ('client', 'admin')),
    is_active boolean not null default true,
    accepted_terms boolean not null default false,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    last_login timestamptz
);

alter table public."user"
    add column if not exists full_name varchar(120),
    add column if not exists phone varchar(40),
    add column if not exists is_active boolean not null default true,
    add column if not exists accepted_terms boolean not null default false,
    add column if not exists updated_at timestamptz not null default now(),
    add column if not exists last_login timestamptz;

update public."user"
set full_name = coalesce(nullif(full_name, ''), 'Usuario sin nombre')
where full_name is null;

alter table public."user"
    alter column full_name set not null;

create table if not exists public.password_reset_token (
    id integer generated always as identity primary key,
    user_id integer not null references public."user"(id) on delete cascade,
    token varchar(255) not null unique,
    expires_at timestamptz not null,
    used_at timestamptz,
    created_at timestamptz not null default now()
);

create index if not exists idx_user_email on public."user" (email);
create index if not exists idx_user_role on public."user" (role);
create index if not exists idx_password_reset_token_user_id on public.password_reset_token (user_id);
create index if not exists idx_password_reset_token_token on public.password_reset_token (token);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists trg_user_set_updated_at on public."user";
create trigger trg_user_set_updated_at
before update on public."user"
for each row
execute function public.set_updated_at();
