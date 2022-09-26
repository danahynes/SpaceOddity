
'''
merge: all keys in src that are not in dst, add to dst

prune: all keys in dst that are not in src, remove from dst

this works for simple add/remove, but not change
how would we know what old(dst) key was changed to new(src) key?
we need to know that to copy over old val for old key to old val for new key

eg

old:
{
    'options':
    {
        'enabled': 1,
        'show_caption': 1
    }
}

new:
{
    'general':
    {
        'enabled': 1
    },
    'caption':
    {
        'enabled': 1
    }
}

maybe a map?

eg:
{
    {
        'options': 'enabled'
        'general': 'enabled'
    },
    {
        'options': 'enabled'
        'caption': 'enabled'
    }
}

map here, merge/purge in dict_funcs

different levels
eg

old:
{
    'options':
    {
        'foo':{
            'enabled': 1,
            'show_caption': 1
        }
    }
}

new:
{
    'general':
    {
        'enabled': 1
    },
    'caption':
    {
        'enabled': 1
    }
}

map:
{
    {
        'options/foo': 'enabled'
        'general': 'enabled'
    },
    {
        'options/foo': 'enabled'
        'caption': 'enabled'
    }
}

---------------------------------------

or!

{
    'sect1/sect2/key' : ' sect1/key',
    'sect1/key' : 'sect1/sect2/key',
    'sect1/key/sect2/key': sect1/key/sect2/key
}

map old sect(s)/keys to new sect(s)/keys

'''


def merge(dict_src, dict_dst):

    # TODO make recursive

    print('merge')

    # iterate over src, adding any missing keys to dst
    for key in dict_src:

        if key not in dict_dst.keys():
            dict_dst[key] = dict_src[key]

            merge(dict_src[key], dict_dst[key])

    return dict_dst


def purge(dict_src, dict_dst):

    # TODO make recursive

    print('purge')

    dict_src_copy = dict_src.copy()

    for key in dict_src.keys():

        if key not in dict_dst.keys():

            purge(dict_src[key], dict_dst[key])

            del dict_src_copy[key]

    return dict_src_copy


def convert():
    pass

    # print('merge')

    # # iterate over src, adding any missing keys to dst
    # for key in dict_src:

    #     print('first key:', key)

    #     next_dict = dict_src[key]
    #     for key in next_dict:
    #         print('next key:', key)

    #         merge()

    #     # print(next_dict)

    #     # if key not in dict_dst.keys():
    #     #     dict_dst[key] = dict_src[key]

    #     #     print('added key', key, 'to dst')

    #     # for key in next_dict:
    #     #     print(key)

    # # return dict_dst
