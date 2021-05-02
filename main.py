import time

from Game import *
import csv


def main(save_scores=False):
    ss = SpadesGameState(Player.north)
    score_track = []
    while ss.GetMoves():
        print(ss)
        if save_scores:
            if len(ss.playerHands[Player.north]) == 13 and len(ss.playerHands[Player.east]) == 13 and len(
                    ss.playerHands[Player.south]) == 13 and len(ss.playerHands[Player.west]) == 13:
                score_track.append([ss.NSscore[0], ss.NSscore[1], ss.EWscore[0], ss.EWscore[1],
                                    ss.bets[Player.north], ss.bets[Player.east], ss.bets[Player.south],
                                    ss.bets[Player.west]])

        if ss.playerToMove == Player.north:
            #st = time.time()
            #m = ParaISMCTS_driver(rootstate=ss, total_iter=5000, verbose=0, numWorkers=5)

            m = ISMCTS(rootstate=ss, itermax=1000, verbose=2)
            #print('Time taken = {} seconds'.format(time.time() - st))

        else:
            m = ISMCTS(rootstate=ss, itermax=5, verbose=0)

        print("Best Move: " + str(m) + "\n")
        ss.DoMove(m)

    score_track.append([ss.NSscore[0], ss.NSscore[1], ss.EWscore[0], ss.EWscore[1],
                        ss.bets[Player.north], ss.bets[Player.east], ss.bets[Player.south], ss.bets[Player.west]])
    if save_scores:
        with open('scores/score.csv', mode='w', newline='') as f:
            score_writer = csv.writer(f, delimiter=',')
            for line in score_track:
                score_writer.writerow(line)
    print(str(ss.NSscore) + str(ss.EWscore))


def main2(ngames):
    score_track = {"NS": 0, "EW": 0}
    for i in range(ngames):
        ss = SpadesGameState(Player.north)
        ss.SCORE_LIMIT = 400
        ss.EXPLORATION = .5
        while ss.GetMoves():
            # print(ss)
            if ss.playerToMove == Player.north or ss.playerToMove == Player.south:
                m = ISMCTS(rootstate=ss, itermax=1000, verbose=2)
            else:
                #m = ISMCTS(rootstate=ss, itermax=5, verbose=0)
                m = random.choice(ss.GetMoves())

            # print("Best Move: " + str(m) + "\n")
            ss.DoMove(m)
        if ss.NSscore[0] > ss.EWscore[0]:
            score_track["NS"] += 1
        else:
            score_track["EW"] += 1
        print(str(ss.NSscore) + str(ss.EWscore))
        print(score_track)

    print(score_track)



if __name__ == "__main__":
    #random.seed(123)
    main(save_scores=False)
    #main2(ngames = 50)
