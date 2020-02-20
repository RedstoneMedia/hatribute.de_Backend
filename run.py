from eureHausaufgabenApp import app


if __name__ == "__main__":
    app.run(
        debug=True,
        host='::',
        port=3182,
        threaded=True,
        ssl_context=('test_certificate.pem', "test_key.pem")
    )