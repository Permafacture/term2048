from board import Board
from copy import deepcopy

'''improvements still to make:

'''


autoplay = True
autokey = [Board.UP]

#define some weights:
combining_weight = 2
smoothness_weight = 1

def projection(b):
    '''takes a Board and returns a dictionary of {'projection_name':reuslt}'''	
    global autokey
    result = []
    winner = {'down':[-100000,0,0]}
    
    top = b.getLine(0)
    print "top:        %s" % top
    print "right most: %s" % b.getCol(3)  
    for test in ['up','left','right','down']:
        #print test
	board = deepcopy(b)
	score = board.move(getattr(Board,test.upper()),add_tile=False)
	top_line_health = line_health(board.getLine(0))
        feeder1_health = line_health(board.getCol(board.SIZE-1))
        feeder2_health = line_health(board.getCol(board.SIZE-2))
        feeder_health = max([feeder1_health,feeder2_health])
	advantage = aggregate_advantage(board)
        second_line_health = line_health(board.getLine(1),flip=True)
	heuristics = [top_line_health,feeder_health,second_line_health,advantage[0],advantage[1]] 
	if board.moved:
	  result.append('%-6s: %s' %(test,heuristics))
	  winner = determine_winner(winner,{test: heuristics})
	else: result.append('%-6s: ---- Not Valid ---' % test)	#this move did not affect the board
    winner = winner.keys()[0]
    result.append('winner: %s\n' % winner)
    autokey.append(getattr(Board,winner.upper()))
    return winner, result

def determine_winner(dict1,dict2):
    '''take two dicts of {'projection_name': value_list}, where most important fac    tor is first and so on. returns winning dict'''
    l1 = dict1[dict1.keys()[0]]
    l2 = dict2[dict2.keys()[0]]
    for i in range(len(l1)):
	if l1[i] < l2[i]:
	    return dict2
	if l1[i] > l2[i]:
	    return dict1
	else:
	    pass
    return dict1    #total tie

def combining_advantage(line):
    '''takes a row or column and returns value of combining advantage'''
    result = 0
    skip = False
    line = line[:]
    #strip out white space
    while True:
	try:
	    line.remove(0)
	except ValueError:
	    break
    
    length = len(line) -1
    if length > 0:
        for i in range(len(line)-1):
	    if not skip:
	      if line[i] == line[i+1]:
		result += line[i]
		skip = True
	    else:
		skip = False
    return result

def aggregate_advantage(board):
    '''returns the maximum advantage of the vertical and horizontal advantages
    considering both combining and smoothness advantages'''

    vert_advantage = 0
    for x in [board.getLine(y) for y in range(board.SIZE)]:
        vert_advantage += combining_advantage(x)*combining_weight
        vert_advantage += smoothness_advantage(x)*smoothness_weight
    horiz_advantage = 0
    for x in [board.getCol(y) for y in range(board.SIZE)]:
        horiz_advantage += combining_advantage(x)*combining_weight
        horiz_advantage += smoothness_advantage(x)*smoothness_weight
    
    return [vert_advantage,horiz_advantage]

def smoothness_advantage(line):
    '''takes a row or column and returns value of smoothness advantage'''
    result = 0
    skip = False
    line = line[:]
    #strip out white space
    while True:
	try:
	    line.remove(0)
	except ValueError:
	    break
    
    length = len(line) -1
    if length > 0:
        for i in range(len(line)-1):
	    if not skip:
	      if line[i] == line[i+1]/2 or line[i] == line[i+1]*2:
		result += min([line[i],line[i+1]])
		skip = True
	    else:
		skip = False
    return result
	
def line_health(line,flip=False):
  '''assumes highest value is best at begining of line. flip=True if
  opposite is desired'''
  line = line[:]
  score = 64  #
  result = 0
  if flip:
    line.reverse() 
  
  biggest = max(line)

  #take the first value off
  this = line.pop()
  line.reverse()  #should be a way to do this without flipping the order...

  for i in range(len(line)):
    #first, check for zeros
    nxt = line[i]
    #print this, result
    if this == 0:
      result -= score
    else:
      if this == nxt:
        #combining advantage
        result += score*this*4
      elif this == nxt/2:
        #smoothness advantage
        result += score*this*2
      elif this < nxt:
        #atleast lined up properly
        result += score*this
      else:
        #line is not good
        #awfulness is propotional to importance of the spot and ratio of values
        try:
         result -= score*(this/nxt)
        except ZeroDivisionError:
         result -= score*biggest
    score /=4
    this = nxt
  print this
  return result


def zig_zag_potential(board,offset=0):
    '''the value at offset in the second line should be equal to or lower than 
    the value above it in the top line'''
    upper = board.getCell(board.SIZE-1-offset,0)
    lower = board.getCell(board.SIZE-1-offset,1)
    difference = upper-lower
    if difference < 0:
      #its bad if lower is greater than upper
      return difference
    else: 
      #We still want to prioritize small differences, but so long
      #as lower is lower than upper, its orders of magnitude better
      try: 
        return -difference/lower
      except ZeroDivisionError:
        return -difference + 1
