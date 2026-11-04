-- CENTRALIZED CLOUD AUTHORIZATION SCHEMA — REVIEW BEFORE APPLYING
-- Target project must be confirmed before this SQL is run.
-- Secrets never belong in profiles, preferences, integration metadata, or this schema.

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text,
  avatar_url text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create table if not exists public.user_preferences (
  user_id uuid primary key references auth.users(id) on delete cascade,
  preferences jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create table if not exists public.user_roles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  role text not null default 'user'
    check (role in ('user', 'premium_user', 'agent', 'operator', 'master_admin')),
  granted_by uuid references auth.users(id),
  granted_at timestamptz not null default now()
);
create table if not exists public.user_subscriptions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  stripe_customer_id text unique,
  stripe_subscription_id text unique,
  plan_tier text not null default 'free',
  status text not null default 'inactive',
  current_period_start timestamptz,
  current_period_end timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists user_subscriptions_user_id_idx on public.user_subscriptions(user_id);

create table if not exists public.integrations (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  provider text not null,
  external_account_id text,
  status text not null default 'pending',
  granted_scopes text[] not null default '{}',
  secret_reference text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(user_id, provider, external_account_id)
);
create index if not exists integrations_user_id_idx on public.integrations(user_id);

create table if not exists public.usage_events (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  event_type text not null,
  quantity numeric(18,6) not null default 1,
  model text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
create index if not exists usage_events_user_created_idx on public.usage_events(user_id, created_at desc);

create table if not exists public.agent_tasks (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete set null,
  agent_name text not null,
  status text not null default 'queued',
  idempotency_key text unique,
  input jsonb not null default '{}'::jsonb,
  output jsonb,
  error_code text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists agent_tasks_user_status_idx on public.agent_tasks(user_id, status, updated_at desc);

create table if not exists public.agent_task_events (
  id uuid primary key default gen_random_uuid(),
  task_id uuid not null references public.agent_tasks(id) on delete cascade,
  event_type text not null,
  details jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
create index if not exists agent_task_events_task_created_idx on public.agent_task_events(task_id, created_at);

create table if not exists public.audit_events (
  id uuid primary key default gen_random_uuid(),
  actor_user_id uuid references auth.users(id) on delete set null,
  action text not null,
  resource_type text,
  resource_id text,
  outcome text not null,
  correlation_id text,
  details jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
create index if not exists audit_events_actor_created_idx on public.audit_events(actor_user_id, created_at desc);

alter table public.conversations
  add column if not exists created_by uuid references auth.users(id) on delete set null;

alter table public.saphira_memory enable row level security;
alter table public.saphira_task_ledger enable row level security;
alter table public.profiles enable row level security;
alter table public.user_preferences enable row level security;
alter table public.user_roles enable row level security;
alter table public.user_subscriptions enable row level security;
alter table public.integrations enable row level security;
alter table public.usage_events enable row level security;
alter table public.agent_tasks enable row level security;
alter table public.agent_task_events enable row level security;
alter table public.audit_events enable row level security;

drop policy if exists profiles_select_own on public.profiles;
create policy profiles_select_own on public.profiles
  for select to authenticated using ((select auth.uid()) = id);
drop policy if exists profiles_insert_own on public.profiles;
create policy profiles_insert_own on public.profiles
  for insert to authenticated with check ((select auth.uid()) = id);
drop policy if exists profiles_update_own on public.profiles;
create policy profiles_update_own on public.profiles
  for update to authenticated using ((select auth.uid()) = id)
  with check ((select auth.uid()) = id);

drop policy if exists preferences_select_own on public.user_preferences;
create policy preferences_select_own on public.user_preferences
  for select to authenticated using ((select auth.uid()) = user_id);
drop policy if exists preferences_insert_own on public.user_preferences;
create policy preferences_insert_own on public.user_preferences
  for insert to authenticated with check ((select auth.uid()) = user_id);
drop policy if exists preferences_update_own on public.user_preferences;
create policy preferences_update_own on public.user_preferences
  for update to authenticated using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

-- Authorization grants are backend-managed; users cannot grant themselves roles.
revoke all on public.user_roles from anon, authenticated;

drop policy if exists subscriptions_select_own on public.user_subscriptions;
create policy subscriptions_select_own on public.user_subscriptions
  for select to authenticated using ((select auth.uid()) = user_id);

drop policy if exists integrations_select_own on public.integrations;
create policy integrations_select_own on public.integrations
  for select to authenticated using ((select auth.uid()) = user_id);
drop policy if exists integrations_insert_own on public.integrations;
create policy integrations_insert_own on public.integrations
  for insert to authenticated with check ((select auth.uid()) = user_id);
drop policy if exists integrations_update_own on public.integrations;
create policy integrations_update_own on public.integrations
  for update to authenticated using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);
drop policy if exists integrations_delete_own on public.integrations;
create policy integrations_delete_own on public.integrations
  for delete to authenticated using ((select auth.uid()) = user_id);

drop policy if exists usage_events_select_own on public.usage_events;
create policy usage_events_select_own on public.usage_events
  for select to authenticated using ((select auth.uid()) = user_id);

drop policy if exists agent_tasks_select_own on public.agent_tasks;
create policy agent_tasks_select_own on public.agent_tasks
  for select to authenticated using ((select auth.uid()) = user_id);
drop policy if exists agent_task_events_select_own on public.agent_task_events;
create policy agent_task_events_select_own on public.agent_task_events
  for select to authenticated using (
    exists (select 1 from public.agent_tasks t
            where t.id = agent_task_events.task_id and t.user_id = (select auth.uid()))
  );
revoke all on public.agent_tasks, public.agent_task_events from anon, authenticated;
grant select on public.agent_tasks, public.agent_task_events to authenticated;

-- Audit history is backend-only and not client-readable or editable.
revoke all on public.audit_events from anon, authenticated;
grant insert on public.audit_events to service_role;

-- Existing memory rows are scoped to their owning auth.users UUID.
drop policy if exists saphira_memory_select_own on public.saphira_memory;
create policy saphira_memory_select_own on public.saphira_memory
  for select to authenticated using ((select auth.uid()) = owner_id);
drop policy if exists saphira_memory_insert_own on public.saphira_memory;
create policy saphira_memory_insert_own on public.saphira_memory
  for insert to authenticated with check ((select auth.uid()) = owner_id);
drop policy if exists saphira_memory_update_own on public.saphira_memory;
create policy saphira_memory_update_own on public.saphira_memory
  for update to authenticated using ((select auth.uid()) = owner_id)
  with check ((select auth.uid()) = owner_id);
drop policy if exists saphira_memory_delete_own on public.saphira_memory;
create policy saphira_memory_delete_own on public.saphira_memory
  for delete to authenticated using ((select auth.uid()) = owner_id);

-- Task writes stay server-side through the backend worker/service identity.
drop policy if exists task_ledger_select_own on public.saphira_task_ledger;
revoke all on public.saphira_task_ledger from anon, authenticated;

-- A member cannot add themselves to an arbitrary conversation.
alter table public.conversations enable row level security;
drop policy if exists conversations_insert_own on public.conversations;
create policy conversations_insert_own on public.conversations
  for insert to authenticated with check ((select auth.uid()) = created_by);
drop policy if exists conversations_update_own on public.conversations;
create policy conversations_update_own on public.conversations
  for update to authenticated using ((select auth.uid()) = created_by)
  with check ((select auth.uid()) = created_by);
drop policy if exists conversations_delete_own on public.conversations;
create policy conversations_delete_own on public.conversations
  for delete to authenticated using ((select auth.uid()) = created_by);

drop policy if exists conversation_members_insert_if_self on public.conversation_members;
drop policy if exists conversation_members_insert_if_creator on public.conversation_members;
create policy conversation_members_insert_if_creator on public.conversation_members
  for insert to authenticated with check (
    user_id = (select auth.uid())
    and exists (select 1 from public.conversations c
                where c.id = conversation_members.conversation_id
                  and c.created_by = (select auth.uid()))
  );

-- Private user files; object key must start with the authenticated user UUID.
insert into storage.buckets (id, name, public)
values ('saphira-user-files', 'saphira-user-files', false)
on conflict (id) do nothing;

drop policy if exists saphira_files_select_own on storage.objects;
create policy saphira_files_select_own on storage.objects
  for select to authenticated using (
    bucket_id = 'saphira-user-files'
    and (storage.foldername(name))[1] = (select auth.uid())::text
  );
drop policy if exists saphira_files_insert_own on storage.objects;
create policy saphira_files_insert_own on storage.objects
  for insert to authenticated with check (
    bucket_id = 'saphira-user-files'
    and (storage.foldername(name))[1] = (select auth.uid())::text
  );
drop policy if exists saphira_files_update_own on storage.objects;
create policy saphira_files_update_own on storage.objects
  for update to authenticated using (
    bucket_id = 'saphira-user-files'
    and (storage.foldername(name))[1] = (select auth.uid())::text
  ) with check (
    bucket_id = 'saphira-user-files'
    and (storage.foldername(name))[1] = (select auth.uid())::text
  );
drop policy if exists saphira_files_delete_own on storage.objects;
create policy saphira_files_delete_own on storage.objects
  for delete to authenticated using (
    bucket_id = 'saphira-user-files'
    and (storage.foldername(name))[1] = (select auth.uid())::text
  );
