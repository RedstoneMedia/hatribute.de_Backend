from eureHausaufgabenApp import app

if __name__ == "__main__":
    app.run(
        debug=True,
        host='0.0.0.0',
        port=31812,
        threaded=True,
        ssl_context=('certificate.pem', "key.pem")
    )