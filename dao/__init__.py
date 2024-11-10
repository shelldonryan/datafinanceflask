import psycopg2
import datetime

def conectardb():
    con = psycopg2.connect(
        host='localhost',
    database = 'datafinanceflask',
        user = 'postgres',
    password = '12345'
    )

    return con


def login(user,senha):
    con = conectardb()
    cur = con.cursor()
    sq = f"SELECT nome, estado, profissao, email from usuario where email='{user}' and senha='{senha}'  "
    cur.execute(sq)
    saida = cur.fetchall()

    cur.close()
    con.close()

    return saida

def inserir_user(nome, email, estado, profissao, senha):

    agora = datetime.datetime.now()


    data_formatada = agora.strftime('%d/%m/%Y')
    conn = conectardb()
    cur = conn.cursor()
    try:
        sql = f"INSERT INTO usuario (email, senha, nome, estado, profissao) VALUES ('{email}','{senha}','{nome}', '{estado}', '{profissao}' )"
        cur.execute(sql)

        sql2 = f"INSERT INTO carteira (email_usuario, data_criacao) VALUES('{email}', '{data_formatada}')"
        cur.execute(sql2)


    except psycopg2.IntegrityError:
        conn.rollback()
        exito = False
    else:
        conn.commit()
        exito = True

    cur.close()
    conn.close()
    return exito


def inserir_acao(nome, email, estado, profissao, senha):
    conn = conectardb()
    cur = conn.cursor()
    try:
        sql = f"INSERT INTO usuario (email, senha, nome, estado, profissao) VALUES ('{email}','{senha}','{nome}', '{estado}', '{profissao}' )"
        cur.execute(sql)
    except psycopg2.IntegrityError:
        conn.rollback()
        exito = False
    else:
        conn.commit()
        exito = True

    cur.close()
    conn.close()
    return exito


def criar_tabelas():
    con = conectardb()
    cur = con.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS public.usuario(
        email VARCHAR(255) NOT NULL,
        senha VARCHAR(255) NOT NULL,
        nome VARCHAR(255)  NOT NULL,
        estado text NOT NULL,
        profissao text NOT NULL,
        CONSTRAINT usuarios_pkey PRIMARY KEY (email)
    );
    
    CREATE TABLE carteira (
        email_usuario VARCHAR(255) PRIMARY KEY REFERENCES usuario(email) ON DELETE CASCADE,
        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE acao (
        id SERIAL PRIMARY KEY,
        email_usuario VARCHAR(255) REFERENCES carteira(email_usuario) ON DELETE CASCADE,
        simbolo VARCHAR(10) NOT NULL,
        quantidade INTEGER NOT NULL,
        preco_compra DECIMAL(10, 2) NOT NULL,
        data_compra TIMESTAMP NOT NULL
    );
    """

    cur.execute(create_table_query)
    con.commit()
    con.close()


def getEmpresasListadasAntigas():
    return ['ABCB4', 'ABEV3', 'AGRO3', 'ALUP11', 'ARZZ3', 'B3SA3', 'BBAS3', 'BBDC4', 'BBSE3', 'BEEF3', 'BPAN4',
               'BRAP4', 'BRSR6', 'CAMB3', 'CCRO3', 'CIEL3', 'CMIG4', 'CPFE3', 'CPLE6', 'CSMG3', 'CSUD3', 'CYRE3',
               'DEXP3', 'EGIE3', 'ENGI11', 'EVEN3', 'FESA4', 'FLRY3', 'FRAS3', 'GGBR4', 'GOAU4', 'GRND3', 'HYPE3',
               'ITSA4', 'ITUB4', 'JHSF3', 'KEPL3', 'LEVE3', 'LREN3', 'MILS3', 'MULT3', 'ODPV3', 'PETR4', 'PINE4',
               'PNVL3', 'POMO4', 'POSI3', 'PSSA3', 'RANI3', 'RAPT4', 'RENT3', 'ROMI3', 'SANB11', 'SBSP3', 'SLCE3',
               'SMTO3', 'STBP3', 'TAEE11', 'TASA4', 'TGMA3', 'TIMS3', 'TOTS3', 'TRIS3', 'TRPL4', 'TUPY3', 'UGPA3',
               'UNIP6', 'VALE3', 'VIVT3', 'VLID3', 'VULC3', 'WEGE3']

def getMinhasEmpresasListadas():
    return ['BBSE3', 'PSSA3', 'BBAS3','BRSR6','ITSA4','EGIE3','ALUP11','TAEE11','KLBN4','VALE3', 'TUPY3','FESA4']

def getCarteira():
    return {'SIMH3':30, 'TAEE11':6, 'ALUP11':13, 'EGIE3':8, 'KLBN11':11, 'ITSA4':30,
             'PSSA3':7, 'BBSE3':9, 'VBBR3':13, 'BRSR6':22, 'TUPY3':6, 'BBAS3':6, 'VALE3':3}

