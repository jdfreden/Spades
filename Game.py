# This is a very simple Python 2.7 implementation of the Information Set Monte Carlo Tree Search algorithm.
# The function ISMCTS(rootstate, itermax, verbose = False) is towards the bottom of the code.
# It aims to have the clearest and simplest possible code, and for the sake of clarity, the code
# is orders of magnitude less efficient than it could be made, particularly by using a
# state.GetRandomMove() or state.DoRandomRollout() function.
#
# An example GameState classes for Knockout Whist is included to give some idea of how you
# can write your own GameState to use ISMCTS in your hidden information game.
#
# Written by Peter Cowling, Edward Powley, Daniel Whitehouse (University of York, UK) September 2012 - August 2013.
#
# Licence is granted to freely use and distribute for any sensible/legal purpose so long as this comment
# remains in any distributed code.
#
# For more information about Monte Carlo Tree Search check out our web site at www.mcts.ai
# Also read the article accompanying this code at ***URL HERE***

# This is code copied from https://gist.github.com/kjlubick/8ea239ede6a026a61f4d
# This code is meant be be subclassed for the specific game
import itertools
import random
from math import sqrt, log
import multiprocessing as mp

from Types.types import *
from helper import *
from betting import *


# import copy


# TODO: implement opponent hand inference within SpadesGameState
# TODO: implement betting algo within SpadesGameState (New Class?)

# Numpy 3d arrays np.zeros((DEPTH, ROWS, COLS))

class GameState:
    """ A state of the game, i.e. the game board. These are the only functions which are
        absolutely necessary to implement ISMCTS in any imperfect information game,
        although they could be enhanced and made quicker, for example by using a
        GetRandomMove() function to generate a random move during rollout.
        By convention the players are numbered 1, 2, ..., self.numberOfPlayers.
    """

    def __init__(self):
        self.numberOfPlayers = 2
        self.playerToMove = 1

    def GetNextPlayer(self, p):
        """ Return the player to the left of the specified player
        """
        return (p % self.numberOfPlayers) + 1

    def Clone(self):
        """ Create a deep clone of this game state.
        """
        st = GameState()
        st.playerToMove = self.playerToMove
        return st

    def CloneAndRandomize(self, observer):
        """ Create a deep clone of this game state, randomizing any information not visible to the specified observer player.
        """
        return self.Clone()

    def DoMove(self, move):
        """ Update a state by carrying out the given move.
            Must update playerToMove.
        """
        self.playerToMove = self.GetNextPlayer(self.playerToMove)

    def GetMoves(self):
        """ Get all possible moves from this state.
        """
        raise NotImplementedError()

    def GetResult(self, player):
        """ Get the game result from the viewpoint of player.
        """
        raise NotImplementedError()

    def __repr__(self):
        """ Don't need this - but good style.
        """
        pass


def sortTrick(suit, trump):
    suit.sort(key=lambda x: x[1])
    trump.sort(key=lambda x: x[1])
    return suit + trump


