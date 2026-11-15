-- Scenario 1: University Student System
create table Students (
    student_id int primary key,
    email varchar(100) unique,
    name varchar(50),
    age int
);

-- Insert 5 students
insert into Students values
(1, 'ali@gmail.com', 'Ali', 19),
(2, 'sara@gmail.com', 'Sara', 22),
(3, 'ahmed@gmail.com', 'Ahmed', 21),
(4, 'sana@gmail.com', 'Sana', 20),
(5, 'usman@gmail.com', 'Usman', 23);

-- Retrieve students where age > 20
select * 
from Students
where age > 20;

-- Scenario 2: Course Management
create table Courses(
	course_id int primary key,
	course_name varchar(100) unique
);

-- Insert 5 courses
insert into Courses values
(101, 'Database Systems'),
(102, 'Operating Systems'),
(103, 'Artificial Intelligence'),
(104, 'Computer Networks'),
(105, 'Web Development');

-- Show only 2 courses
SELECT * 
FROM Courses
LIMIT 2;

--Scenario 3: Student Management
create table Enrollments(
	enroll_id int primary key,
	student_id int, 
	course_id int,
	foreign key (student_id) references Students (student_id),
	foreign key (course_id) references Courses (course_id)
);

-- insert records
insert into Enrollments values
(1, 1, 101),
(2, 1, 103),
(3, 2, 102),
(4, 3, 101),
(5, 4, 104);

-- Find Enrollments of ID = 1
select *from Enrollments where student_id = 1;

-- Scenario 4: Unique Email Validation
insert into Students values
(6, 'ali@gmail.com', 'Hamza', 24);

-- Scenario 5: Attendance tracking 

create table Attendance(
	attendance_id int primary key,
	student_id int,
	date DATE,
	foreign key (student_id) references Students (student_id)	
);

-- Insert data
insert into Attendance values
(1, 1, '2026-05-01'),
(2, 2, '2026-05-01'),
(3, 1, '2026-05-02'),
(4, 3, '2026-05-02'),
(5, 4, '2026-05-03');

-- Show Distinct student_id
select distinct student_id from Attendance;

-- Scenario 6: Student Count Report
select count(*) as total_students from Students;

-- Scenario 7: Filter Student
select * from Students where age > 18 and name like 'S%';

-- Scenario 9: Top student list
select * from Students order by age asc limit 3;

--Scenario 10: Course Popularity Analysis

select course_id,
count(student_id) as total_students from Enrollments group by course_id;