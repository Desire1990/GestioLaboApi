#pip install pycryptodomex
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


new_key = RSA.generate(2048)

private_key = new_key.exportKey("PEM")
public_key = new_key.publickey().exportKey("PEM")

# print(private_key.decode("utf-8"))
fd = open("private_key.pem", "wb")
fd.write(private_key)
fd.close()

# print(public_key.decode("utf-8"))
fd = open("public_key.pem", "wb")
fd.write(public_key)
fd.close()

message = input('Enter what you need to be crypted!!! \n\n')


# encryption
pubkey = RSA.import_key(open('public_key.pem').read())
cipher_pub = PKCS1_OAEP.new(pubkey)
ciphertext = cipher_pub.encrypt(str(message).encode('utf-8'))
print(ciphertext)
print('\n\n')

# decryption
privkey = RSA.import_key(open('private_key.pem').read())
cipher_priv = PKCS1_OAEP.new(privkey)
plaintext = cipher_priv.decrypt(ciphertext)
print (plaintext.decode("utf-8"))

