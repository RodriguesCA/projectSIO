from flask import Blueprint,render_template, session
from produtos import get_produtos


rotas = Blueprint('rotas', __name__, static_folder='static', static_url_path='/rotas/static', template_folder='templates')


@rotas.route('/', methods=['GET', 'POST'])
def index():
    produtos=get_produtos()
    return render_template('index.html', produtos=produtos)
    


@rotas.route('/shop')
def shop():
    produtos=get_produtos()
    return render_template('shop.html', produtos=produtos)

@rotas.route('/about')
def about():
    return render_template('about.html')


@rotas.route("/profile")
def profile():
    return render_template('profile.html', username=session['username'])

@rotas.route('/login')
def login():
    return render_template('login.html')

@rotas.route("/register")
def register():
    return render_template('register.html')

