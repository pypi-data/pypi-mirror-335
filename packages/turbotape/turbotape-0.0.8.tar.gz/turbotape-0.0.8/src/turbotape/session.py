import os
import logging
from requests import Session
from pathlib import Path
from typing import Union

log = logging.getLogger(__file__)


def make_tape_client(token: str, check=True, robust: bool=True) -> Session:
    if token is None or token == "":
        raise Exception("Tape API key not given or key is empty.")
    session = Session()
    session.headers.update({
        'authorization': f'Bearer {token}',
    })
    return session


def try_environment_token():
    """
    Try to get the token from the environment variable TAPE_API_KEY.
    :return:
    """
    try:
        access_token = os.environ['TAPE_API_KEY']
    except KeyError as e:
        log.info('Environment variable TAPE_API_KEY is not set.')
        return None
    log.info('Loading OAuth2 token from environment.')
    return str(access_token)


def load_token(creds_file: Union[Path, str]) -> str:
    """
    Load the token from the file name tape_credentials.txt (unless specified otherwise)
    """
    token = ""
    with open(creds_file, mode="r", encoding='utf-8') as fh:
        token = fh.readline()
    return token.strip()


def create_tape_session(credentials_file=None, credentials=None, check=True, robust=False):
    token = None
    if credentials is not None:
        token = credentials
    else:
        token = try_environment_token()
    if token is None:
        log.info('Loading Tape API key from credentials file.')
        if credentials_file is None:
            token = load_token('tape_credentials.txt')
        else:
            token = load_token(credentials_file)
    tape = make_tape_client(token, check=check, robust=robust)
    return tape
