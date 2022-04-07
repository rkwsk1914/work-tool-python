import re

class Hearing:
    def doing(self, msg):
        hearing_msg = msg + ' : '
        answer = input(hearing_msg)
        return answer

    def validateInclude(self, msg, regExp):
        hearing_msg = msg + ' : '
        answer = input(hearing_msg)
        check_resExp = re.search(regExp, answer)

        check = False
        if not check_resExp is None:
            check = True

        if check == False:
            print('')
            print(f'The word "{regExp}" is not included. Please enter again.')
            answer = self.validateInclude(msg, regExp)
        return answer

    def validateFormat(self, msg, regExp, error_msg):
        hearing_msg = msg + ' : '
        answer = input(hearing_msg)

        pattern = re.compile(r'^' + regExp + r'$')
        check_resExp = pattern.match(answer)

        check = False
        if not check_resExp is None:
            check = True

        if check == False:
            print('')
            print(error_msg)
            answer = self.validateFormat(msg, regExp, error_msg)
        return answer

    def creatSelectionMsg(self, msg, selections):
        repeatMsg = msg + '[ '

        count = 1
        for select in selections:
            if count == 1:
                repeatMsg = repeatMsg + select
            else:
                repeatMsg = repeatMsg + ' / ' + select
            count += 1

        repeatMsg = repeatMsg + ' ] : '
        return repeatMsg

    def select(self, msg, selections, blank_ok=False):
        hearing_msg = self.creatSelectionMsg(msg, selections)
        answer = input(hearing_msg)

        if answer == '' and blank_ok == True:
            return answer

        check = False

        for select in selections:
            if select == answer:
                check = True

        if check == False:
            print('')
            print('Unknown choice. Please select again.')
            answer = self.select(msg, selections)

        return answer
