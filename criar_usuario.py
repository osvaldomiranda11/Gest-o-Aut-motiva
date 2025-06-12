from app import app, db
from models import Usuario
from werkzeug.security import generate_password_hash

with app.app_context():
    admin = Usuario(
        nome="Administrador",
        email="admin@mail.com",
        senha=generate_password_hash("admin123"),
        perfil="administrador"
    )

    vendedor = Usuario(
        nome="Vendedor",
        email="vendedor@mail.com",
        senha=generate_password_hash("vendedor123"),
        perfil="vendedor"
    )

    estoquista = Usuario(
        nome="Estoquista",
        email="estoque@mail.com",
        senha=generate_password_hash("estoque123"),
        perfil="estoquista"
    )

    db.session.add_all([admin, vendedor, estoquista])
    db.session.commit()
    print("Usuários criados com sucesso!")
