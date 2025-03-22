import cython
from typing import Any

__test__: dict
extension_suffix: str
keyfile: str
license_file: str

def activation() -> Any:
    """activation()
    Used to activate the product

        :return: start UI to activate this product.
    """
def modify_proxy() -> Any:
    """modify_proxy()
    Used to modify the proxy setting of the product

        :return: None
    """
def verify_activation() -> cython.bint:
    """verify_activation() -> cython.bint
    Used to verify the activation state of the product

        :return: True if passed verification, False if not.
    """
