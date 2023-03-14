import sys, os
sys.path.append('src')
from models.game import Game

def main():
  old = 'test_save copy.xml'
  new = 'test_save copy1.xml'

  print(f'cwd: {os.path.abspath(os.curdir)}')
  assert os.path.isfile(new) == False

  game = Game(old)
  game.save(new)

  assert os.path.isfile(new) == True
  print(f'old file size: {os.path.getsize(old)}')
  print(f'new file size: {os.path.getsize(new)}')

  print('all done. cleaning up')
  os.remove(new)
  assert os.path.isfile(new) == False

if __name__ == '__main__':
  main()