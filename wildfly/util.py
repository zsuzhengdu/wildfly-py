def is_success(response=None):
    if response is not None:
        return response.json()['outcome'] == 'success'
    return False


def get_list(result):
    pass
