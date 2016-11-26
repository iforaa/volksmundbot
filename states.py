import random
import redis
import hashlib

from random import randint

NAMES = "_names"
STATE = "_state"
QUESTION = "_question"
QUESTION_FOR_RATE = "_question_for_rate"
ANSWERS_FOR_RATE = "_answers_for_rate_2"
CURRENT_ANSWER = "_current_answer"
QUESTION_NUM = "_question_num"
ANSWERS = "_ANSWERS"
RATED_QUESTION = "_rated_question"

ANSW_OPTION_1 = "_answ_option_1"
ANSW_OPTION_2 = "_answ_option_2"
ANSW_OPTION_3 = "_answ_option_3"
ANSW_OPTION_4 = "_answ_option_4"

RATE = "_rate"


SOSS = "_soss"
ADVICES = "_advices"
SCHEDULE = "_schedule"

red = redis.StrictRedis(host='localhost', port=6379, db=1)


def is_user_new(chat_id):
    chat_id = str(chat_id)
    if red.get(chat_id + "_chat_id") is None:
        return True
    else:
        return False


def get_state(chat_id):
    chat_id = str(chat_id)
    return red.get(chat_id + STATE)


def set_state(chat_id, state):
    chat_id = str(chat_id)
    red.set(chat_id + STATE, state)


def set_question(chat_id, q_text):
    chat_id = str(chat_id)
    q_num = str(create_num_for_question())
    red.set(q_num + QUESTION, q_text)
    red.set(chat_id + QUESTION, q_num)


def get_random_question(chat_id):

    chat_id = str(chat_id)

    num_for_question = get_num_for_question(chat_id)
    if num_for_question is False:
        return False
    else:
        q_num = str(num_for_question)
        question = red.get(q_num + QUESTION)
        if question is None:
            return get_random_question(chat_id)

        red.set(chat_id + QUESTION_FOR_RATE, q_num)
        answers = red.lrange(q_num + ANSWERS, 0, -1)
        red.delete(chat_id + ANSWERS_FOR_RATE)
        for answer in answers:
            red.rpush(chat_id + ANSWERS_FOR_RATE, answer)

        return question


def get_random_answer(chat_id):
    chat_id = str(chat_id)
    answers = red.lrange(chat_id + ANSWERS_FOR_RATE, 0, -1)
    if len(answers) == 0:
        return None
    answer = red.blpop(chat_id + ANSWERS_FOR_RATE, timeout=0)
    hash_object = hashlib.md5(answer[1])
    red.set(chat_id + CURRENT_ANSWER, hash_object.hexdigest())
    return answer[1]


def add_answ_var(chat_id, answ_text):
    chat_id = str(chat_id)
    q_num = str(red.get(chat_id + QUESTION))
    red.rpush(q_num + ANSWERS, answ_text)


def add_rated_question(chat_id):
    chat_id = str(chat_id)
    q_num = str(red.get(chat_id + QUESTION_FOR_RATE))
    red.rpush(chat_id + RATED_QUESTION, q_num)


def add_rate(chat_id, rate):
    chat_id = str(chat_id)
    q_num = str(red.get(chat_id + QUESTION_FOR_RATE))
    answer_hash = red.get(chat_id + CURRENT_ANSWER)
    red.rpush(q_num + answer_hash + RATE, rate)


def get_num_for_question(chat_id):
    chat_id = str(chat_id)
    rated_questions = red.lrange(chat_id + RATED_QUESTION, 0, -1)
    if rated_questions is None:
        return 0

    if red.get(QUESTION_NUM) is None:
        red.set(QUESTION_NUM, str(0))

    q_num = int(red.get(QUESTION_NUM))
    for i in range(q_num):
        if str(i) not in rated_questions:
            return i

    return False


def get_answ_len(chat_id):
    chat_id = str(chat_id)
    q_num = str(red.get(chat_id + QUESTION))
    answers = red.lrange(q_num + ANSWERS, 0, -1)
    return len(answers)


def create_num_for_question():
    if red.get(QUESTION_NUM) == None:
        red.set(QUESTION_NUM, str(0))
    q_num = int(red.get(QUESTION_NUM))
    red.set(QUESTION_NUM, str(q_num + 1))
    return q_num


def get_question_len():
    return int(red.get(QUESTION_NUM))





def prepare_ranking():
    text = ""
    for q_num in range(get_question_len()):
        q_num = str(q_num)
        question = red.get(q_num + QUESTION)
        answers = red.lrange(q_num + ANSWERS, 0, -1)
        text += str(q_num) + ") `" + question + "`\n"
        for answer in answers:

            hash_object = hashlib.md5(answer)
            rates = red.lrange(q_num + hash_object.hexdigest() + RATE, 0, -1)
            if len(rates) == 0:
                text += "not rated"
                continue

            text += "  " + answer + " | "
            sum = 0.0
            for rate in rates:
                sum += int(rate)
            avarage = sum / len(rates)
            text += "rating: " + str(avarage)
            text += "\n"

    return text


def remove_sos_phrase(num):
    element = red.lindex(SOSS, num - 1)
    red.lrem(SOSS, -1, element)


def get_random_advice():
    phrases = red.lrange(ADVICES, 0, -1)
    if len(phrases) > 0:
        return phrases[random.randint(0, len(phrases) - 1)]
    else:
        return "Empty"


def add_advice_phrase(phrase):
    red.rpush(ADVICES, phrase)


def show_all_advice_phrases():
    phrases = red.lrange(ADVICES, 0, -1)
    text = ""
    i = 1
    for word in phrases:
        text += str(i) + ") `" + word + "`\n"
        i += 1

    return text


def remove_advice_phrase(num):
    element = red.lindex(ADVICES, num - 1)
    red.lrem(ADVICES, -1, element)


def allKeys():
    return red.keys()

def clearRedis():
    for key in red.keys():
        red.delete(key)

