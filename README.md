# Rukmini-OnlineEcommerceStore

## Description
Welcome to the project, This is a online e-commerce store made in python using flask framework . This is an online clothing store where users view different outfits and add them to cart.

### Prerequisites
Python 3.6 or later version
MongoDB

Installation and setup

 Clone the repository
 
 git clone :https://github.com/Rukmini-2-1/Rukmini-OnlineEcommerceStore.git
 
 create a virtual environment in the clone
 
 Install dependencies from requirements.txt
 
pip install -r requirements.txt

 install mongoDB 
 
Setup MongoDB 

Start MongoDB server

Create a database named "FashionStore" and create collections "users" , "products" ,"cart_collection" , "admin", "orders"

run the app.py using flask run

### Functionalities
#### Login / signup page :
users have to signup as new user to purchase the items.
After login they will be redirected to home page where users can view the different items .
A session for the user will be created.
#### Home :
In home page, users can view different categories like men ,women,kids wear and can search for any kinds of clothes using search bar.
#### cart :
when users click on add to cart, then they will be redirected to cart where users can update quantity of items, or can remove items from cart.
If user clicks on empty cart option then all the items will be removed from cart.
#### confirm order:
when users click on checkout option , they will be redirected to payment options and address for shipment.
#### Admin :
When admin logs in ,he can add new items, delete existing items and view the orders placed by several users.
#### Database:
The products are stored in products collection
The orders are stored in orders collection 
The users are stored in user collection

