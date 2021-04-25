# Spades


I am eyeing a redesign/rebuild of this project

I would keep Node and ISMCTS the same from here: https://gist.github.com/kjlubick/8ea239ede6a026a61f4d
I want to more thoroughly design the SpadesGameState. Initially, I was eager to try and make it work. I would like to carefully test this class.

# Resources
- Information Set Monte Carlo Tree Search: https://pure.york.ac.uk/portal/files/13014166/CowlingPowleyWhitehouse2012.pdf
- ICARUS: https://www.sciencedirect.com/science/article/pii/S0004370214001052#!

# Things to include:
- Bidding Algorithm from: https://arxiv.org/pdf/1912.11323.pdf
- Scoring criterion for backpropagation from here: https://www.aaai.org/ocs/index.php/AIIDE/AIIDE13/paper/view/7369/7595
- Opponent Hand Inference from here: http://www.aifactory.co.uk/newsletter/2018_02_opponent_hand.htm
- (WISH) Write interactive visualization from tree data structure in R using vis-network
- Overall improve computational performance and remove clutter state from the SpadesGameState class


# Thoughts
- Should the exploration paramter change as the game gets closer to the end to encourage exploitation?
- I wonder if cython could give me any performance increase?  
    -I am going to give it a shot because I find cython interesting
  
- I think I have implemented a root parallelization of the ISMCTS.  
    - It only becomes faster when the number of iterations is greater than 1900 in its current state.
    - I wonder if there is a better way. I am not that good with the multiprocessing module in python.