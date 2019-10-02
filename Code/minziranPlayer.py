import sys

# CS440 P3
# Ziran Min
# U59274427
# minziran@bu.edu
# 04/25/2018

# print to stderr for debugging purposes
# remove all debugging statements before submitting your code
msg = "Given board " + sys.argv[1] + "\n";
sys.stderr.write(msg);


#parse the input string, i.e., argv[1]
##############################################################
# Converting game board to a 2-d list
##############################################################
s = sys.argv[1]
(Board, lastPlay) = s.split("LastPlay:")

# Convert lastPlay to list type, like [c, x, y, z]
if lastPlay == "null":
    lastPlay = ['null']
else:
    lastPlay = lastPlay[1:]
    lastPlay = lastPlay[:-1]
    lastPlay = lastPlay.split(",")
    lastPlay = [int(i) for i in lastPlay]

board = []  
row = []
for i in Board:
    # '[' determine the start of a row
    if i  == '[':
        row = []
    # ']' determine the end of a row
    elif i == ']':
        board.append(row)
    else:
        row.append(int(i))
# vertically reverse the board for easily locate each circle
board.reverse()


##############################################################

# initialize the size of board
size = len(board)-2 

# initialize the look ahead depth
# we can change it to any values, but the larger it is, the longer it takes to process
Depth = 5

# initialize the value of alpha (negative infinity) and beta (positive infinity)
PositiveInfinity = float("inf")
NegativeInfinity = float("-inf")
##############################################################



#perform intelligent search to determine the next move
##############################################################
# Buidling helper functions
##############################################################

# finding all adjacent circles next to the previous move
def AllNeighbors(board, lastPlay):
    allneighbor = []
    x = lastPlay[1]
    y = lastPlay[2]

    # these neighors are listed in counterclockwise in the original board
    if x > 1:
        allneighbor = [(x+1, y -1), (x+1, y), (x, y+1), (x-1, y+1), (x-1, y), (x, y-1)]
    else:
        allneighbor = [(x+1, y -1), (x+1, y), (x, y+1), (x-1, y), (x-1, y-1), (x, y-1)]

    return allneighbor



# finding all uncolored adjacent circles (potential next moves for the opponent) next to the previous move
def UncoloredNeighbors(board, lastPlay):
    allneighbor = AllNeighbors(board, lastPlay)
    uncolored = []
    for (x, y) in allneighbor:
        if board[x][y] == 0:
            uncolored.append((x, y))
    return uncolored


# finding all colored adjacent circles next to the previous move
def ColoredNeighbors(board, lastPlay):
    allneighbor = AllNeighbors(board, lastPlay)
    colored = []
    for (x, y) in allneighbor:
        if board[x][y] != 0:
            colored.append((x, y))
    return colored


# testing whether a move will cause player to lose
def Lose(board, move):
    # if this is the first move, we won't lose 
    if move[0] == "null":
        return False

    # move's color, first color
    color = move[0]
    neighbors = AllNeighbors(board, move)

    # go through each triangle to see whether it has three different colors
    for ind, (x, y) in enumerate(neighbors):  
        colors = [color]

        # check the second color
        if board[x][y] != 0:
            colors.append(board[x][y])
            
        # check the third color of the next neighbor circle 
        (x2, y2) = neighbors[(ind+1) % len(neighbors)]
        if board[x2][y2] != 0:
            colors.append(board[x2][y2])  
        if len(set(colors)) == 3:
            return True
        
    return False


# finding all uncolored circles on the board
def AllUncoloered(board):  
    alluncolored = []
    for x, row in enumerate(board):
        for y, circle in enumerate(row):
            if circle == 0:
                alluncolored.append((x, y))
    return alluncolored


# finding all available moves for the next player
def AvailableMoves(board, lastPlay):
    uncolored = UncoloredNeighbors(board, lastPlay)
    if uncolored != []:
        return uncolored
    else:
        other = AllUncoloered(board)
        return other


# for a specific circle, finding its all uncolored neighbors,
# those neighbors' uncolored neighbors, and so on,
# until we finding a biggest uncolored area that contains the
# specific input circle and this area is bounded by all colored circles. 
def BoundedUncolored(board, cirle, visited):
    # visited is the set of visited node, it is useful in recursion
    uncoloredneighbors = UncoloredNeighbors(board, cirle)

    # set of circles that are unvisited
    unvisited = set(uncoloredneighbors) - visited

    # current input circle
    current = set([(cirle[1], cirle[2])])

    # create new visited list for recursion 
    visitedList = visited | unvisited | current  

    # find the ideal connected uncolored set of circles
    for (x, y) in unvisited:  
        newList = BoundedUncolored(board, [0, x, y, size + 2 - x - y], visitedList)
        visitedList = visitedList | newList  

    return visitedList


