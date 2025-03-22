import cython

__test__: dict
extension_suffix: str
keyfile: str

def main() -> cython.bint:
    """main() -> cython.bint
    Used to verify the activation state of the product

        :return: Whether the product is verified with the server, True verified, False not verified.
    """
