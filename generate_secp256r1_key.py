from cryptography.hazmat.primitives.asymmetric import ec

signer = ec.generate_private_key(ec.SECP256R1())
private_key = signer.private_numbers().private_value
print(private_key)
