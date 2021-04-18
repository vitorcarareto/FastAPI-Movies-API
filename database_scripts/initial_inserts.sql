-- Insert admin user with hashed password '123'
insert into users (username,password,email,role)
values ('admin','$2b$12$gRT8jF72.F0i.Q5ZNO.62uHRE/qhYmRZsYG8Xzd4Y2yl/pqTArgnG','vitor.carareto@gmail.com','admin');
