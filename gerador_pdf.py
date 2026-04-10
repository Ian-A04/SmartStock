from fpdf import FPDF
from database import obter_conexao

def gerar_danfe(nota_id):
    conn, cursor = obter_conexao()

    #busca dados da nota
    cursor.execute("SELECT data FROM notas WHERE id = ?", (nota_id,))

    if not nota:
        print("Nota não encontrada!")
        conn.close()

        return
