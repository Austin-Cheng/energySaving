

class BasicError(Exception):
    def __init__(self, status_code, error_message, error_details):
        super(BasicError, self).__init__(error_message)
        self.status_code = status_code
        self.error_message = error_message
        self.error_details = error_details

    def __str__(self):
        return f'{self.status_code}: {self.error_message}: {self.error_details}'