class SpadesGameState(GameState):
    """
    A State of a Spades game. This class inherits the GameState class and is completely implemented by Jake.
    """

    def __init__(self, dealer):
        super().__init__()

        # This are constants that could become parameters for creating the SpadesGameState
        self.SCORE_LIMIT = 400
        self.BACKPROP_CONST = 130
        self.EXPLORATION = 0.7

        # Basic Game State
        self.numberOfPlayers = 4
        self.tricksInRound = 13
        self.NSscore = [0, 0]
        self.EWscore = [0, 0]
        self.trumpSuit = Suit.spade
        # self.ProbTable = ProbabiltyTable(4, 52, 4)

        # Hand State
        self.dealer = dealer
        self.playerToMove = self.GetNextPlayer(self.dealer)
        self.currentTrick = []
        self.trumpBroken = False
        self.bets = {p: 0 for p in Player}

        # Card Related Hand State
        self.playerHands = {p: [] for p in Player}
        self.tricksTaken = {p: 0 for p in Player}
        self.discards = []

        # This is needed to implement the score change criterion. This keeps the previous hand's score
        self.scoreChange = {"NS": [0, 0], "EW": [0, 0]}
        self.tricksTakenpast = {p: 0 for p in Player}

        # Deal the hand out
        self.Deal()

        # self.ProbTable.setup(self.playerHands)
        #
        # for p in Player:
        #     self.ProbTable.updateFromBets(self.playerHands, p)

    def Clone(self):
        st = SpadesGameState(self.dealer)
        st.playerToMove = self.playerToMove

        st.NSscore = deepcopy(self.NSscore)
        st.EWscore = deepcopy(self.EWscore)
        st.playerHands = deepcopy(self.playerHands)
        st.currentTrick = deepcopy(self.currentTrick)
        st.tricksTaken = deepcopy(self.tricksTaken)
        st.discards = deepcopy(self.discards)
        st.bets = deepcopy(self.bets)
        st.trumpBroken = self.trumpBroken
        st.scoreChange = deepcopy(self.scoreChange)
        st.tricksTakenpast = deepcopy(self.tricksTakenpast)
        # st.ProbTable = copy.deepcopy(self.ProbTable)

        return st

    def CloneAndRandomize(self, observer):
        st = self.Clone()

        seenCards = st.playerHands[observer] + [card for (player, card) in st.currentTrick]
        unseenCards = [card for card in st.GetCardDeck() if card not in seenCards]

        # TODO Adjust this to take into account the probability table
        random.shuffle(unseenCards)
        for p in Player:
            if p != observer:
                numCards = len(self.playerHands[p])
                st.playerHands[p] = unseenCards[:numCards]
                unseenCards = unseenCards[numCards:]

        return st

    def GetCardDeck(self):
        """Creates a full 52 Card deck
        :return: list of Cards
        """
        return [Card(suit, val) for suit in Suit for val in range(2, 14 + 1)]

    # I have no clue what is happening in the Short Side Suits with Uncounted Spades (4.1.4) section
    # I am taking a break from trying to include that part
    def Bet(self, player):
        bet = []
        spade_tricks = 0
        for suit in Suit:
            sub = list(filter(lambda x: x.suit == suit, self.playerHands[player]))
            if suit != Suit.spade:
                bet.extend(side_suit_high(TABLE_1_MOD, sub))
            else:
                spade_tricks = spade_betting(sub)
        bet = np.asarray(bet).sum()

        self.bets[player] = round(bet) + spade_tricks

    def Deal(self):
        """Deals cards to each player
        """
        # Reset Hand Related State
        self.discards = []
        self.currentTrick = []
        self.tricksTaken = {p: 0 for p in Player}
        self.bets = {p: -1 for p in Player}
        self.trumpBroken = False

        deck = self.GetCardDeck()
        random.shuffle(deck)
        for p in Player:
            self.playerHands[p] = deck[:self.tricksInRound]
            deck = deck[self.tricksInRound:]
            self.Bet(p)

    def GetNextPlayer(self, p):
        if p == Player.north:
            return Player.east
        elif p == Player.east:
            return Player.south
        elif p == Player.south:
            return Player.west
        else:
            return Player.north

    def GetMoves(self):
        # Cases to think about:
        #   - Leader when spades has not been broken
        #   - Leader when spades has been broken
        #   - Leader when spades has not been broken and only have spades to play
        #   - Follower that has to follow suit
        #   - Follower that is out of the follow suit

        hand = self.playerHands[self.playerToMove]

        # Leader
        if not self.currentTrick:
            if not self.trumpBroken:
                if self._allSpades():
                    return hand
                else:
                    return [c for c in hand if c.suit != Suit.spade]
            else:
                return hand

        # Follower
        else:
            (leader, leadCard) = self.currentTrick[0]
            cardsInSuit = [card for card in hand if card.suit == leadCard.suit]
            if cardsInSuit:
                return cardsInSuit
            else:
                return hand

    def _allSpades(self):
        for c in self.playerHands[self.playerToMove]:
            if c.suit != Suit.spade:
                return False
        return True

    def DoMove(self, move):
        # Play the card, keep track of who played it
        self.currentTrick.append((self.playerToMove, move))

        # Update the trumpBroken if necessary
        if move.suit == Suit.spade and not self.trumpBroken:
            self.trumpBroken = True

        # Remove Card from player's hand and tell next player it is their turn
        self.playerHands[self.playerToMove].remove(move)
        self.playerToMove = self.GetNextPlayer(self.playerToMove)

        # The current trick is done. See who wins and update
        if any(True for (player, card) in self.currentTrick if player == self.playerToMove):
            (leader, leadCard) = self.currentTrick[0]

            # split the cards that followed suit
            suitedPlays = [(player, card.val) for (player, card) in self.currentTrick if card.suit == leadCard.suit]

            # split the cards that were spades
            trumpPlays = [(player, card.val) for (player, card) in self.currentTrick if card.suit == self.trumpSuit]

            # order the cards by value and the suit: LeadSuit, TrumpSuit
            sortedPlays = sortTrick(suitedPlays, trumpPlays)

            trickWinner = sortedPlays[-1][0]

            self.tricksTaken[trickWinner] += 1
            self.discards += [card for (player, card) in self.currentTrick]
            self.currentTrick = []
            self.playerToMove = trickWinner

            # Is the hand over?
            if not self.playerHands[self.playerToMove]:
                self.tricksTakenpast = deepcopy(self.tricksTaken)
                # Calculate the points gained in the hand
                points, bags = self.scoreHand()
                self._updateScore(points, bags)

                # Is the game over?
                if self.NSscore[0] >= self.SCORE_LIMIT or self.EWscore[0] >= self.SCORE_LIMIT:
                    # End the game
                    self.tricksInRound = 0

                # Start a new hand
                self.Deal()

    def scoreHand(self):
        """Score the hand that just finished
        :return: Tuple of Dicts detailing points and bags for each player
        """
        # Cases to think about
        #   1. Player bets a non-zero and non-13 amount
        #   2. Player bets 0 (NIL)
        #   3. Player bets 13 (Shoot the moon)

        points = {p: 0 for p in Player}
        bags = {p: 0 for p in Player}

        for p in Player:
            if self.bets[p] == 0:
                if self.tricksTaken[p] == 0:
                    points[p] = 100
                else:
                    points[p] = -100
                    bags[p] = self.tricksTaken[p]
            elif self.bets[p] == 13:
                if self.tricksTaken[p] == 13:
                    points[p] = 260
                else:
                    points[p] = -130
            else:
                if self.tricksTaken[p] >= self.bets[p]:
                    bag = self.tricksTaken[p] - self.bets[p]
                    bags[p] = bag
                    points[p] = self.bets[p] * 10 + bag
                else:
                    points[p] = self.bets[p] * -10
        return points, bags

    def _updateScore(self, points, bags):
        self.scoreChange["NS"][0] = points[Player.north] + points[Player.south]
        self.scoreChange["NS"][1] = bags[Player.north] + bags[Player.south]
        self.scoreChange["EW"][0] = points[Player.east] + points[Player.west]
        self.scoreChange["EW"][1] = bags[Player.east] + bags[Player.west]

        self.NSscore[0] = self.NSscore[0] + points[Player.north] + points[Player.south]
        self.EWscore[0] = self.EWscore[0] + points[Player.east] + points[Player.west]
        self.NSscore[1] = self.NSscore[1] + bags[Player.north] + bags[Player.south]
        self.EWscore[1] = self.EWscore[1] + bags[Player.east] + bags[Player.west]

        if self.NSscore[1] >= 10:
            self.NSscore[0] -= 100
            self.NSscore[1] -= 10
        if self.EWscore[1] >= 10:
            self.EWscore[0] -= 100
            self.EWscore[1] -= 10

    def GetResult(self, player):
        """Implements the score difference value from "Integrating Monte Carlo Tree Search with Knowledge-Based Methods
to Create Engaging Play in a Commercial Mobile Game" by Whitehouse et. al
        :param player: Point of view from which to calc the difference
        :return: score difference. Typically [-0.5, 0.5]
        """

        NS = self.scoreChange["NS"][0]
        EW = self.scoreChange["EW"][0]
        NSb = self.scoreChange["NS"][1]
        EWb = self.scoreChange["EW"][1]

        if player == Player.north or player == Player.south:
            res = ((NS - 10 * NSb) - (EW - 10 * EWb)) / self.BACKPROP_CONST
        else:
            res = ((EW - 10 * EWb) - (NS - 10 * NSb)) / self.BACKPROP_CONST

        # could threshold the res to be [-0.5, 0.5]
        return res

    def retrieveScore(self, player):
        return {"NS": self.NSscore, "EW": self.EWscore}

    def sortHand(self, player):
        """Sorts hand by value in arbitrary suit order
            spade = 1
            club = 2
            heart = 3
            diamond = 4
        :param player: Player to sort hand
        :return: sort list of Cards
        """
        sp = [card for card in self.playerHands[player] if card.suit == Suit.spade]
        cl = [card for card in self.playerHands[player] if card.suit == Suit.club]
        he = [card for card in self.playerHands[player] if card.suit == Suit.heart]
        di = [card for card in self.playerHands[player] if card.suit == Suit.diamond]
        sp.sort(key=lambda x: x.val)
        cl.sort(key=lambda x: x.val)
        he.sort(key=lambda x: x.val)
        di.sort(key=lambda x: x.val)

        return sp + cl + he + di

    def __repr__(self):
        """ Return a human-readable representation of the state
        """
        result = "%s: " % self.playerToMove
        result += ",".join(str(card) for card in self.sortHand(self.playerToMove))
        result += " | Tricks: %i" % self.tricksTaken[self.playerToMove]
        result += " | Trump: %s" % self.trumpSuit
        result += " | Trick: ["
        result += ",".join(("%s:%s" % (player, card)) for (player, card) in self.currentTrick)
        result += "]"
        result += " | Score: " + str(self.retrieveScore(self.playerToMove)["NS"]) + " - " + str(
            self.retrieveScore(self.playerToMove)["EW"])
        return result


