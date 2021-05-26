# Spades

## This is a work-in-progress 

### I am eyeing a redesign/rebuild of this project PART 2
- I want to create a class for the agent itself
- I want to design with parallelism in mind
- I want to think about a cython implementation
- Offer the Unexplored Action Urgency as an alternative to UCT

# Resources
- Information Set Monte Carlo Tree Search: https://pure.york.ac.uk/portal/files/13014166/CowlingPowleyWhitehouse2012.pdf
- ICARUS: https://www.sciencedirect.com/science/article/pii/S0004370214001052#!
    - MAST: seems interesting
    - More: http://davexi.co.uk/wp-content/uploads/2018/08/document.pdf, https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4561326/
- Opponent Modeling: https://webdocs.cs.ualberta.ca/~bowling/papers/06aaai-probmaxn.pdf

- Cython Agent Example: https://github.com/masouduut94/MCTS-agent-cythonized

# Things to include:
- Bidding Algorithm from: https://arxiv.org/pdf/1912.11323.pdf
- Scoring criterion for backpropagation from here: https://www.aaai.org/ocs/index.php/AIIDE/AIIDE13/paper/view/7369/7595
- Opponent Hand Inference from here: http://www.aifactory.co.uk/newsletter/2018_02_opponent_hand.htm
- (WISH) Write interactive visualization from tree data structure in R using vis-network
- Overall improve computational performance and remove clutter state from the SpadesGameState class


# Thoughts
- Should the exploration paramter change as the game gets closer to the end to encourage exploitation?
- I wonder if cython could give me any performance increase?  
    - I am going to give it a shot because I find cython interesting
  
- I think I have implemented a root parallelization of the ISMCTS.  
    - It only becomes faster when the number of iterations is greater than 1900 in its current state.
    - I wonder if there is a better way. I am not that good with the multiprocessing module in python.
