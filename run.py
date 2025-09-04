# wsgi.py
from DAS import appointment

app = appointment()

if __name__ == "__main__":
    app.run(debug=True)
