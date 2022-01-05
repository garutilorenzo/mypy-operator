import base64
from cryptography.fernet import Fernet

SECRET  = bytes("dosyQXJFy6OLK90XSJFUTAhqHYftPsxUcxnHKBd3NIY=", "latin-1")

def encode(password):
    fernet = Fernet(SECRET)
    return fernet.encrypt(password.encode())

def decode(enc_password):
    fernet = Fernet(SECRET)
    return fernet.decrypt(enc_password).decode()

if __name__ == '__main__':
    password = 'test'
    encoded = encode(password)
    a = encoded.decode('utf-8')
    decoded = decode(a.encode('utf-8'))
    print(decoded)