from datetime import datetime
from . import db
from flask_login import UserMixin

class Empresa(db.Model):
    __tablename__ = 'empresas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255))
    telefone = db.Column(db.String(50))
    endereco = db.Column(db.String(255))
    data_registo = db.Column(db.DateTime, default=datetime.utcnow)
    
    veiculos = db.relationship('Veiculo', backref='empresa', lazy=True)

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.String(20), nullable=False, default='vendedor')
    ativo = db.Column(db.Boolean, default=True)
    data_registo = db.Column(db.DateTime, default=datetime.utcnow)

class Veiculo(db.Model):
    __tablename__ = 'veiculos'
    id = db.Column(db.Integer, primary_key=True)
    marca = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(100))
    cor = db.Column(db.String(50))
    matricula = db.Column(db.String(50), unique=True)
    ano = db.Column(db.String(10))
    id_empresa = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)

    ordens = db.relationship('OrdemServico', backref='veiculo', lazy=True)

class Status(db.Model):
    __tablename__ = 'status'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)

class OrdemServico(db.Model):
    __tablename__ = 'ordens_servico'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_entrega = db.Column(db.DateTime)
    preco_estimado = db.Column(db.Float)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculos.id'))
    criado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))

    status = db.relationship('Status', backref='ordens', lazy=True)
    usuario = db.relationship('Usuario', foreign_keys=[criado_por])

class Historico(db.Model):
    __tablename__ = 'historico'
    id = db.Column(db.Integer, primary_key=True)
    ordem_id = db.Column(db.Integer, db.ForeignKey('ordens_servico.id'))
    alterado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    data_alteracao = db.Column(db.DateTime, default=datetime.utcnow)
    observacao = db.Column(db.Text)

    ordem = db.relationship('OrdemServico', backref='historicos', lazy=True)
    usuario = db.relationship('Usuario', foreign_keys=[alterado_por])

# Modelos adicionais para stock e vendas
class Produto(db.Model):
    __tablename__ = 'produtos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    categoria = db.Column(db.String(100))
    quantidade = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=0)

class MovimentacaoProduto(db.Model):
    __tablename__ = 'movimentacoes'
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'))
    tipo = db.Column(db.String(20))  # entrada ou saida
    quantidade = db.Column(db.Integer)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    observacao = db.Column(db.Text)

    produto = db.relationship('Produto', backref='movimentacoes', lazy=True)

class Venda(db.Model):
    __tablename__ = 'vendas'
    id = db.Column(db.Integer, primary_key=True)
    cliente = db.Column(db.String(255))
    data = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Float)
    itens = db.relationship('ItemVenda', backref='venda', lazy=True)

class ItemVenda(db.Model):
    __tablename__ = 'itens_venda'
    id = db.Column(db.Integer, primary_key=True)
    venda_id = db.Column(db.Integer, db.ForeignKey('vendas.id'))
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'))
    quantidade = db.Column(db.Integer)

    produto = db.relationship('Produto')