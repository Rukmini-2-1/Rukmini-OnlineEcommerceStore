from flask import Flask, get_flashed_messages, render_template, request,redirect,url_for,flash,session
from pymongo import MongoClient
from faker import Faker
import logging
from datetime import datetime
import re
app=Flask(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler('app.log')
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
app.secret_key = "secret_key"

client=MongoClient("mongodb://localhost:27017")
db=client['FashionStore']
@app.route('/')
@app.route('/home')
def home():
    try:
        logger.info("home page is accessed")
        return render_template("base.html")
    except Exception as e:
        logger.error("Error occured in opening Home page")
        return f'Error:{str(e)}'

@app.route('/admin',methods=('GET','POST'))
def admin():
    # if request.method=='POST':
    try:
        if session['admin']==True:
            logger.info("admin page is accessed")
            return render_template('admin/main.html',admin=session['admin'])
        else:
            return redirect(url_for('home'))
    except Exception as e:
        return f'Error:{str(e)}'


@app.route("/signup",methods=('GET','POST'))
def signup():
    try:
        if request.method=='POST':
            name=request.form['username']
            email=request.form['email']
            password=request.form['password']
            confirm=request.form['confirm_password']
            email=request.form['email']
            pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$'
            if not re.match(pattern,email):
                flash("invalid email address",'warning')
                redirect(url_for('login'))
            elif password!=confirm:
                flash('passwords dont match','warning')
                return redirect(url_for('signup'))
            else:
                fake=Faker()
                userid=fake.pyint()
                db.users.insert_one({'userid':userid,'name':name,'password':password,'email':email})
                return redirect(url_for('login'))
        return render_template("users/signup.html")
    except Exception as e:
        logger.error("Couldnot signup")
        flash("Couldnot signup",'danger')
        return f'Error:{str(e)}'
    
@app.route("/login",methods=('GET','POST'))
def login():
    try:
        if request.method=='POST':
            name=request.form['username']
            password=request.form['password']
            is_admin='admin' in request.form
            if is_admin:
                admin=db.admin.find_one({'name':name,'password':password})
                if admin:
                    session['admin']=True
                    flash('Welcome admin!','success')
                    return redirect(url_for('admin'))
                else:
                    flash("Wrong credentials",'danger')
                    return redirect(url_for('login'))
            else:
                userid=db.users.find_one({'name':name,'password':password},{'_id':0,'userid':1})
                if userid:
                    session['user']=[name,userid['userid']]
                    session.modified=True
                    flash(f'Welcome {session['user'][0]}!','success')
                    return redirect(url_for('home'))
                else:
                    flash("username and password donot match",'danger')
                    return redirect(url_for('login'))
        return render_template("users/login.html")
    except Exception as e:
        return f'Error:{str(e)}'

@app.route("/logout")
def logout():
        try:
            if 'user' in session:
                session.pop('user',None)
                flash('logged out successfully','success')
                return redirect(url_for('home'))
            elif session['admin']:
                session.pop('admin',None)
                flash('logged out successfully','success')
                return redirect(url_for('home'))
        except Exception as e:
            return f'Error:{str(e)}'
 

@app.route("/addproduct", methods=('GET', 'POST'))
def add_product():
    try:
        if session['admin']==True:
            if request.method == 'POST':
                product_id=request.form['id']
                name = request.form['name']
                price = request.form['price']
                desc = request.form['desc']
                category = request.form['product']
                type=request.form['type']
                image = request.files['image']
                if image:
                    image_url=url_for('static',filename='images/products/'+image.filename)
                db.products.insert_one({
                        'id':product_id,
                        'name': name,
                        'price': price,
                        'description': desc,
                        'category': category,
                        'type':type,
                        'image': image_url
                    })
                flash("product successfully added",'success')
                return redirect(url_for('admin'))
            fake=Faker()
            return render_template('products/addproduct.html',fake=fake)
        else:
            flash('login to continue','warning')
            return redirect(url_for('login'))
    except Exception as e:
        logger.critical("Couldnot add product !")
        return f'Error:{str(e)}'
    
@app.route("/deleteproduct",methods=('GET','POST'))
def delete():
    try:
        if request.method=='POST':
            productid=request.form['id']
            result=list(db.products.find({'id':productid}))
            if len(result)==0:
                flash('no such product available','warning')
                return redirect(url_for('admin'))
            else:
                db.products.delete_one({'id':productid})
                flash('product deleted from database','success')
                return redirect(url_for('admin'))
        return render_template('products/deleteproduct.html')
    except Exception as e:
        logger.error("error in deleting product")
        return f'Error:{str(e)} :couldnot delete the product'

@app.route('/search',methods=('POST','GET'))
def search():
    try:
        if request.method=='POST':
            key = request.form['q']
            print(key)
            query={}
            if key:
                query['description']={"$regex": f' *[^a-z]+{key}*', "$options": "i"}
            product = db.products.find(query)
            print(product)
            res=list(product)
            return render_template('products/search_results.html',query=key,products=res)
        else:
            logger.error("COULDNOT DISPLAY RESULTS")
        return redirect(url_for('home'))
    except Exception as e:
        return f'Error:{str(e)}'


@app.route("/<category>/<type>")
@app.route("/<category>")
def products(category, type=None):
    try:
        if category not in ['men','women','kids']:
            return redirect(url_for('home'))
        query = {"category": category.capitalize()}
        if type:
            query["type"] = type.capitalize()
        products = db.products.find(query)
        return render_template('products/displayproducts.html', products=products)
    except Exception as e:
        return f'Error:{str(e)}'

@app.route("/add_to_cart",methods=('GET','POST'))
def add_to_cart():
    try:
        if request.method=='POST':
            selected_product_id=request.form['product_id']
            quantity=int(request.form['quantity'])
            product=db.products.find_one({"id":selected_product_id})
            cartitem={
                'image':product['image'],
                'productid':int(product['id']),
                'name':product['name'],
                'price':float(product['price']),
                'category':product['category'],
                'type':product['type'],
                'description':product['description'],
                'quantity':quantity,
            }
            if 'user' in session:
                userid=session['user'][1]
                cart=db.cart_collection.find_one({'userid':userid})
                if not cart:
                    cart={'userid':userid,'items':[cartitem]}
                else:
                    found_item = False
                    for i in cart['items']:
                        if int(selected_product_id) == int(i.get('productid')):
                            i['quantity'] += quantity
                            found_item = True
                            break
                    if not found_item:
                        cart['items'].append(cartitem)
                db.cart_collection.replace_one({'userid':userid},cart,upsert=True)
        return redirect(url_for('cart'))
    except Exception as e:
        return f'Error:{str(e)}' 


@app.route('/remove_from_cart',methods=['GET','POST'])
def remove_from_cart():

    if 'user' not in session or len(session['user'])<=0:
        return redirect(url_for('cart'))
    if request.method=='POST':
        product_id=int(request.form['product_id'])
        cart_items = db.cart_collection.find_one({'userid':session['user'][1]},{'items':1,'_id':0})
        updated_cart = []
        if cart_items:
            items = cart_items.get('items', []) 
            for item in items:
                if int(item['productid']) != product_id:
                    updated_cart.append(item)
            db.cart_collection.update_one({'userid':session['user'][1]}, {'$set': {'items': updated_cart}}, upsert=False)
    return redirect(url_for('cart'))

@app.route('/empty',methods=('GET','POST'))
def empty_cart():
    try:
        if request.method=='POST':
            result = db.cart_collection.delete_many({'userid':session['user'][1]})
            return redirect('/cart')
    except Exception as e:
        return f'Error:{str(e)}'
    
@app.route('/cart')
def cart():
    try:
        if 'user' not in session or len(session['user'])<=0:
            flash("login required",'warning')
            return redirect(url_for('login'))
        else:
            cart_items = db.cart_collection.find({'userid':session['user'][1]},{'items':1,'_id':0})
            grandtotal=0
            items=[]
            for i in cart_items:
                items = i.get('items', [])  
                subtotal = 0
                for item in items:
                    # access each item in the list and calculate the subtotal
                    subtotal += float(item['price']) * int(item['quantity'])
                grandtotal += subtotal
            return render_template('cart/displaycart.html',cart_items=items,grandtotal=grandtotal)
    except Exception as e:
        return f'Error:{str(e)}'
    
@app.route('/update',methods=('GET','POST'))
def update_cart():
    try:
        if 'user' not in session or len(session['user'])<=0:
            return redirect(url_for('home'))
        if request.method=='POST':
            id=request.form['product_id']
            quantity=int(request.form['quantity'])
            cart = db.cart_collection.find_one({'userid': session['user'][1]})
            if cart:
                items = cart.get('items', [])
                for item in items:
                    if int(item['productid']) == int(id):
                        item['quantity'] = quantity
                        db.cart_collection.update_one({'userid': session['user'][1]}, {'$set': {'items': items}})
                        break
                flash('Item is updated!','success')
            return redirect(url_for('cart'))
    except Exception as e:
        return f'Error:{str(e)}'
        
@app.route('/checkout',methods=('GET',"POST"))
def checkout():
    try:
        if 'user' in session:
            if request.method=='POST':
                address=request.form['address']
                payment=request.form['payment']
                if not address or not payment:
                    return "please provide"
                userid=session['user'][1]
                cart=db.cart_collection.find_one({'userid':userid})
                if cart:
                    cartitems=cart['items']
                    fake=Faker()
                    orderid=fake.pyint()
                    order={
                        'orderid':orderid,
                        'userid':userid,
                        'address':address,
                        'payment':payment,
                        'order-date':datetime.now(),
                        'products':cartitems
                    }
                    db.orders.insert_one(order)
                    return redirect(url_for('confirm_order'))
            return render_template('cart/checkout.html')
    except Exception as e:
        return f'Error:{str(e)}'
    
@app.route('/confirm_order',methods=('GET','POST'))
def confirm_order():
    try:
        if 'user' in session:
            userid=session['user'][1]
            order=db.orders.find_one({'userid':userid})
            if order:
                    cart=db.cart_collection.find_one({'userid':userid})
                    if cart and cart['items']:
                        return redirect(url_for('payment'))
                    else:
                        flash('Payment failed','danger')
                    return redirect(url_for('cart'))
            else:
                flash('orders not found','warning')
                return redirect(url_for('cart'))
        else:
            return redirect(url_for('login'))
    except Exception as e:
        logger.error("error occured in placing order")
        return f'Error:{str(e)}'
    

@app.route('/payment')
def payment():
    try:
        if 'user' in session:
            userid=session['user'][1]
            db.cart_collection.update_one({'userid':userid},{'$set':{'items':[]}})
            return render_template('orders/payment.html')
    except Exception as e:
        flash("payment failed")
        return f'Error:{str(e)}'

@app.route('/orders')
def orders_placed():
    orders=db.orders.find()
    return render_template('orders/orders.html',orders=orders)

if __name__=='__main__':
    app.run(debug=True)  