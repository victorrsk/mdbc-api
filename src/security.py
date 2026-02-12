from pwdlib import PasswordHash

pwd_context = PasswordHash.recommended()


# return the user hasdhed pwd
def get_pwd_hash(pwd: str):
    hashed_pwd = pwd_context.hash(pwd)

    return hashed_pwd
