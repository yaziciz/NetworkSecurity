import sys

class NetworkSecurityException(Exception):
    def __init__(self, message: str, error_detail: sys):
        super().__init__(message)
        self.error_detail = error_detail

    def __str__(self):
        return f"NetworkSecurityException: {self.args[0]} | Error Detail: {self.error_detail}"
    
if __name__ == "__main__":
    try:
        a = 1 / 0
    except Exception as e:
        raise NetworkSecurityException("An error occurred in the NetworkSecurity module.", sys) from e