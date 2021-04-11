# Spades


I am eyeing a redesign/rebuild of this project

I would keep Node and ISMCTS the same from here: https://gist.github.com/kjlubick/8ea239ede6a026a61f4d
I want to more thoroughly design the SpadesGameState. Initially, I was eager to try and make it work. I would like to carefully test this class.

# Things to include:
- Bidding Algorithm from: https://arxiv.org/pdf/1912.11323.pdf
- Scoring criterion for backpropagation from here: https://www.aaai.org/ocs/index.php/AIIDE/AIIDE13/paper/view/7369/7595
- Opponent Hand Inference from here: http://www.aifactory.co.uk/newsletter/2018_02_opponent_hand.htm
- (WISH) Write interactive visualization from tree data structure in javascript using vis-network
- Overall improve computational performance and remove clutter state from the SpadesGameState class
