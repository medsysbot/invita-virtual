create extension if not exists pgcrypto;

create table if not exists public."user" (
    id bigserial primary key,
    full_name varchar(120) not null,
    email varchar(255) not null unique,
    phone varchar(40),
    password_hash varchar(255) not null,
    role varchar(32) not null default 'client' check (role in ('client','admin')),
    is_active boolean not null default true,
    accepted_terms boolean not null default false,
    created_at timestamp without time zone not null default now(),
    updated_at timestamp without time zone not null default now(),
    last_login timestamp without time zone
);

create table if not exists public.password_reset_token (
    id bigserial primary key,
    user_id bigint not null references public."user"(id) on delete cascade,
    token varchar(255) not null unique,
    expires_at timestamp without time zone not null,
    used_at timestamp without time zone,
    created_at timestamp without time zone not null default now()
);

create table if not exists public.template (
    id bigserial primary key,
    name varchar(120) not null,
    description text,
    is_active boolean default true,
    preview_asset_url varchar(512)
);

create table if not exists public.plan (
    id bigserial primary key,
    name varchar(120) not null,
    description text,
    price integer default 0,
    currency varchar(8) default 'ARS',
    is_active boolean default true,
    features_json text
);

create table if not exists public.invitation (
    id bigserial primary key,
    user_id bigint not null references public."user"(id),
    plan_id bigint references public.plan(id),
    template_id bigint references public.template(id),
    title varchar(255),
    date_time varchar(64),
    venue varchar(255),
    body_text text,
    status varchar(32) default 'draft',
    created_at timestamp without time zone default now(),
    updated_at timestamp without time zone default now()
);

create table if not exists public."order" (
    id bigserial primary key,
    user_id bigint not null references public."user"(id),
    invitation_id bigint references public.invitation(id),
    amount integer default 0,
    currency varchar(8) default 'ARS',
    status varchar(32) default 'pending',
    created_at timestamp without time zone default now(),
    updated_at timestamp without time zone default now()
);

create table if not exists public.payment (
    id bigserial primary key,
    order_id bigint not null references public."order"(id),
    provider varchar(64) default 'stub',
    provider_charge_id varchar(128),
    status varchar(32) default 'pending',
    paid_at timestamp without time zone,
    raw_payload text
);

create table if not exists public.testimonial (
    id bigserial primary key,
    author_name varchar(120),
    text text,
    is_approved boolean default false,
    created_at timestamp without time zone default now()
);

create table if not exists public.tip_category (
    id bigserial primary key,
    parent_id bigint references public.tip_category(id),
    name varchar(120) not null,
    slug varchar(120) not null unique,
    position integer default 0,
    is_active boolean default true,
    created_at timestamp without time zone default now(),
    updated_at timestamp without time zone default now()
);

create table if not exists public.tip_article (
    id bigserial primary key,
    category_id bigint not null references public.tip_category(id),
    title varchar(255) not null,
    slug varchar(255) not null unique,
    summary text,
    body_richtext text,
    hero_asset_url varchar(512),
    status varchar(32) default 'draft',
    submitted_by bigint references public."user"(id),
    submitted_at timestamp without time zone,
    reviewed_by bigint references public."user"(id),
    reviewed_at timestamp without time zone,
    review_notes text,
    published_at timestamp without time zone,
    created_at timestamp without time zone default now(),
    updated_at timestamp without time zone default now()
);

create table if not exists public.tip_tag (
    id bigserial primary key,
    name varchar(120) not null unique,
    slug varchar(120) not null unique
);

create table if not exists public.tip_article_tag (
    article_id bigint not null references public.tip_article(id) on delete cascade,
    tag_id bigint not null references public.tip_tag(id) on delete cascade,
    primary key (article_id, tag_id)
);

create table if not exists public.custom_request (
    id bigserial primary key,
    user_id bigint not null references public."user"(id),
    event_type varchar(120),
    event_date varchar(64),
    contact_name varchar(120),
    phone varchar(64),
    email varchar(255),
    details_text text,
    style_refs_text text,
    budget_range varchar(64),
    attachments_count integer default 0,
    status varchar(32) default 'new',
    created_at timestamp without time zone default now(),
    updated_at timestamp without time zone default now()
);

create index if not exists idx_user_email on public."user"(email);
create index if not exists idx_user_role on public."user"(role);
create index if not exists idx_password_reset_token_token on public.password_reset_token(token);
create index if not exists idx_invitation_user_id on public.invitation(user_id);
create index if not exists idx_order_user_id on public."order"(user_id);
create index if not exists idx_order_invitation_id on public."order"(invitation_id);
create index if not exists idx_custom_request_user_id on public.custom_request(user_id);

insert into public.template (name, description, is_active, preview_asset_url)
select 'Clásica', 'Plantilla clásica', true, '/static/img/placeholder.png'
where not exists (select 1 from public.template where name = 'Clásica');

insert into public.template (name, description, is_active, preview_asset_url)
select 'Moderna', 'Plantilla moderna', true, '/static/img/placeholder.png'
where not exists (select 1 from public.template where name = 'Moderna');

insert into public.plan (name, description, price, currency, is_active, features_json)
select 'Básico', 'Funciones esenciales', 100000, 'ARS', true, '{"max_sections":3,"export_pdf":false,"export_link":true}'
where not exists (select 1 from public.plan where name = 'Básico');

insert into public.plan (name, description, price, currency, is_active, features_json)
select 'Pro', 'Funciones avanzadas', 200000, 'ARS', true, '{"max_sections":10,"export_pdf":true,"export_link":true}'
where not exists (select 1 from public.plan where name = 'Pro');

insert into public.tip_category (name, slug, position, is_active)
select 'Casamientos', 'casamientos', 1, true
where not exists (select 1 from public.tip_category where slug = 'casamientos');

insert into public.tip_category (name, slug, position, is_active)
select 'Cumpleaños', 'cumpleanos', 2, true
where not exists (select 1 from public.tip_category where slug = 'cumpleanos');

insert into public.tip_category (name, slug, parent_id, position, is_active)
select '15 años', '15-anos', (select id from public.tip_category where slug = 'cumpleanos'), 1, true
where not exists (select 1 from public.tip_category where slug = '15-anos');

insert into public.tip_category (name, slug, parent_id, position, is_active)
select 'Niños', 'ninos', (select id from public.tip_category where slug = 'cumpleanos'), 2, true
where not exists (select 1 from public.tip_category where slug = 'ninos');

insert into public.tip_category (name, slug, parent_id, position, is_active)
select 'Adultos', 'adultos', (select id from public.tip_category where slug = 'cumpleanos'), 3, true
where not exists (select 1 from public.tip_category where slug = 'adultos');

insert into public.tip_category (name, slug, parent_id, position, is_active)
select 'Tercera edad', 'tercera-edad', (select id from public.tip_category where slug = 'cumpleanos'), 4, true
where not exists (select 1 from public.tip_category where slug = 'tercera-edad');

update public."user"
set role = 'admin', is_active = true
where email = 'tuemail@dominio.com';
