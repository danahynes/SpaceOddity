import dict_funcs as df

dict_old = {
    'options': {
        'enabled': '1',
        'show_caption': '1',
        'foo': {
            'bar': 1
        }
    }
}

dict_new = {
    'general': {
        'enabled': '1'
    },
    'caption': {
        'enabled': '1'
    }
}

# add all keys from dict_old that are not present in dict_new
alt_dict = df.merge(dict_old, dict_new)
print('alt:', alt_dict)

# purge all keys from alt_dict that are not present in dict_old
alt_dict_2 = df.purge(alt_dict, dict_old)
print('alt_2', alt_dict_2)
