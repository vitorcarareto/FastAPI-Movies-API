-- Tabela de cadastro de pessoas
create table users (
  id bigserial primary key,
  username varchar(200) not null unique,
  password text not null,
  email varchar not null unique,
  role varchar
);
