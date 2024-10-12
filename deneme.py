from flask import Flask, request, jsonify
import pyodbc
from datetime import datetime
import traceback

app = Flask(__name__)

def get_db_connection():
    try:
        # ODBC veri kaynağı adını (MySQLServer gibi) belirtin
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=.\\SQLEXPRESS;'  # Server parametresini kullanın
            'DATABASE=NovaAkademi;'
            'Trusted_Connection=yes;'
        )
        return conn
    except pyodbc.Error as e:
        print(f"Veri tabanı bağlantı hatası: {e}")
        return None

@app.route('/add-book', methods=['POST'])
def add_book():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Veritabanına bağlanılamadı"}), 500

    try:
        data = request.json
        print(f"Alınan veri: {data}")

        yazar_id = data.get('YazarID')
        baslik = data.get('Başlık')
        yayin_yili_str = data.get('YayınYılı')

        if yazar_id is None or baslik is None or yayin_yili_str is None:
            return jsonify({"error": "Eksik veri: YazarID, Başlık ve YayınYılı gerekli."}), 400

        try:
            yayin_yili = datetime.strptime(yayin_yili_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "YayınYılı geçersiz formatta. Format: YYYY-MM-DD"}), 400

        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO dbo.Kitaplar (YazarID, Başlık, YayınYılı) VALUES (?,?,?)",
            (yazar_id, baslik, yayin_yili)
        )
        conn.commit()

        return jsonify({"message": "Kitap başarıyla eklendi."}), 201

    except pyodbc.Error as e:
        print(f"Hata: {e}")
        print("Traceback:", traceback.format_exc())
        return jsonify({"error": f"Veritabanı hatası: {e}"}), 500

    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
     app.run(host='0.0.0.0', port=5000, debug=True)