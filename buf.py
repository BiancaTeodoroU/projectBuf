from flask import Flask
from markupsafe import escape
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask import url_for
from flask import redirect
from flask_login import (current_user, LoginManager,
                            login_user, logout_user,
                            login_required)
import hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://projectbuf:toledo23@localhost:3306/buf'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

app.secret_key = 'sopa é janta'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Usuario(db.Model):
    __tablename__ = "usuario"
    id = db.Column('usu_id', db.Integer, primary_key=True)
    nome = db.Column('usu_nome', db.String(256))
    email = db.Column('usu_email', db.String(256))
    senha = db.Column('usu_senha', db.String(256))
    endereco = db.Column('usu_endereco', db.String(256))

    def __init__(self, nome, email, senha, endereco):
        self.nome = nome 
        self.email = email
        self.senha = senha 
        self.endereco = endereco

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

class Categoria(db.Model):
    __tablename__ = "categoria"
    id = db.Column('cat_id', db.Integer, primary_key=True)
    nome = db.Column('cat_nome', db.String(256))
    desc = db.Column('cat_descricao', db.String(256))

    def __init__ (self, nome, desc):
        self.nome = nome
        self.desc = desc

class Compra(db.Model):
    __tablename__ = "compra"
    id = db.Column("idcompra", db.Integer, primary_key=True)
    preco = db.Column("com_preco", db.Float)
    qtd = db.Column("com_qtd", db.Integer)
    total = db.Column("com_total", db.Float)
    anuncio_id = db.Column("anunc_idanuncio", db.Integer, db.ForeignKey("anuncio.anuncio_id"))
    usu_id = db.Column("user_idusuario", db.Integer, db.ForeignKey("usuario.usu_id"))
    
    def __init__(self, preco, qtd, total, anuncio_id, usu_id):
        self.preco = preco
        self.qtd = qtd
        self.total = total
        self.anuncio_id = anuncio_id
        self.usu_id = usu_id

class Pergunta(db.Model):
    __tablename__ = "pergunta"
    id = db.Column("idPergunta", db.Integer, primary_key=True)
    pergunta = db.Column("per_pergunta", db.String(256))
    resposta = db.Column("per_resposta", db.String(256))
    usu_id = db.Column("usu_id", db.Integer, db.ForeignKey("usuario.usu_id"))
    anuncio_id = db.Column("anuncio_id", db.Integer, db.ForeignKey("anuncio.anuncio_id"))
    
    def __init__(self, pergunta, resposta, usu_id, anuncio_id):
        self.pergunta = pergunta
        self.resposta = resposta
        self.usu_id = usu_id
        self.anuncio_id = anuncio_id

class Anuncio(db.Model):
    __tablename__ = "anuncio"
    id = db.Column('anuncio_id', db.Integer, primary_key=True)
    nome = db.Column('anu_nome', db.String(256))
    desc = db.Column('anu_descricao', db.String(256))
    qtd = db.Column('anu_quantidade', db.Integer)
    preco = db.Column('anu_preco', db.Float)
    usu_id = db.Column('user_idusuario',db.Integer, db.ForeignKey("usuario.usu_id"))
    cat_id = db.Column('cat_idcategoria',db.Integer, db.ForeignKey("categoria.cat_id"))

    def __init__(self, nome, desc, qtd, preco, usu_id, cat_id):
        self.nome = nome
        self.desc = desc
        self.qtd = qtd
        self.preco = preco
        self.usu_id = usu_id
        self.cat_id = cat_id

    def get_categoria(self):
        return Categoria.query.get(self.cat_id)

@app.errorhandler(404)
def paginanaoencontrada(error):
    return render_template('pagNaoEncontrada.html')

@login_manager.user_loader
def load_user(id):
    return Usuario.query.get(id)

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        passwd = hashlib.sha512(str(request.form.get('passwd')).encode("utf-8")).hexdigest()

        user = Usuario.query.filter_by(email=email, senha=passwd).first()
        if user:
            login_user(user)
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/cadastro/usuario")
def usuario():
    return render_template('usuario.html', usuarios = Usuario.query.all(), titulo="Usuario")

@app.route("/usuario/criar", methods=['POST'])
def criarusuario():
    hash = hashlib.sha512(str(request.form.get('senha')).encode("utf-8")).hexdigest()
    usuario = Usuario(request.form.get('user'), request.form.get('email'),hash,request.form.get('end'))
    db.session.add(usuario)
    db.session.commit()
    return redirect(url_for('usuario'))

@app.route("/usuario/detalhar/<int:id>")
def buscarusuario(id):
    usuario = Usuario.query.get(id)
    return usuario.nome

@app.route("/usuario/editar/<int:id>", methods=['GET','POST'])
def editarusuario(id):
    usuario = Usuario.query.get(id)
    if request.method == 'POST':
        usuario.nome = request.form.get('user')
        usuario.email = request.form.get('email')
        usuario.passwd = hashlib.sha512(str(request.form.get('passwd')).encode("utf-8")).hexdigest()
        usuario.endereco = request.form.get('endereco')
        db.session.add(usuario)
        db.session.commit()
        return redirect(url_for('usuario'))

    return render_template('editUsuario.html', usuario = usuario, titulo="Usuario")

@app.route("/usuario/deletar/<int:id>")
def deletarusuario(id):
    usuario = Usuario.query.get(id)
    db.session.delete(usuario)
    db.session.commit()
    return redirect(url_for('usuario'))     

@app.route("/config/categoria")
@login_required
def categoria():
    return render_template('categoria.html', categorias = Categoria.query.all(), titulo='Categoria')

