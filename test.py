from werkzeug.security import generate_password_hash

password = generate_password_hash('Scott_labs-28')
print(password)