########################################################################
# evaluator using trap forcing and less different color around own move 
########################################################################

def Evaluator(board, lastPlay, isMax):
    # input isMax is a boolean variable to determine whehter to find highest score of lowest score
    # initialize the final score of a move is 0
    FinalScore = 0

    # if this move causes to lose, it has the worst score
    if Lose(board, lastPlay):  
        if isMax:
            return (PositiveInfinity, lastPlay)
        else:
            return (NegativeInfinity, lastPlay)

    # if a move could create potential trap and force the opponent to fall into it, it has a high score
    TrapPoints = 0
    uncoloredneighbors = UncoloredNeighbors(board, lastPlay)
    BoundArea = set()
    OddBoundCircle = 0
    EvenBoundCircle = 0
    for (x, y) in uncoloredneighbors:
        if (x, y) not in BoundArea:  
            NewBound = BoundedUncolored(board, [0, x, y, size + 2 - x - y], set())
            BoundArea = BoundArea | NewBound
            if len(NewBound) % 2 == 0:
                EvenBoundCircle += 1
            else:
                OddBoundCircle += 1
    TrapPoints += (OddBoundCircle - EvenBoundCircle)

    # add more points if the opponent will be forced to color the last circle in a bounded area
    # counting total numbers of uncolored circles (included thr current one) in the bounded area
    board[lastPlay[1]][lastPlay[2]] = 0
    Bounded = BoundedUncolored(board, lastPlay, set())
    board[lastPlay[1]][lastPlay[2]] = lastPlay[0]
    # if the opponent colors the last circle in a bounded area
    if len(Bounded) % 2 == 0:  
        if isMax:
            TrapPoints += 1
        else:
            TrapPoints -= 1
            
    # to decrease my own probability of creating a three color triangle
    # I need to color the move by the most seen color of its neighbers
    ColorPoints = 0
    color = lastPlay[0]
    coloredneighbors = ColoredNeighbors(board, lastPlay)
    ColorScoreSet = [0, 0, 0, 0]
    for (x, y) in coloredneighbors:
        # to prevent the ColorPoints being too large, I scale it according to the TrapPoints
        if isMax:
            ColorScoreSet[board[x][y]] += (TrapPoints / 7)
        else:
            ColorScoreSet[board[x][y]] -= (TrapPoints / 7)

    ColorPoints = TrapPoints - ColorScoreSet[color]
    FinalScore = TrapPoints + ColorPoints
    
    return (FinalScore, lastPlay)


##############################################################
# the minimax searching algorithm with alpha-beta pruning
##############################################################
# this is mainly inspired by the pseudo code privided in lab

def Minimax(board, lastPlay, depth, alpha, beta, isMax):
    # input isMax is a boolean variable to determine whehter to find highest score of lowest score
    
    # if we start first, put node in the top of board
    # because here is more likely force opponent fall into a trap
    if lastPlay[0] == "null":
        return (0, [3, size, 1, 1])
    
    # base case
    if depth == 0 or Lose(board, lastPlay):
        return Evaluator(board, lastPlay, isMax)
    
    # the main alpha-beta pruning part
    else:
        children = AvailableMoves(board, lastPlay)
        # if it is the max level
        if isMax:
            score = (NegativeInfinity, [])
            # go through all possible move, find the highest score one
            for (x, y) in children:
                for color in range(1, 4):                           
                    board[x][y] = color
                    move = [color, x, y, size + 2 - x - y]
                    childScore = Minimax(board, move, depth - 1, alpha, beta, False)
                    board[x][y] = 0
                    if childScore[0] >= score[0]:
                        score = (childScore[0], move)
                    if score[0] > alpha:
                        alpha = score[0]
                    if beta <= alpha:
                        break
            return score
        
        # if it is the min level
        else:
            score = (PositiveInfinity, [])
            # go through all possible move, find the lowest score one
            for (x, y) in children:
                for color in range(1, 4):                           
                    board[x][y] = color
                    move = [color, x, y, size + 2 - x - y]
                    childScore = Minimax(board, move, depth - 1, alpha, beta, True)
                    board[x][y] = 0
                    if childScore[0] <= score[0]:
                        score = (childScore[0], move)
                    if score[0] < beta:
                        beta = score[0]
                    if beta <= alpha:
                        break
            return score



# find the best move by minimax function and convert the move to readable input
BestMove = Minimax(board, lastPlay, Depth, NegativeInfinity, PositiveInfinity, True)
StringMove = map(str, BestMove[1])
Move = ",".join(StringMove)
sys.stdout.write("(" + Move + ")");













