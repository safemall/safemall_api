import uuid


def generate_account(prefix='204'):
    acct_num = prefix + str(uuid.uuid4().int)[:10-len(prefix)]
    return acct_num