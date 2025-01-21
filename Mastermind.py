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
    def __init__(self, password, code_range):
        self.password = password 
        self.code_length = len(password)
        self.guess_list = []
        self.code_range = code_range
        self.inputError = 0
        print(self)

    def __str__(self):
        out = '\n\n\n\n\n\n\n'
        out = out + 'Try to crack the code!\n'
        out = out + self.get_error()
        out = out + '_'*self.code_length + ' \t\t(0-' + str(self.code_range) + ')'
        for g in self.guess_list:
            out = out + '\n' + g + ' \t\t' + str(self.check_lock(g))
        return out
    
    def check_lock(self,key):
        return self.check_key(key,self.password)
    
    def is_valid_code(self, code):
        if not isinstance(code, str):
            self.inputError = 1
            return False        
        elif not code.isdigit():
            self.inputError = 2
            return False        
        elif len(code) != self.code_length:
            self.inputError = 3
            return False
        else:     
            for i in code:
                if int(i) > self.code_range:
                    self.inputError = 4
                    return False        
        return True
    
    @staticmethod
    def is_valid_code(code,code_range):
        if not isinstance(code, str) and not isinstance(code_range, str):
            return False        
        elif not code.isdigit() and not code_range.isdigit():
            return False        
        else:     
            for i in code:
                if int(i) > int(code_range):
                    return False        
        return True

    def get_error(self):
        error = ''
        if self.inputError == 1:
            error = 'NOT A STRING\n'
        elif self.inputError == 2:
            error = 'NO NONDIGITS\n'
        elif self.inputError == 3:
            error = 'WRONG LENGTH\t(' + str(self.code_length) + ': ' + '_'*self.code_length + ' )\n'
        elif self.inputError == 4:
            error = 'NOT IN RANGE (0, ' + str(self.code_range) + ')\n'
        self.inputError = 0

        return error
    
    def save_key(self,key):
        self.guess_list.append(key)
    
    def cracked_password(self):
        if self.password == self.guess_list[-1]:
            return True
        return False

    @staticmethod
    def generate_random_passcode(code_length, code_range):
        password = ''
        for i in range(code_length):
            password = password + str(random.randint(0,code_range))

        return Mastermind(password,code_range)
    
    @staticmethod
    def select_passcode(code_range):
        valid_key = False

        while not valid_key:
            print('Select passcode range, n (0-n)')
            code_range = input('')

            print('Select passcode:')
            passcode = input('')
            
            if Mastermind.is_valid_code(passcode,code_range):
                valid_key = True
            else:
                print('error')
        return Mastermind(passcode,int(code_range))
        
    
    @staticmethod
    def check_key(key,password):
        temp_key = ''
        temp_pass = ''
        score = [0, 0]
        for i in range(len(password)):
            if password[i] != key[i]:
                temp_key = temp_key + key[i]
                temp_pass = temp_pass + password[i]
            else:
                score[0] = score[0] + 1
            
        for i in range(10):
            stri = str(i)
            if stri in temp_pass:
                if temp_pass.count(stri) <= temp_key.count(stri):
                    score[1] = score[1] + temp_pass.count(stri)
                else:
                    score[1] = score[1] + temp_key.count(stri)

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
            
            if game.is_valid_code(key):
                valid_key = True
            else:
                print(game)

        return key
    
class Test(Player):
    def __init__(self):
        super().__init__('Test')
        self.guess_list = []
        self.guess_out_list = []

    def get_key(self, game):
        guess_out_list = [game.check_lock(g) for g in game.guess_list]
        (key, key_out, sol_min) = Test.find_best_guess(game.code_range,game.code_length,game.guess_list,guess_out_list)

        return key


    @staticmethod
    def password_generator(code_range,code_length,code,gs,gs_out): 
        if code_length == 0:
            for i in range(len(gs)):
                if Mastermind.check_key(gs[i],code) != gs_out[i]:
                    return
            yield code
            return

        for num in range(code_range+1):
            yield from Test.password_generator(code_range,code_length-1, code + str(num),gs,gs_out)

        return

    @staticmethod
    def find_prob(code_range,code_length,key,gs,gs_out):
        score_list = []
        for password in Test.password_generator(code_range,code_length,'',gs,gs_out):
            score = Mastermind.check_key(key,password)
            if score in score_list:
                i = score_list.index(score)
                score_list[i+1] = score_list[i+1] + 1
            else:
                score_list.append(score)
                score_list.append(1)
        return score_list
    
    @staticmethod
    def find_best_guess(code_range,code_length,gs,gs_out):
        sol_min = 99999999
        best_guess = ''
        best_out = []
        for guess in Test.password_generator(code_range,code_length,'',[],[]):
            prob = Test.find_prob(code_range,code_length,guess,gs,gs_out)
            max_temp = max(prob[1::2])
            out_temp = prob[prob.index(max_temp)-1]
            if sol_min > max_temp or (sol_min == max_temp and (out_temp[0] > best_out[0] or (out_temp[0] == best_out[0] and out_temp[1] > best_out[1]))):
                sol_min = max_temp
                best_guess = guess
                best_out = out_temp

        return (best_guess, best_out, sol_min)

