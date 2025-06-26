from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Empresa, Usuario, Veiculo, Status, OrdemServico, Produto, MovimentacaoProduto, Venda
from . import db
from .permissions import permissao_requerida

main = Blueprint('main', __name__)

# --- Autenticação ---
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and check_password_hash(usuario.senha, senha):
            login_user(usuario)
            return redirect(url_for('main.dashboard'))
        flash('Login inválido', 'danger')
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

# --- Dashboard ---
@main.route('/')
@login_required
def dashboard():
    total_empresas = Empresa.query.count()
    total_veiculos = Veiculo.query.count()
    total_ordens = OrdemServico.query.count()
    ordens_por_status = db.session.query(Status.nome, db.func.count(OrdemServico.id)).join(OrdemServico).group_by(Status.nome).all()
    return render_template('dashboard.html', total_empresas=total_empresas, total_veiculos=total_veiculos, total_ordens=total_ordens, ordens_por_status=ordens_por_status)

# --- Empresas ---
@main.route('/empresas/cadastrar', methods=['GET', 'POST'])
@login_required
@permissao_requerida('administrador')
def cadastrar_empresa():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        endereco = request.form['endereco']
        if not nome:
            flash('Nome obrigatório', 'danger')
            return redirect(url_for('main.cadastrar_empresa'))
        db.session.add(Empresa(nome=nome, email=email, telefone=telefone, endereco=endereco))
        db.session.commit()
        flash('Empresa cadastrada', 'success')
        return redirect(url_for('main.cadastrar_empresa'))
    return render_template('empresas/form.html')

# --- Listar Empresas ---
@main.route('/empresas', methods=['GET'])
@login_required
@permissao_requerida('administrador')
def listar_empresas():
    empresas = Empresa.query.all()
    return render_template('empresas/listar.html', empresas=empresas)

# --- Veículos ---
@main.route('/veiculos/cadastrar', methods=['GET', 'POST'])
@login_required
@permissao_requerida('administrador', 'estoquista')
def cadastrar_veiculo():
    empresas = Empresa.query.all()
    if request.method == 'POST':
        marca = request.form['marca']
        modelo = request.form['modelo']
        cor = request.form['cor']
        matricula = request.form['matricula']
        ano = request.form['ano']
        id_empresa = request.form['id_empresa']
        if not marca or not matricula or not id_empresa:
            flash('Marca, matrícula e empresa são obrigatórios.', 'danger')
            return redirect(url_for('main.cadastrar_veiculo'))
        veiculo = Veiculo(marca=marca, modelo=modelo, cor=cor, matricula=matricula, ano=ano, id_empresa=id_empresa)
        db.session.add(veiculo)
        db.session.commit()
        flash('Veículo cadastrado com sucesso!', 'success')
        return redirect(url_for('main.cadastrar_veiculo'))
    return render_template('veiculos/form.html', empresas=empresas)

@main.route('/veiculos', methods=['GET'])
@login_required
@permissao_requerida('administrador', 'estoquista')
def listar_veiculos():
    veiculos = Veiculo.query.join(Empresa).add_columns(
        Veiculo.id, Veiculo.marca, Veiculo.modelo, Veiculo.cor,
        Veiculo.matricula, Veiculo.ano, Empresa.nome.label('empresa_nome')
    ).all()
    return render_template('veiculos/listar.html', veiculos=veiculos)

# --- Ordens de Serviço ---
@main.route('/ordens/cadastrar', methods=['GET', 'POST'])
@login_required
@permissao_requerida('administrador', 'vendedor')
def cadastrar_ordem():
    veiculos = Veiculo.query.all()
    status_list = Status.query.all()
    if request.method == 'POST':
        descricao = request.form['descricao']
        preco = request.form['valor']
        id_veiculo = request.form['id_veiculo']
        id_status = request.form['id_status']
        ordem = OrdemServico(descricao=descricao, preco_estimado=preco, veiculo_id=id_veiculo, status_id=id_status, criado_por=current_user.id)
        db.session.add(ordem)
        db.session.commit()
        flash('Ordem de serviço cadastrada com sucesso!', 'success')
        return redirect(url_for('main.cadastrar_ordem'))
    return render_template('ordens/form.html', veiculos=veiculos, status_list=status_list)

# --- Rotas para Empresas ---
@main.route('/ordens', methods=['GET'])
@login_required
@permissao_requerida('administrador', 'vendedor')
def listar_ordens():
    ordens = OrdemServico.query.join(Veiculo).join(Empresa).join(Status).add_columns(
        OrdemServico.id, OrdemServico.descricao, OrdemServico.preco_estimado.label('valor'),
        Veiculo.matricula, Empresa.nome.label('empresa_nome'), Status.nome.label('status_nome'),
        OrdemServico.data_criacao.label('data')
    ).order_by(OrdemServico.data_criacao.desc()).all()
    return render_template('ordens/listar.html', ordens=ordens)
