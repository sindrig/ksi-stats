def print_info(players, get_value):
    max_name_length = max(
        len(player_name) for (player_id, player_name), attributes in players
    )
    for (player_id, player_name), attributes in players:
        value = get_value([None, attributes])
        print('%s: %s' % (player_name.ljust(max_name_length), value))


def extract_data(sorted_list, num, get_value):
    while (
        len(sorted_list) < num and
        get_value(sorted_list[num - 1]) == get_value(sorted_list[num])
    ):
        num += 1
    return sorted_list[:num]


def generic(attribute, players, num):
    items = list(players.items())

    def get_value(x):
        return x[1][attribute]
    sorted_list = sorted(
        items, key=get_value, reverse=True
    )
    print_info(extract_data(sorted_list, num, get_value), get_value)


def ratio(value, by, players, num):
    items = list(players.items())

    def get_value(x):
        if x[1][by] == 0:
            return 0
        return x[1][value] / x[1][by]
    sorted_list = sorted(
        items, key=get_value, reverse=True
    )
    print_info(extract_data(sorted_list, num, get_value), get_value)


def console(players, empty_container):
    examples = empty_container.keys()
    while True:
        ans = input(
            'What the fuck do you want (examples: %s)? ' % (examples)
        ).split()
        func = ans[0]
        num = int(ans[1]) if len(ans) > 1 else 10
        if func == 'q':
            return
        if func in empty_container:
            generic(func, players, num)
        elif '/' in func:
            value, by = func.split('/')
            ratio(value, by, players, num)
        else:
            print('I have no idea what the fuck %s is' % func)