class Node:
    """
    A node in the game tree. Note wins is always from the viewpoint of playerJustMoved.
    This is to be subclassed and have SelectChild implemented
    """

    def __init__(self, move=None, parent=None, playerJustMoved=None):
        self.move = move  # the move that got us to this node - "None" for the root node
        self.parentNode = parent  # "None" for the root node
        self.childNodes = []
        self.wins = 0
        self.visits = 0
        self.avails = 1
        self.playerJustMoved = playerJustMoved  # the only part of the state that the Node needs later

    def GetUntriedMoves(self, legalMoves):
        """ Return the elements of legalMoves for which this node does not have children.
        """

        # Find all moves for which this node *does* have children
        triedMoves = [child.move for child in self.childNodes]

        # Return all moves that are legal but have not been tried yet
        return [move for move in legalMoves if move not in triedMoves]

    # 0.7
    def SelectChild(self, legalMoves, exploration=.7):
        raise NotImplementedError()

    def AddChild(self, m, p):
        raise NotImplementedError()

    def Update(self, terminalState):
        """ Update this node - increment the visit count by one, and increase the win count by the result of terminalState for self.playerJustMoved.
        """
        self.visits += 1
        if self.playerJustMoved is not None:
            # scores, bags = terminalState.score() # the state get dealt again before being able to score it so this doesnt work
            self.wins += terminalState.GetResult(self.playerJustMoved)

    def __repr__(self):
        return "[M:%s W/V/A: %4f/%4i/%4i]" % (self.move, self.wins, self.visits, self.avails)

    def TreeToString(self, indent):
        """ Represent the tree as a string, for debugging purposes.
        """
        s = self.IndentString(indent) + str(self)
        if self.parentNode is not None:
            s = s + " " + str(self.parentNode.move) + ":" + str(self.parentNode.wins)
        for c in self.childNodes:
            s += c.TreeToString(indent + 1)
        return s

    @staticmethod
    def IndentString(indent):
        s = "\n"
        for i in range(1, indent + 1):
            s += "| "
        return s

    def ChildrenToString(self):
        s = ""
        for c in self.childNodes:
            s += str(c) + "\n"
        return s




