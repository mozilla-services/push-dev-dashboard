from base64 import urlsafe_b64encode
import ecdsa

import fudge


MESSAGES_API_RESPONSE_JSON_MESSAGES = [
    {
        'id': 'ABCdef123456',
        'timestamp': '2016-02-24T17:24:45.737Z',
        'size': 321,
        'ttl': 86400
    },
    {
        'id': 'GHIjkl789101',
        'timestamp': '2016-02-24T17:24:45.314Z',
        'size': 0,
        'ttl': 0
    }
]

MESSAGES_API_POST_RESPONSE = fudge.Fake().has_attr(status_code=201)


def gen_keys():
    signing_key = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p)
    verifying_key = signing_key.get_verifying_key()
    vapid_key = urlsafe_b64encode(verifying_key.to_string())
    return (signing_key, verifying_key, vapid_key)
