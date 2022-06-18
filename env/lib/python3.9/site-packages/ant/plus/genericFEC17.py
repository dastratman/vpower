class genericFEC17:

      def __init__(self):
          self.dataPageNumber = 0
          self.cycleLength = 0

      def p17(self, data):
          self.dataPageNumber = data[0]
          print(self.dataPageNumber)
          if(self.dataPageNumber == 17):
             self.cycleLength = data[3]