class UCBNode(Node):
    """
    A node in the game tree. Note wins is always from the viewpoint of playerJustMoved.
    This node implements the UCB method for selecting children
    """

    def __init__(self, move=None, parent=None, playerJustMoved=None):
        super().__init__(move, parent, playerJustMoved)

    def SelectChild(self, legalMoves, exploration=.7):
        """ Use the UCB1 formula to select a child node, filtered by the given list of legal moves.
            exploration is a constant balancing between exploitation and exploration, with default value 0.7 (approximately sqrt(2) / 2)
        """

        # Filter the list of children by the list of legal moves
        legalChildren = [child for child in self.childNodes if child.move in legalMoves]

        # Get the child with the highest UCB score
        s = max(legalChildren,
                key=lambda c: float(c.wins) / float(c.visits) + exploration * sqrt(log(c.avails) / float(c.visits)))

        # Update availability counts -- it is easier to do this now than during backpropagation
        for child in legalChildren:
            child.avails += 1

        # Return the child selected above
        return s

    def AddChild(self, m, p):
        """ Add a new child node for the move m.
            Return the added child node
        """
        n = UCBNode(move=m, parent=self, playerJustMoved=p)
        self.childNodes.append(n)
        return n


class UrgencyNode(Node):
    def __init__(self, move=None, parent=None, playerJustMoved=None):
        super().__init__(move, parent, playerJustMoved)

    def SelectChild(self, legalMoves, exploration=.7):
        d = 1

    def AddChild(self, m, p):
        """ Add a new child node for the move m.
            Return the added child node
        """
        n = UrgencyNode(move=m, parent=self, playerJustMoved=p)
        self.childNodes.append(n)
        return n


