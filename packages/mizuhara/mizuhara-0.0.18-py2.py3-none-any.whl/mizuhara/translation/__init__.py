import importlib.resources
from yaml import safe_load
from os.path import exists


def translate(domain: str, key: str, language_code: str = "en") -> str:
    """
    this function is charge of translate string, which is defined on yaml file in the same path, into another language_code.
    if you need customize, please create another yaml file on translation folder,
    and use this function to translate.

    :param domain: name or alternate path of yaml file.
    :param key: name of main key in yaml file.
    :param language_code: language that you want to translate to.
    :return: str
    """

    # convert file name to file system format.
    file_name = f"{domain.replace("_", "/")}.yml"
    try:
        with importlib.resources.files("mizuhara.translation").joinpath(file_name).open("r", encoding="utf-8") as file:
            content = safe_load(file) or {}
            if content.get(key.lower(), None) is None:
                raise ModuleNotFoundError

    except (FileNotFoundError, ModuleNotFoundError):
        # Check if there's a user-defined translation file
        if exists(f"translation/{file_name}"):
            with open(f"translation/{file_name}", mode="r", encoding="utf-8") as file:
                content = safe_load(file) or {}

        # If no translation file exists, return the original key
        else:
            return key

    return content.get(key.lower(), {}).get(language_code, key)
