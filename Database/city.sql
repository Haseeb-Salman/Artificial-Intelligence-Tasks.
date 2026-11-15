create table student(
first_name varchar(20) not null,
last_name varchar(20) not null,
age int not null,
course_enrolled varchar(20) not null default 'Data Analytics',
course_fee int not null
);
insert into student(first_name,last_name,age,course_fee) values ('Madhavi','Kumari',24,40000);
insert into student(first_name,last_name,age,course_fee) values ('Madhavi','Kumari',24,40000);
select * from student;
drop table student;

--CREATE A TABLE WITH AN "ID"COLUMN
create table student(
id int,
first_name varchar(20) not null,
last_name varchar(20) not null,
age int not null,
course_enrolled varchar(20) not null default 'Data Analytics',
course_fee int not null
);
insert into student(id,first_name,last_name,age,course_fee) values (1,'Madhavi','Kumari',24,40000);
insert into student(id,first_name,last_name,age,course_fee) values (1,'Madhavi','Kumari',24,40000);
select * from student;
drop table student;