@main.route('/empresas')
@login_required
@permissao_requerida('administrador')
def listar_empresas():
    empresas = Empresa.query.all()
    return render_template('empresas/listar.html', empresas=empresas)

@main.route('/empresas/cadastrar', methods=['GET', 'POST'])
@login_required
@permissao_requerida('administrador')
def cadastrar_empresa():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        endereco = request.form['endereco']
        if not nome:
            flash('Nome é obrigatório.', 'danger')
            return redirect(url_for('main.cadastrar_empresa'))
        empresa = Empresa(nome=nome, email=email, telefone=telefone, endereco=endereco)
        db.session.add(empresa)
        db.session.commit()
        flash('Empresa cadastrada com sucesso!', 'success')
        return redirect(url_for('main.listar_empresas'))
    return render_template('empresas/form.html')
    
@main.route('/empresas/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@permissao_requerida('administrador')
def editar_empresa(id):
    empresa = Empresa.query.get_or_404(id)
    if request.method == 'POST':
        empresa.nome = request.form['nome']
        empresa.email = request.form['email']
        empresa.telefone = request.form['telefone']
        empresa.endereco = request.form['endereco']
        db.session.commit()
        flash('Empresa atualizada com sucesso!', 'success')
        return redirect(url_for('main.listar_empresas'))
    return render_template('empresas/form.html', empresa=empresa)

@main.route('/empresas/excluir/<int:id>', methods=['POST'])
@login_required
@permissao_requerida('administrador')
def excluir_empresa(id):
    empresa = Empresa.query.get_or_404(id)
    db.session.delete(empresa)
    db.session.commit()
    flash('Empresa excluída com sucesso!', 'success')
    return redirect(url_for('main.listar_empresas'))

# --- Rotas para Veiculos ---
@main.route('/veiculos')
@login_required
@permissao_requerida('administrador', 'estoquista')
def listar_veiculos():
    veiculos = Veiculo.query.join(Empresa).add_columns(
        Veiculo.id, Veiculo.marca, Veiculo.modelo, Veiculo.cor,
        Veiculo.matricula, Veiculo.ano, Empresa.nome.label('empresa_nome')
    ).all()
    return render_template('veiculos/listar.html', veiculos=veiculos)

@main.route('/veiculos/cadastrar', methods=['GET', 'POST'])
@login_required
@permissao_requerida('administrador', 'estoquista')
def cadastrar_veiculo():
    empresas = Empresa.query.all()
    if request.method == 'POST':
        marca = request.form['marca']
        modelo = request.form['modelo']
        cor = request.form['cor']
        matricula = request.form['matricula']
        ano = request.form['ano']
        id_empresa = request.form['id_empresa']
        if not marca or not matricula or not id_empresa:
            flash('Marca, matrícula e empresa são obrigatórios.', 'danger')
            return redirect(url_for('main.cadastrar_veiculo'))
        veiculo = Veiculo(marca=marca, modelo=modelo, cor=cor,
                          matricula=matricula, ano=ano, id_empresa=id_empresa)
        db.session.add(veiculo)
        db.session.commit()
        flash('Veículo cadastrado com sucesso!', 'success')
        return redirect(url_for('main.listar_veiculos'))
    return render_template('veiculos/form.html', empresas=empresas)

@main.route('/veiculos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@permissao_requerida('administrador', 'estoquista')
def editar_veiculo(id):
    veiculo = Veiculo.query.get_or_404(id)
    empresas = Empresa.query.all()
    if request.method == 'POST':
        veiculo.marca = request.form['marca']
        veiculo.modelo = request.form['modelo']
        veiculo.cor = request.form['cor']
        veiculo.matricula = request.form['matricula']
        veiculo.ano = request.form['ano']
        veiculo.id_empresa = request.form['id_empresa']
        db.session.commit()
        flash('Veículo atualizado com sucesso!', 'success')
        return redirect(url_for('main.listar_veiculos'))
    return render_template('veiculos/form.html', veiculo=veiculo, empresas=empresas)

@main.route('/veiculos/excluir/<int:id>', methods=['POST'])
@login_required
@permissao_requerida('administrador', 'estoquista')
def excluir_veiculo(id):
    veiculo = Veiculo.query.get_or_404(id)
    db.session.delete(veiculo)
    db.session.commit()
    flash('Veículo excluído com sucesso!', 'success')
    return redirect(url_for('main.listar_veiculos'))

@main.route('/ordens')
@login_required
@permissao_requerida('administrador', 'vendedor')
def listar_ordens():
    ordens = OrdemServico.query.join(Veiculo).join(Status).add_columns(
        OrdemServico.id, OrdemServico.descricao, OrdemServico.data_criacao,
        OrdemServico.data_entrega, OrdemServico.preco_estimado,
        Veiculo.matricula.label('veiculo_matricula'),
        Status.nome.label('status_nome')
    ).all()
    return render_template('ordens/listar.html', ordens=ordens)

@main.route('/ordens/cadastrar', methods=['GET', 'POST'])
@login_required
@permissao_requerida('administrador', 'vendedor')
def cadastrar_ordem():
    veiculos = Veiculo.query.all()
    status_list = Status.query.all()
    if request.method == 'POST':
        descricao = request.form['descricao']
        data_entrega = request.form['data_entrega']
        preco = request.form['preco_estimado']
        status_id = request.form['status_id']
        veiculo_id = request.form['veiculo_id']

        ordem = OrdemServico(
            descricao=descricao,
            data_entrega=data_entrega if data_entrega else None,
            preco_estimado=preco,
            status_id=status_id,
            veiculo_id=veiculo_id,
            criado_por=current_user.id
        )
        db.session.add(ordem)
        db.session.commit()
        flash('Ordem cadastrada com sucesso!', 'success')
        return redirect(url_for('main.listar_ordens'))
    return render_template('ordens/form.html', veiculos=veiculos, status_list=status_list)

@main.route('/ordens/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@permissao_requerida('administrador', 'vendedor')
def editar_ordem(id):
    ordem = OrdemServico.query.get_or_404(id)
    veiculos = Veiculo.query.all()
    status_list = Status.query.all()
    if request.method == 'POST':
        ordem.descricao = request.form['descricao']
        ordem.data_entrega = request.form['data_entrega']
        ordem.preco_estimado = request.form['preco_estimado']
        ordem.status_id = request.form['status_id']
        ordem.veiculo_id = request.form['veiculo_id']
        db.session.commit()
        flash('Ordem atualizada com sucesso!', 'success')
        return redirect(url_for('main.listar_ordens'))
    return render_template('ordens/form.html', ordem=ordem, veiculos=veiculos, status_list=status_list)

@main.route('/ordens/excluir/<int:id>', methods=['POST'])
@login_required
@permissao_requerida('administrador')
def excluir_ordem(id):
    ordem = OrdemServico.query.get_or_404(id)
    db.session.delete(ordem)
    db.session.commit()
    flash('Ordem excluída com sucesso!', 'success')
    return redirect(url_for('main.listar_ordens'))
@main.route('/usuarios')
@login_required
@permissao_requerida('administrador')
def listar_usuarios():
    usuarios = Usuario.query.all()
    return render_template('usuarios/listar.html', usuarios=usuarios)

@main.route('/usuarios/cadastrar', methods=['GET', 'POST'])
@login_required
@permissao_requerida('administrador')
def cadastrar_usuario():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        tipo = request.form['tipo']
        ativo = 'ativo' in request.form

        if Usuario.query.filter_by(email=email).first():
            flash('Email já cadastrado.', 'warning')
            return redirect(url_for('main.cadastrar_usuario'))

        usuario = Usuario(nome=nome, email=email, tipo=tipo, ativo=ativo)
        usuario.set_senha(senha)
        db.session.add(usuario)
        db.session.commit()
        flash('Usuário cadastrado com sucesso!', 'success')
        return redirect(url_for('main.listar_usuarios'))

    return render_template('usuarios/form.html')

@main.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@permissao_requerida('administrador')
def editar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    if request.method == 'POST':
        usuario.nome = request.form['nome']
        usuario.email = request.form['email']
        usuario.tipo = request.form['tipo']
        usuario.ativo = 'ativo' in request.form

        nova_senha = request.form['senha']
        if nova_senha:
            usuario.set_senha(nova_senha)

        db.session.commit()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('main.listar_usuarios'))

    return render_template('usuarios/form.html', usuario=usuario)

@main.route('/usuarios/excluir/<int:id>', methods=['POST'])
@login_required
@permissao_requerida('administrador')
def excluir_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    flash('Usuário excluído com sucesso!', 'success')
    return redirect(url_for('main.listar_usuarios'))
@main.route('/relatorios/vendas', methods=['GET', 'POST'])
@login_required
@permissao_requerida('administrador')
def relatorio_vendas():
    vendas = []
    data_inicial = data_final = None

    if request.method == 'POST':
        data_inicial = request.form.get('data_inicial')
        data_final = request.form.get('data_final')

        if data_inicial and data_final:
            vendas = Venda.query.filter(
                Venda.data >= data_inicial,
                Venda.data <= data_final
            ).all()

    return render_template('relatorios/vendas.html', vendas=vendas, data_inicial=data_inicial, data_final=data_final)
