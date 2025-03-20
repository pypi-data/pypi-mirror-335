import requests
import json
import sqlite3
import hashlib
import numpy as np
from pydantic import BaseModel
import os
from pyngrok import ngrok
from flask import Flask, request, jsonify
import qxenonsign.core as qxenonsign  
import threading

app = Flask(__name__)


# 크립토그래픽 파라미터
N = 256
q = 8380417

def keygen():
    """키 생성 함수"""
    np.random.seed()
    A = np.random.randint(-q // 2, q // 2, (N, N), dtype=np.int64)
    s = np.random.randint(-1, 2, N, dtype=np.int64)
    e = np.random.randint(-1, 2, N, dtype=np.int64)
    t = np.mod(A @ s + e, q)
    return {"public_key": t.tolist(), "secret_key": s.tolist()}

def sign(sk, message: str):
    """서명 생성 함수"""
    c = hashlib.shake_128(message.encode()).digest(32)
    np.random.seed(int.from_bytes(c, 'big') % (2**32))
    z = np.random.randint(-q // 2, q // 2, len(sk), dtype=np.int64)
    
    return {
        "hash": c.hex(),
        "signature": {"signature_values": z.tolist()
    }}


def connection(server_url):
    """서버에 연결 확인"""
    try:
        response = requests.get(server_url)
        if response.status_code == 200:
            print("서버 연결 성공!")
            print("서버 응답: ", response.text)
            return True  # 연결 성공 시 True 반환
        else:
            print(f"서버 연결 실패: {response.status_code}")
            return False  # 연결 실패 시 False 반환
    except requests.exceptions.RequestException as e:
        print(f"서버에 연결하는 중 오류가 발생했습니다: {e}")
        return False  # 예외 발생 시 False 반환



def verify_signature(server_url, public_key, signature, message):
    """서버의 서명 검증 요청"""
    verify_url = f"{server_url}/verify_signature"
    data = {
        'public_key': public_key,
        'signature': signature,
        'message': message
    }

    try:
        response = requests.post(verify_url, json=data)
        if response.status_code == 200:
            result = response.json()
            print(result["message"])
        elif response.status_code == 500:
            print("서버에서 500 오류 발생: 내부 서버 오류")
        else:
            print(f"서버에서 서명 검증 실패: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"서버에 서명 검증 요청 중 오류가 발생했습니다: {e}")


def start_ngrok(port: int):
    """Ngrok 터널을 생성하고 Public URL을 반환하는 함수"""
    try:
        NGROK_AUTH_TOKEN = os.getenv('NGROK_AUTH_TOKEN')  # 환경 변수에서 인증 토큰 가져오기
        if not NGROK_AUTH_TOKEN:
            raise ValueError("Ngrok 인증 토큰이 설정되지 않았습니다. 환경 변수를 확인해주세요.")
        
        ngrok.set_auth_token(NGROK_AUTH_TOKEN)
        tunnel = ngrok.connect(port)
        public_url = tunnel.public_url  # NgrokTunnel 객체에서 public_url을 추출
        return public_url
    except Exception as e:
        print(f"Ngrok 연결 실패: {e}")
        raise



def verify(message: str, received_hash: str, public_key: list):
    """서명 검증 함수"""
    message_hash = hashlib.shake_128(message.encode()).digest(32).hex()
    return message_hash == received_hash



@app.route('/')
def hello():
    return "서버가 연결되었습니다!"

@app.route('/get_server_url')
def get_server_url():
    try:
        return jsonify({"server_url": public_url})
    except Exception as e:
        print(f"서버 URL 요청 처리 중 오류 발생: {e}")
        return jsonify({"error": "서버 URL을 가져오는 중 오류 발생"}), 500

@app.route('/verify_signature', methods=['POST'])
def verify_process():
    try:
        data = request.get_json()

        public_key = data['public_key']
        signature = data['signature']
        message = data['message']

        if not isinstance(signature, dict):
            raise ValueError("서명 데이터는 dict 형태여야 합니다.")

        # 서명 검증
        if qxenonsign.verify(message, signature["hash"], public_key):  # verify 함수 사용
            return jsonify({"status": "success", "message": "서명 검증 성공!"})
        else:
            return jsonify({"status": "failure", "message": "서명 검증 실패!"})

    except Exception as e:
        print(f"서명 검증 처리 중 오류 발생: {e}")
        return jsonify({"status": "error", "message": f"오류 발생: {str(e)}"}), 500


def start_server(port=5001):
    global public_url
    try:
        public_url = qxenonsign.start_ngrok(port)  # Ngrok 시작
        threading.Thread(target=app.run, kwargs={"port": port, "use_reloader": False}).start()
        return public_url
    except Exception as e:
        print(f"서버 시작 중 오류 발생: {e}")
        return None






