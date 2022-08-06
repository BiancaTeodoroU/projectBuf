from flask import Flask
from markupsafe import escape
from flask import render_template
from flask import request

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/cadastro/usuario")
def usuario():
    return render_template('usuario.html', titulo="Cadastro de Usuario")

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/cadastro/anuncio")
def cadAnun():
    return render_template('cadAnun.html')

@app.route("/anuncio/categoria")
def anunCat():
    return render_template('anunCat.html')

@app.route("/pergunta/anuncio")
def pergAnun():
    return render_template('pergAnun.html')

@app.route("/resposta/anuncio")
def respostAnun():
    return render_template('respostAnun.html')

@app.route("/anuncio/compra")
def anunComp():
    print("anuncio comprado")
    return ""

@app.route("/anuncio/favorito")
def anunFavo():
    print("favorito inserido")
    return f"<h3>Inserido com sucesso</h3>"

@app.route("/relatorio/vendas")
def relaVend():
    return render_template('relaVend.html')

@app.route("/relatorio/compra")
def relaCompr():
    return render_template('relaCompr.html')