@app.route("/categoria/novo", methods=['POST'])
def novacategoria():
    categoria = Categoria(request.form.get('nome'), request.form.get('desc'))
    db.session.add(categoria)
    db.session.commit()
    return redirect(url_for('categoria'))

@app.route("/categoria/editar/<int:id>", methods=['GET','POST'])
def editarcategoria(id):
    categoria = Categoria.query.get(id)
    print(categoria)
    if request.method == 'POST':
        categoria.nome = request.form.get('nome')
        categoria.desc = request.form.get('desc')
        db.session.add(categoria)
        db.session.commit()
        return redirect(url_for('categoria'))

    return render_template('editCategoria.html', categoria = categoria, titulo="Categoria")

@app.route("/categoria/deletar/<int:id>")
def deletarcategoria(id):
    categoria = Categoria.query.get(id)
    db.session.delete(categoria)
    db.session.commit()
    return redirect(url_for('categoria'))     

@app.route("/cadast/anuncio")
@login_required
def anuncio():
    return render_template('anuncio.html', anuncios = Anuncio.query.all(), categorias = Categoria.query.all(), titulo="Anuncio")

@app.route("/anuncio/novo", methods=['POST'])
def novoanuncio():
    print('categoria {} usuario {}'.format(request.form.get('cat'),
        request.form.get('uso')))
    anuncio = Anuncio(
        request.form.get('nome'), 
        request.form.get('desc'),
        request.form.get('qtd'),
        request.form.get('preco'),
        request.form.get('cat'),
        request.form.get('uso'))
    db.session.add(anuncio)
    db.session.commit()
    return redirect(url_for('anuncio'))

@app.route("/anuncio/editar/<int:id>", methods=['GET','POST'])
def editaranuncio(id):
    anuncio = Anuncio.query.get(id)
    categorias = Categoria.query.all()
    if request.method == 'POST':
        anuncio.nome = request.form.get('nome')
        anuncio.desc = request.form.get('desc')
        anuncio.qtd = request.form.get('qtd')
        anuncio.preco = request.form.get('preco')
        anuncio.cat_id = request.form.get('cat')
        anuncio.usu_id = request.form.get('uso')
        db.session.add(anuncio)
        db.session.commit()
        return redirect(url_for('anuncio'))

    return render_template('editAnuncio.html', categorias = categorias, anuncio = anuncio, titulo="Anuncio")

@app.route("/anuncio/deletar/<int:id>")
def deletaranuncio(id):
    anuncio = Anuncio.query.get(id)
    db.session.delete(anuncio)
    db.session.commit()
    return redirect(url_for('anuncio'))     

@app.route("/anuncios/pergunta")
def pergunta():
    return render_template('anuncioPergunta.html', perguntas = Pergunta.query.all())

@app.route("/anunc/fazerpergunta/<int:id>")
def fazerpergunta(id):
    anuncio = Anuncio.query.get(id)
    return render_template("fazerpergunta.html", anuncio = anuncio, usuarios = Usuario.query.all())

@app.route("/anunc/pergunta/criar/<int:id>", methods=['POST'])
def criarpergunta(id):
    anuncio = Anuncio.query.get(id)
    pergunta = Pergunta(request.form.get("pergunta"), "", request.form.get("user"), anuncio.id)
    db.session.add(pergunta)
    db.session.commit()
    return redirect(url_for("pergunta"))

@app.route("/anunc/pergunta/resposta/<int:id>", methods=['GET','POST'])
def editarperguntar(id):
    pergunta = Pergunta.query.get(id) 
    if request.method == "POST":
        pergunta.pergunta = pergunta.pergunta
        pergunta.resposta = request.form.get("resposta")
        pergunta.usu_id = pergunta.usu_id
        pergunta.anuncio_id = pergunta.anuncio_id
        db.session.add(pergunta)
        db.session.commit()
        return redirect(url_for("pergunta"))
    return render_template("responderpergunta.html", pergunta = pergunta)

@app.route("/anuncio/compra/")
def compra():
    return redirect(url_for("index"))

@app.route("/anuncio/comprar/<int:id>")
def comprar(id):
    anuncio = Anuncio.query.get(id)
    aux = anuncio.qtd
    return render_template("comprar.html", aux = aux, anuncio = anuncio, usuarios = Usuario.query.all())

@app.route("/anunc/compra/confirmarcompra/<int:id>", methods=['GET','POST'])
def confirmarcompra(id):
    anuncio = Anuncio.query.get(id)
    if int(request.form.get("qtd")) > anuncio.qtd:
        return render_template("errocompra.html")
    else:
        compra = Compra(anuncio.preco, request.form.get("qtd"), anuncio.preco * float(request.form.get("qtd")), anuncio.id, request.form.get("user"))
        anuncio.nome = anuncio.nome
        anuncio.desc = anuncio.desc
        anuncio.qtd = anuncio.qtd - int(request.form.get("qtd"))
        anuncio.preco = anuncio.preco
        anuncio.usu_id = anuncio.usu_id
        anuncio.cat_id = anuncio.cat_id
        db.session.add(compra)
        db.session.commit()
        db.session.add(anuncio)
        db.session.commit()
        return redirect(url_for("index"))

@app.route("/anuncio/favorito")
def anunFavo():
    return render_template('favoritar.html')

@app.route("/relatorio/vendas")
@login_required
def relaVend():
    return render_template('relaVend.html', compras = Compra.query.all(), anuncios = Anuncio.query.all(), usuarios = Usuario.query.all())

@app.route("/relatorio/compra")
@login_required
def relaCompr():
    return render_template('relaCompr.html', compras = Compra.query.all(), anuncios = Anuncio.query.all(), usuarios = Usuario.query.all())

if __name__ == 'buf':
    db.create_all()