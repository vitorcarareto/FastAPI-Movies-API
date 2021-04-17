
create table users (
  id bigserial primary key,
  username varchar(200) not null unique,
  password text not null,
  email varchar not null unique,
  role varchar
);

create table movies (
  id bigserial primary key,
  title varchar(200) not null,
  description text,
  stock integer not null,
  rental_price decimal(10, 2) not null,
  sale_price decimal(10, 2) not null,
  availability boolean not null
);

create table movies_log (
    movie_id bigint not null,
    updated_field text not null,
    old_value text not null,
    new_value text not null,
    updated_datetime timestamp default current_timestamp
)
