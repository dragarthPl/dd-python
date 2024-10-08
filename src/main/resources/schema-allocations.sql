create table if not exists project_allocations (
    project_allocations_id uuid not null,
    allocations jsonb not null,
    demands jsonb not null,
    from_date timestamp with time zone,
    to_date timestamp with time zone,
    primary key (project_allocations_id));

create table if not exists allocatable_capabilities (
    id uuid not null,
    resource_id uuid not null,
    possible_capabilities jsonb not null,
    from_date timestamp with time zone not null,
    to_date timestamp with time zone not null,
    primary key (id));
