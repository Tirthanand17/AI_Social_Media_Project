from fastapi import FastAPI

app = FastAPI(title='Storage App')

@app.get('/')
def home():
    return {'status': 'ok'}
