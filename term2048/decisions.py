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
    #print b.getCell(0,0)
    for test in ['up','left','right','down']:
        print test
	board = deepcopy(b)
	score = board.move(getattr(Board,test.upper()),add_tile=False)
	if board.moved:
          heuristics = [board.getCell(0,0)]
          for cell in [[x,0] for x in range(board.SIZE-1)]:
            #print cell
            heuristics.append(zig_zag_potential(board,cell,vertical=False))
	  heuristics.append(collapsed_line(board.getLine(0)) - collapsed_line(b.getLine(0)))
          sum_container = []
          for cell in [[board.SIZE-1-x,0] for x in range(3)]:
            #print ' ====== '
            heuristics.append(zig_zag_potential(board,cell,vertical=True))
 	    heuristics.append(combining_advantage(board.getCol(board.SIZE-1-x)))
            heuristics.append(collapsed_line(board.getCol(board.SIZE-1-x)) - collapsed_line(b.getCol(board.SIZE-1-x)))

            #print ' ..... '
          #heuristics.append(score)
          #sum_container.sort()
          #sum_container.reverse()
          #heuristics.extend(sum_container)
          heuristics.extend(aggregate_advantage(board))
    
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
  score = len(line)**2
  result = 0
  if flip:
    line.reverse()

  #first, check for zeros
  for i in range(len(line)):
    if line[i] == 0:
      result -= score
    score = score/2

  
  #then, check for descendingness.
  #compare to ordered list

  score = len(line)**2 
  test = line[:]
  test.sort()
  test.reverse()
  for i in range(len(line)):
    if line[i] == test[i]:
      result += line[i]*score 
    score = score/2   
  return result


def zig_zag_potential(board,cell,vertical=False):
    '''the value at offset in the second line should be equal to or lower than 
    the value above it in the top line'''
    x,y = cell
    upper = board.getCell(x,y)
    if vertical:
      cell2 = x,y+1
      lower = board.getCell(x,y+1)
    else:     
      cell2 = x+1,y
      lower = board.getCell(x+1,y)
    #print cell,upper,cell2,lower
    difference = upper-lower
    if difference == 0:
      return 16*upper
    elif upper == lower*2:
      return 2*upper
    elif upper > lower:
      return upper+lower
    else: 
      return difference #is negative

def collapsed_line(line,flip=False):
  line = line[:]
  if flip:
    line.reverse()
  score = 0
  line.reverse()
  for x in line:
    if x == 0:
      score += 1
    else:
      break
  return score*sum(line)  #don't value zeros over loosing tiles
