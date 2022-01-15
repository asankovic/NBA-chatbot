import NbaPlayers
import spacy
from chatterbot import ChatBot
from chatterbot.conversation import Statement

chatbot = ChatBot("NbaBot", storage_adapter='chatterbot.storage.SQLStorageAdapter')
nlp = spacy.load("en_core_web_sm")
player = ""
NbaPlayers.setup()

def store_answer(question, answer):
    statements = []
    statement_search_text = chatbot.storage.tagger.get_bigram_pair_string(answer)
    phrase_search_text = chatbot.storage.tagger.get_bigram_pair_string(question)
    statement = Statement(text = answer,
                      search_text = statement_search_text,
                      in_response_to = question,
                      seach_in_response_to = phrase_search_text,
                      conversation = 'nba')
    statements.append(statement)
    chatbot.storage.create_many(statements)

def find_answer(question):
    answer = ""
    doc = nlp(question)
    verbs = [token.lemma_ for token in doc if token.pos_ == "VERB"]
    adjectives = [token.lemma_ for token in doc if token.pos_ == "ADJ"]
    nouns = [token.lemma_ for token in doc if token.pos_ == "NOUN"]
    numbers = [token.lemma_ for token in doc if token.pos_ == "NUM"]
    
    for ent in doc.ents:
        #spacy nekad neke igrace ne definira kao person, vec kao gpe (geopoliticki entitet)
        if ent.label_ != "PERSON" and ent.label_ != "GPE" :
            continue

        player = ent.text.replace("'s", '')
        if player.lower() not in NbaPlayers.players:
            answer += "I don't know about " + player +". "
            continue
        
        
        if 'team' in nouns:
            answer += player + "'s team abbreviation is " + NbaPlayers.players[player.lower()].team + ". "

        if 'old' in adjectives or 'age' in nouns:
            answer += player + " is " + str(NbaPlayers.players[player.lower()].age) + " years old. "

        if 'game' in nouns and 'play' in verbs:
            answer += player + " played a total of " + str(NbaPlayers.players[player.lower()].games_played) + " games this season. "

        if 'minute' in nouns and ('play' in verbs or 'play' in nouns):
            answer += player + " played a total of " + str(NbaPlayers.players[player.lower()].minutes_played) + " minutes this season. "

        if 'win' in verbs or 'win' in nouns:
            if 'percentage' in nouns:
                answer += player + " 's team " + NbaPlayers.players[player.lower()].team + ", has won " + str(NbaPlayers.players[player.lower()].win_percentage*100) + "% of their games this season. "
            else:
                answer += player + " 's team " + NbaPlayers.players[player.lower()].team + ", has won " + str(NbaPlayers.players[player.lower()].wins) + " games this season. "

        if 'lose' in verbs or 'lose' in nouns:
            answer += player + " 's team " + NbaPlayers.players[player.lower()].team + ", has lost " + str(NbaPlayers.players[player.lower()].loses) + " games this season. "

        if 'field' in nouns and 'goal' in nouns:
            if 'attempt' in nouns or 'attempt' in verbs:
                if 'three' in numbers:
                    answer += player + " has attempted a total of " + str(NbaPlayers.players[player.lower()].field_goal_3_attempt) + " three pointers this season. "
                else:
                    answer += player + " has attempted a total of " + str(NbaPlayers.players[player.lower()].field_goal_attempt) + " two pointers this season. "
            elif 'make' in verbs:
                if 'three' in numbers:
                    answer += player + " has scored a total of " + str(NbaPlayers.players[player.lower()].field_goal_3_made) + " three pointers this season. "
                else :               
                    answer += player + " has scored a total of " + str(NbaPlayers.players[player.lower()].field_goal_made) + " two pointers this season. "
            if 'percentage' in nouns:
                if 'three' in numbers:
                    answer += player + " is shooting " + str(NbaPlayers.players[player.lower()].field_goal_3_percentage*100) + "% from three point this season. "
                else:             
                    answer += player + " is shooting " + str(NbaPlayers.players[player.lower()].field_goal_percentage*100) + "% for two this season. "

        if 'free' in adjectives and 'throw' in nouns:
            if 'attempt' in verbs or 'attempt' in nouns:
                answer += player + " has attempted a total of " + str(NbaPlayers.players[player.lower()].free_throws_attempt) + " free throws this season. "
            elif 'make' in verbs:
                answer += player + " has made a total of " + str(NbaPlayers.players[player.lower()].free_throws_made) + " free throws this season. "
            elif 'percentage' in nouns:
                answer += player + " is shooting " + str(NbaPlayers.players[player.lower()].free_throws_percentage*100) + "% from the free throw line this season. "
                

        if 'rebound' in nouns:
            if 'offensive' in adjectives or 'offense' in nouns:
                answer += player + " has gotten a total of " + str(NbaPlayers.players[player.lower()].rebounds) + " offensive rebounds so far this season. "
            if 'defensive' in adjectives or 'defense' in nouns:
                 answer += player + " has gotten a total of " + str(NbaPlayers.players[player.lower()].def_rebound) + " defensive rebounds so far this season. "
            answer += player + " has gotten a total of " + str(NbaPlayers.players[player.lower()].off_rebound) + " rebounds so far this season. "

        if 'assist' in nouns:
            answer += player + " has assisted a total of " + str(NbaPlayers.players[player.lower()].assists) + " times so far in this season. "
                
        if 'turnover' in nouns:
            answer += player + " has lost a possesion a total of " + str(NbaPlayers.players[player.lower()].turnovers) + " times so far in this season. "

        if 'steal' in nouns:
            answer += player + " made a steal " + str(NbaPlayers.players[player.lower()].steals) + " times so far in this season. "
                
        if 'block' in nouns:
            answer += player + " blocked a shot " + str(NbaPlayers.players[player.lower()].blocks) + " times so far in this season. "
                
        if 'point' in nouns:
            answer += player + " scored a total of " + str(NbaPlayers.players[player.lower()].points) + " so far in this season. "
    if answer:    
        store_answer(question, answer)
