from Types.types import Player


def format_hand_for_write(state):
    s = state.GetResult2(Player.north)
    b = state.bets
    bets = {"North": b[Player.north], "East": b[Player.east], "South": b[Player.south], "West": b[Player.west]}
    out = {"Score": {"NS_score": s[0][0], "NS_bag": s[0][1], "EW_score": s[1][0], "EW_bag": s[1][1]},
           "Bets": bets}
    return out


def clean_player(p):
    if p == Player.north:
        return "North"
    elif p == Player.east:
        return "East"
    elif p == Player.south:
        return "South"
    else:
        return "West"


######
# Implements a much faster version of 'deepcopy'
######

_dispatcher = {}


def _copy_list(l, dispatch):
    ret = l.copy()
    for idx, item in enumerate(ret):
        cp = dispatch.get(type(item))
        if cp is not None:
            ret[idx] = cp(item, dispatch)
    return ret


def _copy_dict(d, dispatch):
    ret = d.copy()
    for key, value in ret.items():
        cp = dispatch.get(type(value))
        if cp is not None:
            ret[key] = cp(value, dispatch)

    return ret


_dispatcher[list] = _copy_list
_dispatcher[dict] = _copy_dict


def deepcopy(sth):
    cp = _dispatcher.get(type(sth))
    if cp is None:
        return sth
    else:
        return cp(sth, _dispatcher)
