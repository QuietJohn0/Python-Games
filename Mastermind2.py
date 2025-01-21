# Mastermind
#import numpy as np
import random
import signal 
import sys 
import time 
from functools import lru_cache


def signal_handler(sig, frame): 
    print('You pressed Ctrl+C!') 
    sys.exit(0) 


class Mastermind:
    inputError = 0

    def __init__(self, passcode, code_range, code_length):
        self.passcode = passcode 
        self.code_length = code_length
        self.guess_list = []
        self.guess_out_list = []
        self.code_range = code_range

    def __str__(self):
        out = '\n\n\n\n\n\n\n'
        out = out + 'Try to crack the code!\n'
        out = out + self.get_error()
        out = out + '_'*self.code_length + ' \t\t(0-' + str(self.code_range) + ')'
        for i in range(len(self.guess_list)):
            zeros = self.code_length - len(str(self.guess_list[i]))
            out = out + '\n' + '0'*zeros + str(self.guess_list[i]) + ' \t\t' + str(self.guess_out_list[i])
        return out
    
    def check_lock(self,key):
        return self.check_key(key,self.passcode,self.code_length)
    
    def is_valid_passcode(self,code):
        return Mastermind.is_valid_code(code, self.code_range, self.code_length)

    def save_key(self,key):
        self.guess_list.append(key)
        self.guess_out_list.append(self.check_lock(key))
    
    def cracked_passcode(self):
        if self.passcode == self.guess_list[-1]:
            return True
        return False
    
    @staticmethod
    def is_valid_code(code, code_range, code_length):
        if not isinstance(code, str):
            Mastermind.inputError = 1      
        elif not code.isdigit():
            Mastermind.inputError = 2     
        elif len(code) != code_length:
            Mastermind.inputError = 3
        else:     
            for i in code:
                if int(i) > code_range:
                    Mastermind.inputError = 4      
        return Mastermind.inputError == 0
    
    @staticmethod
    def is_valid_int(code):
        return Mastermind.is_valid_code(code, 9, 1)

    @staticmethod
    def get_error():
        error = ''
        if Mastermind.inputError == 1:
            error = 'NOT A STRING\n'
        elif Mastermind.inputError == 2:
            error = 'NO NONDIGITS\n'
        elif Mastermind.inputError == 3:
            error = 'WRONG LENGTH\n'
        elif Mastermind.inputError == 4:
            error = 'NOT IN RANGE\n'
        Mastermind.inputError = 0

        return error
    
    @staticmethod
    def generate_random_passcode(code_length, code_range):
        passcode = 0
        for i in range(code_length):
            passcode = passcode*10 + random.randint(0,code_range)

        return Mastermind(passcode,code_range, code_length)
    
    @staticmethod
    def select_passcode():
        valid_key = False

        while not valid_key:
            print(Mastermind.get_error() + 'Select passcode range (0-9)')
            code_range = input('')

            valid_key = Mastermind.is_valid_int(code_range)

        valid_key = False
        while not valid_key:
            print(Mastermind.get_error() + 'Select passcode:')
            code = input('')
            
            valid_key = Mastermind.is_valid_code(code, int(code_range), len(code))

        return Mastermind(int(code),int(code_range),len(code))
        
    
    @staticmethod
    def check_key(key,passcode,code_length):
        temp_key = [0,0,0,0,0,0,0,0,0,0]
        temp_pass = [0,0,0,0,0,0,0,0,0,0]
        score = [0, 0]
        for i in range(code_length):
            p = (passcode//(10**i))%10
            k = (key//(10**i))%10
            if p != k:
                temp_key[k] = temp_key[k] + 1
                temp_pass[p] = temp_pass[p] + 1
            else:
                score[0] = score[0] + 1
            
        for i in range(len(temp_key)):
            if temp_key[i] > 0:
                if temp_pass[i] <= temp_key[i]:
                    score[1] = score[1] + temp_pass[i]
                else:
                    score[1] = score[1] + temp_key[i]

        return score
    
class Player:
    def __init__(self, name):
        self.name = name
        print('New Player: ' + name)


    def get_key(self, game):
        raise NotImplementedError("Subclass must implement abstract method")

class Human(Player):
    def __init__(self):
        super().__init__('Human')

    def get_key(self, game):
        valid_key = False
        while not valid_key:
            key = input('')
            
            if game.is_valid_passcode(key):
                valid_key = True
            else:
                print(game)

        return int(key)
    


class Test(Player):
    def __init__(self,game):
        super().__init__('Test')
        self.game = game
        self.create_all_guess_list()

    def create_all_guess_list(self):
        self.all_guess_list = [guess for guess in Test.passcode_generator(self.game.code_range,self.game.code_length,self.game.code_length,0,[],[])]
        self.valid_guess_list = self.all_guess_list.copy()

    def get_key(self,game):
        guess_out_list = [self.game.check_lock(g) for g in self.game.guess_list]
        self.restrict_passcode(self.game.guess_list,guess_out_list)
        (key, key_out, sol_min) = self.find_best_guess()
        print(sol_min)
        return key



    def restrict_passcode(self,gs,gs_out):
        for i in range(len(gs)):
            for code in self.valid_guess_list.copy():
                if Mastermind.check_key(code,gs[i],self.game.code_length) != gs_out[i]:
                    self.valid_guess_list.remove(code)

                    

    @staticmethod
    def passcode_generator(code_range,code_length,length,code,gs,gs_out): 
        if length == 0:
            for i in range(len(gs)):
                if Mastermind.check_key(gs[i],code,code_length) != gs_out[i]:
                    return
            yield code
            return

        for num in range(code_range+1):
            yield from Test.passcode_generator(code_range, code_length, length-1, code*10 + num,gs,gs_out)

        return

    def find_prob(self,key,sol_min):
        score_list = []
        for passcode in self.valid_guess_list:
            score = Mastermind.check_key(key,passcode, self.game.code_length)
            if score in score_list:
                i = score_list.index(score)
                score_list[i+1] = score_list[i+1] + 1
                if sol_min < max(score_list[1::2]):
                    return score_list
            else:
                score_list.append(score)
                score_list.append(1)
        return score_list
    
    def find_best_guess(self):
        sol_min = 99999999
        best_guess = 0
        best_out = []
        for guess in self.all_guess_list:
            prob = self.find_prob(guess,sol_min)
            max_temp = max(prob[1::2])
            out_temp = prob[prob.index(max_temp)-1]
            if sol_min > max_temp or (sol_min == max_temp and (out_temp[0] > best_out[0] or (out_temp[0] == best_out[0] and out_temp[1] > best_out[1]))):
                sol_min = max_temp
                best_guess = guess
                best_out = out_temp
        return (best_guess, best_out, sol_min)

class John(Player):
    def __init__(self,game):
        super().__init__('Test')
        self.game = game
        self.guess_gen = self.passcode_generator(self.game.code_length,0)

    def get_key(self,game):
        return next(self.guess_gen)
    

    def restrict_passcode(self,gs,gs_out):
        for i in range(len(gs)):
            for code in self.valid_guess_list.copy():
                if Mastermind.check_key(code,gs[i],self.game.code_length) != gs_out[i]:
                    self.valid_guess_list.remove(code)

    
    def passcode_generator(self,length,code): 
        if length == 0:
            yield code
            return
            
        for num in range(self.game.code_range+1):
            if John.check_all_partial_keys(self.game,length-1, code*10 + num):
                yield from self.passcode_generator(length-1, code*10 + num)
        print(length)
        return

    @staticmethod
    def check_all_partial_keys(game,length,code):
        for i in range(len(game.guess_list)):
            if John.check_partial_key(game.guess_list[i],code,game.code_length,length,game.guess_out_list[i]):
                    return False
        return True

    @staticmethod
    def check_partial_key(key,passcode,code_length,length,guess_out):
        temp_key = [0,0,0,0,0,0,0,0,0,0]
        temp_pass = [0,0,0,0,0,0,0,0,0,0]
        score = [0, 0]

        for i in range(length):
            k = (key//(10**i))%10
            temp_key[k] = temp_key[k] + 1

        key = key//(10**length)
        for i in range(code_length - length):
            p = (passcode//(10**i))%10
            k = (key//(10**i))%10
            if p != k:
                temp_key[k] = temp_key[k] + 1
                temp_pass[p] = temp_pass[p] + 1
            else:
                score[0] = score[0] + 1
            
        for i in range(len(temp_key)):
            if temp_key[i] > 0:
                if temp_pass[i] <= temp_key[i]:
                    score[1] = score[1] + temp_pass[i]
                else:
                    score[1] = score[1] + temp_key[i]

        if score[0] > guess_out[0] or score[1] >  guess_out[1] or (guess_out[0] + guess_out[1] - score[1] - score[0]) > length:
            return True
            
        return False


def play(game, player):
    is_unsolved = True
    
    while is_unsolved:
        
        game.save_key(player.get_key(game))
        print(game)
        time.sleep(.5)
        
        if game.cracked_passcode():
            guess_num = len(game.guess_list)
            print('Guessed in ' + str(guess_num) + '!')
            return guess_num

    

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    t = Mastermind.select_passcode()

    start_time = time.time()
    
    # t = Mastermind.generate_random_passcode(8,5)

    player = John(t)

    # player = Human()

    play(t, player)

    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print("Time taken:", elapsed_time, "seconds")

    

