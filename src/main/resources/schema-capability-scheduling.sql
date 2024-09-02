create table if not exists allocatable_capabilities (
    id uuid not null,
    resource_id uuid not null,
    capability jsonb not null,
    from_date timestamp with time zone not null,
    to_date timestamp with time zone not null,
    primary key (id));
