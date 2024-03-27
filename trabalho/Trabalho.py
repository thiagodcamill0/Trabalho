from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

def connect_db():
    conn = sqlite3.connect('enquetes.db')
    return conn

@app.route('/api/enquetes', methods=['POST'])
def criar_enquete():
    data = request.get_json()

    if 'pergunta' not in data or 'opcoes' not in data:
        return jsonify({'error': 'Pergunta e opções são campos obrigatórios.'}), 400

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO enquetes (pergunta) VALUES (?)", (data['pergunta'],))
        enquete_id = cursor.lastrowid

        for opcao in data['opcoes']:
            cursor.execute("INSERT INTO opcoes (enquete_id, descricao) VALUES (?, ?)", (enquete_id, opcao))

        conn.commit()

        return jsonify({'success': 'Enquete criada com sucesso!'}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/enquetes', methods=['GET'])
def listar_enquetes():
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, pergunta FROM enquetes")
        enquetes = cursor.fetchall()

        return jsonify({'enquetes': enquetes}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/enquetes/<int:id>', methods=['GET'])
def detalhes_enquete(id):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, pergunta FROM enquetes WHERE id=?", (id,))
        enquete = cursor.fetchone()

        if enquete is None:
            return jsonify({'error': 'Enquete não encontrada'}), 404

        cursor.execute("SELECT id, descricao FROM opcoes WHERE enquete_id=?", (id,))
        opcoes = cursor.fetchall()

        return jsonify({'enquete': {'id': enquete[0], 'pergunta': enquete[1], 'opcoes': opcoes}}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/enquetes/<int:id>/votar', methods=['POST'])
def votar_enquete(id):
    data = request.get_json()

    if 'opcao_id' not in data:
        return jsonify({'error': 'Opcao_id é um campo obrigatório.'}), 400

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM opcoes WHERE enquete_id=? AND id=?", (id, data['opcao_id']))
        opcao = cursor.fetchone()

        if opcao is None:
            return jsonify({'error': 'Opção de voto não encontrada'}), 404

        cursor.execute("INSERT INTO votos (enquete_id, opcao_id) VALUES (?, ?)", (id, data['opcao_id']))

        conn.commit()

        return jsonify({'success': 'Voto registrado com sucesso!'}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/enquetes/<int:id>/resultados', methods=['GET'])
def resultados_enquete(id):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT opcoes.descricao, COUNT(votos.id) AS votos FROM opcoes LEFT JOIN votos ON opcoes.id = votos.opcao_id WHERE opcoes.enquete_id=? GROUP BY opcoes.id", (id,))
        resultados = cursor.fetchall()

        return jsonify({'resultados': resultados}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/api/enquetes/<int:id>/opcoes', methods=['GET'])
def visualizar_opcoes_enquete(id):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, descricao FROM opcoes WHERE enquete_id=?", (id,))
        opcoes = cursor.fetchall()

        if not opcoes:
            return jsonify({'message': 'Nenhuma opção encontrada para esta enquete.'}), 404

        return jsonify({'opcoes': opcoes}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/enquetes/<int:id>/opcoes', methods=['POST'])
def adicionar_opcao_enquete(id):
    data = request.get_json()

    if 'descricao' not in data:
        return jsonify({'error': 'Descrição é um campo obrigatório.'}), 400

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO opcoes (enquete_id, descricao) VALUES (?, ?)", (id, data['descricao']))
        opcao_id = cursor.lastrowid

        conn.commit()

        return jsonify({'success': 'Opção adicionada com sucesso!', 'opcao_id': opcao_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/enquetes/<int:id>', methods=['DELETE'])
def deletar_enquete(id):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM enquetes WHERE id=?", (id,))
        enquete = cursor.fetchone()

        if enquete is None:
            return jsonify({'error': 'Enquete não encontrada'}), 404

        cursor.execute("DELETE FROM enquetes WHERE id=?", (id,))
        cursor.execute("DELETE FROM opcoes WHERE enquete_id=?", (id,))

        conn.commit()

        return jsonify({'success': 'Enquete deletada com sucesso!'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/enquetes/<int:id_enquete>/opcoes/<int:id_opcao>', methods=['DELETE'])
def deletar_opcao_enquete(id_enquete, id_opcao):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM opcoes WHERE enquete_id=? AND id=?", (id_enquete, id_opcao))
        opcao = cursor.fetchone()

        if opcao is None:
            return jsonify({'error': 'Opção de enquete não encontrada'}), 404

        cursor.execute("DELETE FROM opcoes WHERE enquete_id=? AND id=?", (id_enquete, id_opcao))

        conn.commit()

        return jsonify({'success': 'Opção de enquete deletada com sucesso!'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


if __name__ == '__main__':
    app.run(debug=True)
