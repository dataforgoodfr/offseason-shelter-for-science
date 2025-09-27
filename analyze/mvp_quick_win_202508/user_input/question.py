# coding: utf-8

def yn_question(question):
    while True:
        value = input(question + " ").lower()

        if value in yn_question.pos_answers:
            return True
        if value in yn_question.neg_answers:
            return False

        print("Invalid answer. Possible answers: %s" % yn_question.answers)

yn_question.pos_answers = ["y", "Y", "o", "O"]
yn_question.neg_answers = ["n", "N"]
yn_question.answers = yn_question.pos_answers + yn_question.neg_answers