def ISMCTS(rootstate, itermax, verbose=0, child_select_mode=ChildSelectMode.UCB):
    """ Conduct an ISMCTS search for itermax iterations starting from rootstate.
        Return the best move from the rootstate.
    """

    if child_select_mode == ChildSelectMode.UCB:
        rootnode = UCBNode()
    elif child_select_mode == ChildSelectMode.Urgency:
        rootstate = UrgencyNode()
    else:
        raise Exception("Invalid mode")

    for i in range(itermax):
        node = rootnode

        # Determinize
        state = rootstate.CloneAndRandomize(rootstate.playerToMove)

        # Select
        # node is fully expanded and non-terminal
        while state.GetMoves() != [] and node.GetUntriedMoves(state.GetMoves()) == []:
            # scale the exploration value as the game goes on.
            node = node.SelectChild(state.GetMoves(), state.EXPLORATION)
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
        #print(rootnode.TreeToString(0))
        write_tree(rootnode)
    elif verbose == 1:
        print(rootnode.ChildrenToString())

    return max(rootnode.childNodes, key=lambda c: c.visits).move  # return the move that was most visited


def ParaISMCTS(rootstate, itermax, verbose=0):
    """ The code is mostly the same as the 'ISMCTS' function but returns the number of visits
        per root->child so they can be aggregated
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
    return ret_stats


def ParaISMCTS_driver(rootstate, total_iter, verbose=0, numWorkers=2):
    poolnum = []
    n = round(total_iter / numWorkers)
    for i in range(numWorkers):
        poolnum.append(n)

    arglist = list(zip(itertools.repeat(deepcopy(rootstate)), poolnum, [verbose] * len(poolnum)))
    pool = mp.Pool(numWorkers)

    a = pool.starmap(ParaISMCTS, arglist)
    pool.close()
    move_count = {}
    for i in range(0, len(a)):
        for k in a[i].keys():
            try:
                move_count[k] += a[i][k]
            except KeyError:
                move_count[k] = a[i][k]
    return max(move_count, key=move_count.get)
