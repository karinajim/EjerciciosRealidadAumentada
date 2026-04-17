from flask import Flask

#Creo el objeto de app flask
app = Flask(__name__)

@app.route("/")
def inicio():
    return("<h1>Hola</h1>")

#Bloque que ejecuta la app
if __name__ == "__main__":
    app.run(debug=True)