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


create table student(
id int primary key,
first_name varchar(20) not null,
last_name varchar(20) not null,
age int not null,
course_enrolled varchar(20) not null default 'Data Analytics',
course_fee int not null
);
insert into student(id,first_name,last_name,age,course_fee) values (null,'Madhavi','Kumari',24,40000);
insert into student(id,first_name,last_name,age,course_fee) values (1,'Madhavi','Kumari',24,40000);
insert into student(id,first_name,last_name,age,course_fee) values (1,'Madhavi','Kumari',24,40000);
insert into student(id,first_name,last_name,age,course_fee) values (2,'Madhavi','Kumari',24,40000);
select * from student;
drop table student;


create table student(
id int,
first_name varchar(20) not null,
last_name varchar(20) not null,
age int not null,
course_enrolled varchar(20) not null default 'Data Analytics',
course_fee int not null,
primary key(id)
);

insert into student(id,first_name,last_name,age,course_fee) values (1,'Madhavi','Kumari',24,40000);
insert into student(id,first_name,last_name,age,course_fee) values (2,'Madhavi','Kumari',24,40000);


--COMPOSITE PRIMARY KEY
create table sales_rep(
rep_fname varchar(20) not null,
rep_lname varchar(20) not null,
salary int not null
);
insert into sales_rep(rep_fname,rep_lname,salary) values('Anil','Sharma',25000),('Ankit','Verma',30000),('Anil','Sharma',25000);
select * from sales_rep;
drop table sales_rep;



create table sales_rep(
rep_fname varchar(20) not null,
rep_lname varchar(20) not null,
salary int not null,
primary key(rep_fname,rep_lname)
);
insert into sales_rep(rep_fname,rep_lname,salary) values('Anil','Sharma',25000),('Ankit','Verma',30000),('Anil','Sharma',25000);
insert into sales_rep(rep_fname,rep_lname,salary) values('Anil','Sharma',25000),('Ankit','Verma',30000),('Sunil','Sharma',25000);
select * from sales_rep;
