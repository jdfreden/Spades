import multiprocessing as mp
import time
from Types.types import *
from Game import *
import itertools

def f(rootstate, itermax, verbose=0):
    """ Conduct an ISMCTS search for itermax iterations starting from rootstate.
        Return the best move from the rootstate.
    """

    rootnode = Node()

    for i in range(itermax):
        node = rootnode

        # Determinize
        state = rootstate.CloneAndRandomize(rootstate.playerToMove)

        # Select
        while state.GetMoves() != [] and node.GetUntriedMoves(
                state.GetMoves()) == []:  # node is fully expanded and non-terminal
            # scale the exploration value as the game goes on.
            node = node.UCBSelectChild(state.GetMoves())
            state.DoMove(node.move)

        # Expand
        untriedMoves = node.GetUntriedMoves(state.GetMoves())
        if untriedMoves:  # if we can expand (i.e. state/node is non-terminal)
            m = random.choice(untriedMoves)
            player = state.playerToMove
            state.DoMove(m)

            node = node.AddChild(m, player)  # add child and descend tree

        # Simulate
        while state.GetMoves():  # while state is non-terminal

            # When the last card of the hand is going to be played break from the rollout
            if len(state.playerHands[Player.north]) + len(state.playerHands[Player.east]) + len(
                    state.playerHands[Player.south]) + len(state.playerHands[Player.west]) == 1:
                state.DoMove(random.choice(state.GetMoves()))
                break
            state.DoMove(random.choice(state.GetMoves()))

        # Backpropagate
        while node is not None:  # backpropagate from the expanded node and work back to the root node
            node.Update(state)
            node = node.parentNode

    # Output some information about the tree - can be omitted
    if verbose == 2:
        print(rootnode.TreeToString(0))
    elif verbose == 1:
        print(rootnode.ChildrenToString())

    ret_stats = {}
    for cn in rootnode.childNodes:
        ret_stats[cn.move] = cn.visits
    # return max(rootnode.childNodes, key=lambda c: c.visits).move  # return the move that was most visited
    # return stats from the moves from depth 1 (really only need visits)
    return ret_stats


def main():
    N = 10000
    nworkers = 10

    starttime = time.time()
    poolnum = []
    n = int(N / nworkers)
    for i in range(nworkers):
        poolnum.append(n)
    random.seed(123)
    ss = SpadesGameState(Player.north)
    # for i in range(3):
    #     m = ISMCTS(ss, N, verbose = 1)
    #     ss.DoMove(m)
    arglist = list(zip(itertools.repeat(deepcopy(ss)), poolnum, [1] * len(poolnum)))
    pool = mp.Pool(nworkers)

    a = pool.starmap(f, arglist)
    pool.close()
    move_count = {}
    for i in range(0, len(a)):
        for k in a[i].keys():
            try:
                move_count[k] += a[i][k]
            except KeyError:
                move_count[k] = a[i][k]

    ma = max(move_count, key = move_count.get)
    print(ma, move_count[ma])


    print('Time taken = {} seconds'.format(time.time() - starttime))
    print(a)

    # Time the original
    random.seed(123)
    ss = SpadesGameState(Player.north)

    # for i in range(3):
    #     m = ISMCTS(ss, N, verbose = 1)
    #     ss.DoMove(m)

    starttime = time.time()
    print(ISMCTS(ss, N, verbose=1))
    print('Time taken = {} seconds'.format(time.time() - starttime))



if __name__ == '__main__':
    main()
