from Types.types import Player


def format_hand_for_write(state):
    s = state.GetResult2(Player.north)
    b = state.bets
    bets = {"North": b[Player.north], "East": b[Player.east], "South": b[Player.south], "West": b[Player.west]}
    out = {"Score": {"NS_score": s[0][0], "NS_bag": s[0][1], "EW_score": s[1][0], "EW_bag": s[1][1]},
           "Bets": bets}
    return out
