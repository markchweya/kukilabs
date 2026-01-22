create table if not exists public.notes (
  id uuid primary key default gen_random_uuid(),

  uploader_email text,
  title text not null,
  course text not null,
  tags text[] not null default '{}'::text[],
  consent_to_share boolean not null default false,

  file_path text not null,
  file_name text not null,
  file_hash text not null,

  status text not null default 'pending_review'
    check (status in ('pending_review','needs_edits','rejected','approved')),
  reviewer_comment text,
  reviewed_at timestamptz,

  created_at timestamptz not null default now()
);

create index if not exists notes_status_idx on public.notes(status);
create index if not exists notes_course_idx on public.notes(course);
create unique index if not exists notes_hash_unique on public.notes(file_hash);
