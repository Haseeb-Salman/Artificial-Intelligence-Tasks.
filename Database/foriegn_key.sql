create table department(
dept_name varchar(30) primary key,
dept_head varchar(30)
);
insert into department (dept_name,dept_head) values ('IT','Ravi Kiran'),('Finance',null),('HR','Swati Rao');


create table employee(
id serial primary key,
f_nm varchar(20) not null,
l_nm varchar(20) not null,
age int not null,
location varchar(20) not null default 'Hyderabad',
dept varchar(20) not null
);
insert into employee (f_nm,l_nm,age,dept) values ('mohan','bhargav',30,'IT'),('manoj','bajpai',35,'HR'),('Rani','Kumari',40,'Finance');
insert into employee (f_nm,l_nm,age,dept) values ('priya','darshini',30,'HealthCare');

insert into employee (f_nm,l_nm,age,dept) values ('mohan','bhargav',30,'IT'),('manoj','bajpai',35,'HR'),('Rani','Kumari',40,'Finance');
insert into employee (f_nm,l_nm,age,dept) values ('priya','darshini',30,'HealthCare');


alter table employee add foreign key(dept) references department(dept_name);

delete from employee where dept = 'HealthCare';

alter table employee add foreign key(dept) references department(dept_name);

insert into employee (f_nm,l_nm,age,dept) values ('priya','darshini',30,'HealthCare');
insert into employee (f_nm,l_nm,age,dept) values ('priya','darshini',30,'IT');

delete from department where dept_name = 'HR'; 
delete from employee where dept = 'HR';



create table school (
name varchar, 
schoolname varchar default '360digitmg', 
age int, 
check (age>= 10));

insert into school (name, age) values ('Ram',10), ('Ravi',20);
select * from school;
insert into school (name,age)  values ('Priya',8);

CREATE TABLE products ( 
product_no integer, 
name text, 
price numeric CHECK (price > 0) 
);
insert into products values(1,'apples',100.00),(2,'oranges',200.00);
select * from products;
insert into products values(3,'grapes',-100.00),(4,'plums',200.00); 
insert into products values(3,'grapes',150.00),(4,'plums',200.00);
