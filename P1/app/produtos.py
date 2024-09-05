from connection import get_connection

def get_produtos():
    conn = get_connection()

    query = "SELECT NOME, PRECO FROM Produto"

    cursor = conn.cursor()
    cursor.execute(query)

    produtos = cursor.fetchall()
    produtos_dict = [{"NOME": produto[0], "PRECO": produto[1]} for produto in produtos]

    cursor.close()
    conn.close()

    return produtos_dict