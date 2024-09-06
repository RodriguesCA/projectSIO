from flask import Flask,request,jsonify, redirect, url_for, session, flash,render_template,Blueprint,render_template_string
from rotas import rotas
from flask_cors import CORS
from html import escape
from datetime import timedelta
import pyotp
import qrcode
from flask_wtf.csrf import CSRFProtect

from produtos import get_produtos
from connection import get_connection

app = Flask(__name__)
CORS(app)
csrf = CSRFProtect(app)

app.register_blueprint(rotas)

app.secret_key='log key'

produtos = get_produtos()
carrrinho=[]

app.config['SESSION_COOKIE_HTTPONLY'] = True 
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=2)

@app.before_request
def make_session_permanent():
    session.permanent = True
'''
@app.after_request
def set_secure_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self';"
    return response
    '''

def product_exists(product_name, products):
    """Verifica se um produto com determinado nome existe na lista de produtos"""
    print(products)
    for product in products:
        if product["NOME"] == product_name:
            return True
    return False

def get_product_by_name(productName, products):
    for product in products:
        if product["NOME"] == productName:
            return product
    return None

def get_review(productName):
    conn = get_connection()
    print(productName)

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Review WHERE NOME_P = ?", (productName,))

    reviews = cursor.fetchall()
    reviews_dict = [{"NOME_U": r[0], "NOME_P": r[1], "N_STARS": r[2], "COMENTARIO": r[3]} for r in reviews]

    cursor.close()
    conn.close()

    return reviews_dict

@app.route('/add_to_cart/<product>', methods=['POST', 'GET'])
def add_to_cart(product, carrinho=carrrinho):
    # Obter o nome e o preço do produto
    product_info = product.split(',')
    product_name = product_info[0]
    product_price = float(product_info[1])
    
    # Obter a lista de produtos a partir do banco de dados
    products = get_produtos()

    # Verificar se o produto existe
    if product_exists(product_name, products):
        # Adicionar o produto ao carrinho
        for item in carrinho:
            if item['NOME'] == product_name:
                item['Quantidade'] += 1
                break
        else:
            carrinho.append({'NOME': product_name, 'PRECO': product_price, 'Quantidade': 1})
        
        print(carrinho)
        return jsonify({'message': 'Product added to the cart successfully!'}), 200
    else:
        return jsonify({'message': 'Product not found!'}), 404
    
@app.route('/remove_from_cart/<product>', methods=['POST'])
def remove_from_cart(product, carrinho=carrrinho):
    # Obter o nome e o preço do produto
    product_info = product.split(',')
    product_name = product_info[0]

    # Verificar se o produto existe
    if (product_exists(product_name, carrinho)):
        # Remover o produto do carrinho
        for item in carrinho:
            if item['NOME'] == product_name:
                item['Quantidade'] -= 1
                if item['Quantidade'] == 0:
                    carrinho.remove(item)
                break
        return jsonify({'message': 'Product removed to the cart successfully!'}), 200
    else:
        return jsonify({'message': 'Product not found!'}), 404
    
@app.route('/delete_from_cart/<product>', methods=['POST','GET'])
def delete_from_cart(product, carrinho=carrrinho):
    # Obter o nome e o preço do produto
    product_info = product.split(',')
    product_name = product_info[0]
    product_price = float(product_info[1])

    # Verificar se o produto existe
    if (product_exists(product_name, carrinho)):
        # Remover o produto do carrinho
        for item in carrinho:
            if item['NOME'] == product_name:
                carrinho.remove(item)
                break
        return jsonify({'message': 'Product removed to the cart successfully!'}), 200
    else:
        return jsonify({'message': 'Product not found!'}), 404

@app.route('/quantidades/<product>')
def quantidades(carrinho=carrrinho):

    return jsonify(quantidades)

@app.route('/checkout', methods=['POST'])
def checkout():
    # Limpe o carrinho aqui
    global carrinho  
    carrinho = []
    # Redirecione o usuário para a página 'thankyou.html'
    return redirect(url_for('thank_you'))

@app.route('/thankyou')
def thank_you():
    return render_template('thankyou.html')

@app.route('/cart')
def cart():
    global carrrinho
    carrinho=carrrinho
    return render_template('cart.html', carrinho=carrinho, produtos=produtos)

@app.route('/register', methods=['POST'])
@csrf.exempt
def register():
    username = request.form['username']
    password = request.form['password']

    otp_secret = pyotp.random_base32()

    uri = pyotp.totp.TOTP(otp_secret).provisioning_uri(name=username, issuer_name='DETShop')
    
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"INSERT INTO Users (USERNAME, PASS, OTP) VALUES (?, ?, ?)", username, password, otp_secret)
    conn.commit()
    cursor.close()
    conn.close()

    session['otp_uri'] = uri

    img = qrcode.make(uri)
    img.save('./static/images/qrcode.png')

    return redirect('loginCode')

@app.route('/login', methods=['POST'])
@csrf.exempt
def login():
    username = request.form['username']
    password = request.form['password']
    otp_code = request.form['otp_code']  
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM Users WHERE USERNAME = ? AND PASS = ?", username, password)
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result:
        user_id, stored_password, otp_secret = result

        totp = pyotp.TOTP(otp_secret)
        if not totp.verify(otp_code):
            return render_template('login.html', alert_message="Invalid OTP code")
    
        if stored_password == password:
            session['logged_in'] = True
            session['username'] = username
            return render_template('profile.html', username=username)
        else:
            return render_template('login.html', alert_message="Invalid username or password")
    else:
        return render_template('login.html', alert_message="Invalid username or password")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/product/<productName>')
def product(productName):
    products = get_produtos()
    product = get_product_by_name(productName, products)
    reviews_dict = get_review(productName)
    if product != None: return render_template('product.html', product=product, reviews=reviews_dict)
    else: redirect('/shop')

@app.route('/submit_review', methods=['POST'])
@csrf.exempt
def submit_review():
    data = request.json
    review_text = escape(data.get('reviewText'))
    review_stars = data.get('reviewStars')
    product_name = escape(data.get('productName'))
    username = escape(data.get('username'))

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO Review (NOME_U, NOME_P, N_STARS, COMENTARIO) VALUES (?, ?, ?, ?)", username, product_name, review_stars, review_text)  
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Review submitted successfully!'})
    except Exception as e:
        print(f"Error inserting review: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while submitting your review.'})


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="5000")