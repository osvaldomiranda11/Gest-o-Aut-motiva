class Config:
    SECRET_KEY = 'sua_chave_secreta'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://usuario:senha@localhost/gestao_automotiva'
    SQLALCHEMY_TRACK_MODIFICATIONS = False