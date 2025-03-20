from typing import Union, List, Dict


def replace_value_in_dict(item: Union[List, Dict], original_schema):  # type: ignore
    if isinstance(item, list):
        return [replace_value_in_dict(i, original_schema) for i in item]
    elif isinstance(item, dict):
        if list(item.keys()) == ['$ref']:
            definitions = item['$ref'][2:].split('/')
            res = original_schema.copy()
            for definition in definitions:
                if 'enum' in res[definition]:
                    res[definition]['type'] = 'string'
                res = res[definition]
            return res
        else:
            return {key: replace_value_in_dict(i, original_schema) for key, i in item.items()}
    return item  # type: ignore
