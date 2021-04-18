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
  id bigserial primary key,
  movie_id bigint not null references movies(id),
  updated_field text not null,
  old_value text not null,
  new_value text not null,
  updated_datetime timestamp default current_timestamp
);

create table orders (
  id bigserial primary key,
  movie_id bigint not null references movies(id),
  user_id bigint not null references users(id),
  amount integer not null,
  price_paid decimal(10, 2) not null,
  order_type text not null,
  order_datetime timestamp default current_timestamp,
  expected_return_date date,
  returned_date date,
  delay_penalty_paid decimal(10, 2)
);

create table interactions (
  id bigserial primary key,
  movie_id bigint not null references movies(id),
  user_id bigint not null references users(id),
  interaction_type text not null,
  interaction_datetime timestamp default current_timestamp
);
