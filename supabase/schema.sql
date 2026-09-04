-- CareerLens AI — Supabase (Postgres) schema
-- Run in the Supabase SQL editor, or `supabase db push` with the CLI.
-- Auth is handled entirely by Supabase Auth (auth.users) — spec §26,
-- we never implement password storage ourselves.

create extension if not exists "uuid-ossp";

-- ---------- resumes ----------
create table if not exists resumes (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid not null references auth.users(id) on delete cascade,
    filename text not null,
    storage_path text,                 -- path in Supabase Storage bucket, if file bytes are kept
    extracted_profile jsonb not null,  -- ResumeProfile as JSON (name, contact, education, experience, ...)
    ats_score numeric(5,2),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists idx_resumes_user_id on resumes(user_id);

-- ---------- resume_analysis ----------
-- one row per analysis run (a resume can be re-analyzed after edits)
create table if not exists resume_analysis (
    id uuid primary key default uuid_generate_v4(),
    resume_id uuid not null references resumes(id) on delete cascade,
    ats_breakdown jsonb not null,
    improvement_suggestions jsonb,
    created_at timestamptz not null default now()
);

create index if not exists idx_resume_analysis_resume_id on resume_analysis(resume_id);

-- ---------- skills (normalized taxonomy reference table, optional persisted mirror of ml/extraction/skill_taxonomy.py) ----------
create table if not exists skills (
    id uuid primary key default uuid_generate_v4(),
    canonical_name text not null unique,
    category text
);

-- ---------- resume_skills (many-to-many: resume <-> normalized skill) ----------
create table if not exists resume_skills (
    resume_id uuid not null references resumes(id) on delete cascade,
    skill_id uuid not null references skills(id) on delete cascade,
    primary key (resume_id, skill_id)
);

-- ---------- jobs ----------
-- sample/demo jobs by default (spec §14); a real job-board integration
-- would insert real rows here with is_sample_data = false.
create table if not exists jobs (
    id uuid primary key default uuid_generate_v4(),
    title text not null,
    company text not null,
    location text,
    description text not null,
    required_skills jsonb not null default '[]',
    preferred_skills jsonb not null default '[]',
    experience_years_required numeric(4,1),
    education_required text,
    is_sample_data boolean not null default true,
    created_at timestamptz not null default now()
);

-- ---------- job_analysis ----------
-- cached structured analysis of a user-pasted job description
create table if not exists job_analysis (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid not null references auth.users(id) on delete cascade,
    title text not null,
    raw_description text not null,
    required_skills jsonb not null default '[]',
    preferred_skills jsonb not null default '[]',
    experience_years_required numeric(4,1),
    education_required text,
    created_at timestamptz not null default now()
);

-- ---------- job_matches ----------
create table if not exists job_matches (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid not null references auth.users(id) on delete cascade,
    resume_id uuid not null references resumes(id) on delete cascade,
    job_id uuid references jobs(id) on delete set null,
    job_analysis_id uuid references job_analysis(id) on delete set null,
    overall_score numeric(5,2) not null,
    breakdown jsonb not null,           -- {semantic_similarity, technical_skills, experience, education, role_compatibility, resume_quality}
    matched_skills jsonb not null default '[]',
    missing_skills jsonb not null default '[]',
    created_at timestamptz not null default now()
);

create index if not exists idx_job_matches_user_id on job_matches(user_id);

-- ---------- career_recommendations ----------
create table if not exists career_recommendations (
    id uuid primary key default uuid_generate_v4(),
    resume_id uuid not null references resumes(id) on delete cascade,
    role text not null,
    compatibility numeric(5,2) not null,
    matched_skills jsonb not null default '[]',
    missing_skills jsonb not null default '[]',
    reason text,
    created_at timestamptz not null default now()
);

-- ---------- analysis_history ----------
-- unified feed for the /history page: one row per user-visible analysis event
create table if not exists analysis_history (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid not null references auth.users(id) on delete cascade,
    event_type text not null check (event_type in ('resume_upload', 'resume_reanalysis', 'job_match', 'job_analysis')),
    reference_id uuid,      -- points at resumes.id / job_matches.id / job_analysis.id depending on event_type
    summary text,
    created_at timestamptz not null default now()
);

create index if not exists idx_analysis_history_user_id on analysis_history(user_id);

-- =====================================================================
-- ROW LEVEL SECURITY — every user-owned table only exposes its own rows
-- (spec §28 privacy: user ownership + access control)
-- =====================================================================
alter table resumes enable row level security;
alter table resume_analysis enable row level security;
alter table job_analysis enable row level security;
alter table job_matches enable row level security;
alter table career_recommendations enable row level security;
alter table analysis_history enable row level security;

create policy "Users can manage their own resumes" on resumes
    for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "Users can view analysis of their own resumes" on resume_analysis
    for all using (exists (select 1 from resumes r where r.id = resume_id and r.user_id = auth.uid()));

create policy "Users can manage their own job analyses" on job_analysis
    for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "Users can manage their own job matches" on job_matches
    for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "Users can view recommendations for their own resumes" on career_recommendations
    for all using (exists (select 1 from resumes r where r.id = resume_id and r.user_id = auth.uid()));

create policy "Users can manage their own history" on analysis_history
    for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- jobs / skills are public reference data — readable by anyone, writable only via service role
alter table jobs enable row level security;
create policy "Anyone can read jobs" on jobs for select using (true);

alter table skills enable row level security;
create policy "Anyone can read skills" on skills for select using (true);