class Test2(Player):
    def __init__(self,game):
        super().__init__('Test2')
        self.game = game
        self.create_all_guess_list()

    def create_all_guess_list(self):
        self.all_guess_list = [guess for guess in Test2.password_generator(self.game.code_range,self.game.code_length,'',[],[])]
        self.valid_guess_list = self.all_guess_list.copy()

    def get_key(self,game):
        guess_out_list = [self.game.check_lock(g) for g in self.game.guess_list]
        self.restrict_password(self.game.guess_list,guess_out_list)
        (key, key_out, sol_min) = self.find_best_guess()
        print(sol_min)
        return key



    def restrict_password(self,gs,gs_out):
        for code in self.valid_guess_list.copy():
            elim = True
            for i in range(len(gs)):
                if Mastermind.check_key(code,gs[i]) != gs_out[i] and elim:
                    self.valid_guess_list.remove(code)
                    elim = False

                    

    @staticmethod
    def password_generator(code_range,code_length,code,gs,gs_out): 
        if code_length == 0:
            for i in range(len(gs)):
                if Mastermind.check_key(gs[i],code) != gs_out[i]:
                    return
            yield code
            return

        for num in range(code_range+1):
            yield from Test2.password_generator(code_range,code_length-1, code + str(num),gs,gs_out)

        return

    def find_prob(self,key):
        score_list = []
        for password in self.valid_guess_list:
            score = Mastermind.check_key(key,password)
            if score in score_list:
                i = score_list.index(score)
                score_list[i+1] = score_list[i+1] + 1
            else:
                score_list.append(score)
                score_list.append(1)
        return score_list
    
    def find_best_guess(self):
        sol_min = 99999999
        best_guess = ''
        best_out = []
        best_prob = []
        for guess in self.all_guess_list:
            prob = self.find_prob(guess)
            max_temp = max(prob[1::2])
            out_temp = prob[prob.index(max_temp)-1]
            if sol_min > max_temp or (sol_min == max_temp and (out_temp[0] > best_out[0] or (out_temp[0] == best_out[0] and out_temp[1] > best_out[1]))):
                sol_min = max_temp
                best_guess = guess
                best_out = out_temp
                best_prob = prob
        return (best_guess, best_out, sol_min)

def play(game, player):
    is_unsolved = True
    
    while is_unsolved:
        
        game.save_key(player.get_key(game))
        print(game)
        time.sleep(.5)
        
        if game.cracked_password():
            guess_num = len(game.guess_list)
            print('Guessed in ' + str(guess_num) + '!')
            return guess_num

    

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    t = Mastermind.select_passcode(4)

    #t = Mastermind.generate_random_passcode(5,5)
    player = Test2(t)
    # player = BotPlayer()
    # t = Mastermind.generate_random_passcode(4,4)

    play(t, player)

    # print('new')
    # prob = Test.find_prob(5,5,'00123',[],[])
    # print(prob)
    # print(prob[1::2])
    # print(max(prob[1::2]))



    # #(best_guess, best_out, sol_min) = Test.find_best_guess(5,5,['00123','44012','33542','25515'],[[0,2],[1,1],[1,1],[4,0]])#21515
    # #(best_guess, best_out, sol_min) = Test.find_best_guess(5,5,['00123','14214','11535','34405','25504'],[[0,2],[1,1],[1,1],[1,2],[1,2]])#25504
    # (best_guess, best_out, sol_min) = Test.find_best_guess(4,4,['0011','0202','3000'],[[0,1],[1,0],[0,1]])
    # #00123
    # print(best_guess)
    # print(best_out)
    # print(sol_min)
    

