class Response:
    def __init__(self):
        self.success = False
        self.message = None
        self.errors = None

    # Setters
    def set_message(self, message: str):
        self.message = message

    def set_success_status(self, status: bool):
        self.success = status

    def set_errors(self, errors):
        self.errors = errors

    # Getters
    def get_message(self) -> bool:
        return self.message

    def get_success_status(self) -> bool:
        return self.success

    def get_errors(self):
        return self.errors
