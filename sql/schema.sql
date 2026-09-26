CREATE DATABASE IF NOT EXISTS retailpulse;
USE retailpulse;

create table Customers (
Customer_Id int primary key,
Customer_name varchar(100) not null,
email varchar(150) unique,
city varchar (50) ,
signup_date date );

Create  table stores( 
store_id int primary key,
store_name varchar(100) not null,
city varchar(50) not null,
openinig_date DATE
);

create table products (
product_id int primary key,
product_name varchar(120) not null,
category varchar(50) not null,
Unit_price decimal (10,2) check( Unit_price > 0),
recorder_level int default 10);

create table orders ( 
order_id int primary key,
Customer_id int ,
store_id int,
Order_date DATE not null,
payment_method Varchar(30),
order_status varchar (30),
foreign key (Customer_id)
references
Customers (Customer_id),
foreign key (store_id)
references Stores(store_id));

create table order_items(
order_id int ,
product_id int,
quantity int check (quantity > 0),
selling_price decimal (10,2) check (selling_price > 0),

foreign key (order_id)
references orders (order_id),

foreign key (product_id)
references products(product_id),

primary key (order_id,Product_id));

create table inventory(
store_id int,
product_id int,
stock_quantity int check(stock_quantity>=0),
last_updated date ,

foreign key (store_id)
references stores (store_id),

foreign key (Product_id)
references
products(product_id));

alter table inventory
add
primary key (store_id,Product_id);