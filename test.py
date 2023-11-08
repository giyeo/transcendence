import pyotp
import qrcode
import os

# Generate a random secret key for the user
secret_key = pyotp.random_base32()

# Create a TOTP instance
totp = pyotp.TOTP(secret_key)
# Generate a provisioning URI for the user to scan
uri = totp.provisioning_uri("localhost:8000", issuer_name="transcendence")

# Create a QR code for the user to scan
img = qrcode.make(uri)
img.save("qrcode.png")
# Store the secret_key securely with the user's account

user_input = input("Enter the 6-digit code from Google Authenticator: ")
if totp.verify(user_input):
    # The code is valid; allow access
	print("bem vindo ao app foda")
else:
	print("sai fora rapa, te conheço?")
    # The code is invalid; deny access
