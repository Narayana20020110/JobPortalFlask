from app import create_app

FLASK = create_app()
if __name__ == '__main__' :
    FLASK.run(port=5678,debug = True)
