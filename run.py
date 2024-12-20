from app import create_app

FLASK = create_app()
if __name__ == '__main__' :
    FLASK.run(host = '0.0.0.0',port =8080)
