from pwdlib import PasswordHash

pwd_context = PasswordHash.recommended()


# return the user hasdhed pwd
def get_pwd_hash(pwd: str):
    hashed_pwd = pwd_context.hash(pwd)

    return hashed_pwd


def verify_pwd(plain_pwd: str, hashed_pwd: str):
    # returns true if the plain pwd matches de hashed.
    return pwd_context.verify(password=plain_pwd, hash=hashed_pwd)


def create_access_token():
    pass
