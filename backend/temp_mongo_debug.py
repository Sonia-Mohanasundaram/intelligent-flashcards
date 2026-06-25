import ssl
import socket
import certifi
import traceback
from pymongo import MongoClient

host='ac-zzjsua7-shard-00-00.d3r0e8c.mongodb.net'
port=27017

print('certifi:', certifi.where())
print('pymongo:', __import__('pymongo').version)
print('openssl:', ssl.OPENSSL_VERSION)
print('raw TLS test')
ctx=ssl.create_default_context(cafile=certifi.where())
for af in [socket.AF_INET, socket.AF_INET6]:
    try:
        print('af', af)
        addr = socket.getaddrinfo(host, port, af, socket.SOCK_STREAM)[0][4]
        print('addr', addr)
        s = socket.socket(af, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect(addr)
        ss = ctx.wrap_socket(s, server_hostname=host)
        print('tls version', ss.version())
        print('cipher', ss.cipher())
        cert = ss.getpeercert()
        if cert:
            print('cert subject', cert.get('subject'))
        ss.close()
    except Exception as e:
        print('ERROR', af, repr(e))
        traceback.print_exc()
print('\ntrying pymongo invalid-cert test')
uri='mongodb+srv://msonia21062005_db_user:Sonia%402005@cluster0.d3r0e8c.mongodb.net/smartflashcard?retryWrites=true&w=majority'
try:
    client=MongoClient(uri, tls=True, tlsAllowInvalidCertificates=True, serverSelectionTimeoutMS=10000, connectTimeoutMS=10000)
    print('client created')
    print('ping', client.admin.command('ping'))
except Exception as e:
    print('pymongo invalid cert failure', repr(e))
    traceback.print_exc()
print('\ntrying pymongo certifi test')
try:
    client=MongoClient(uri, tls=True, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=10000, connectTimeoutMS=10000)
    print('client created')
    print('ping', client.admin.command('ping'))
except Exception as e:
    print('pymongo certifi failure', repr(e))
    traceback.print_exc()
