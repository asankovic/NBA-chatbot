#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from chatterbot import filters
from chatterbot import ChatBot
from chatterbot import comparisons
from chatterbot.trainers import ListTrainer
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade import quit_spade
from spade.template import Template
from spade.message import Message

chatbot = ChatBot("NbaBot", storage_adapter='chatterbot.storage.SQLStorageAdapter',logic_adapters=[
		{'import_path':'chatterbot.logic.BestMatch',
		"statement_comparison_function": comparisons.JaccardSimilarity,
		'default_response':'I think I\'ve missed it somehow. Uhh, awkward..'}],
	filters=[filters.get_recent_repeated_responses])

class NbaBotAgent(Agent):
	class Ponasanje(FSMBehaviour):
		async def on_start(self):
			print(f"Pocetno stanje automata: {self.current_state}")
		async def on_end(self):
			print(f"Zavrsno stanje automata: {self.current_state}")
	
	class StanjeSlanja(State):
		async def run(self):	
			global chatbot
			self.agent.pitanje = input("BOT: What do you want to know?\nYou: ")
			if "bye" not in self.agent.pitanje.strip().lower():
				odgovor = chatbot.get_response(self.agent.pitanje)
				if odgovor.confidence <= self.agent.minimalna_sigurnost:
					msg = Message(
						to = "agent@rec.foi.hr",
						body = self.agent.pitanje,
						metadata = {
							"ontology":"nba",
							"language":"english",
							"performative":"inform"})
					await self.send(msg)
					print("BOT: Hold on, I'll ask a friend.")
					self.set_next_state(self.agent.STANJE_PRIMANJA)
				else:
					print(f"BOT: {odgovor}")
					self.set_next_state(self.agent.STANJE_SLANJA)
			else:
				msg = Message(
					to = "agent@rec.foi.hr", 
					body = "END", 
					metadata = {
						"ontology":"nba",
						"language":"english",
						"performative":"inform"})
				await self.send(msg)
				self.set_next_state(self.agent.ZAVRSNO_STANJE)
				
	class StanjePrimanja(State):
		async def run(self):
			global chatbot
			self.msg = await self.receive(timeout=20)
			if(self.msg):
				odgovor = chatbot.get_response(self.agent.pitanje)
				print(f"BOT: {odgovor}")
				self.set_next_state(self.agent.STANJE_SLANJA)
			else:
				print("BOT: Sorry, my friend couldn't find out :(")
				self.set_next_state(self.agent.STANJE_SLANJA)
			
	class ZavrsnoStanje(State):
		async def run(self):
			print("BOT: Bye, my friend. It was nice talking to you!")
			await self.agent.stop()
	
	async def setup(self):
		print("BOT: I'm waking up..")
		
		self.STANJE_SLANJA = "StanjeSlanja"
		self.STANJE_PRIMANJA = "StanjePrimanja"
		self.ZAVRSNO_STANJE = "ZavrsnoStanje"
		
		self.pitanje = ""
		self.minimalna_sigurnost = 0.9
		
		fsm = self.Ponasanje()
		
		fsm.add_state(name=self.STANJE_SLANJA, state=self.StanjeSlanja(), initial = True)
		fsm.add_state(name=self.STANJE_PRIMANJA, state=self.StanjePrimanja())
		fsm.add_state(name=self.ZAVRSNO_STANJE, state=self.ZavrsnoStanje())
		
		fsm.add_transition(source=self.STANJE_SLANJA, dest=self.STANJE_PRIMANJA)
		fsm.add_transition(source=self.STANJE_SLANJA, dest=self.STANJE_SLANJA)
		fsm.add_transition(source=self.STANJE_SLANJA, dest=self.ZAVRSNO_STANJE)
		
		fsm.add_transition(source=self.STANJE_PRIMANJA, dest=self.STANJE_SLANJA)
		fsm.add_transition(source=self.STANJE_PRIMANJA, dest=self.STANJE_PRIMANJA)
		fsm.add_transition(source=self.STANJE_PRIMANJA, dest=self.ZAVRSNO_STANJE)
		
		predlozak = Template(metadata = {"ontology":"nba"})
		
		self.add_behaviour(fsm, predlozak)

if __name__ == "__main__":
	chatAgent = NbaBotAgent('asankovic@rec.foi.hr','2zAX4awt')
	pokretanje = chatAgent.start()
	pokretanje.result()
	while chatAgent.is_alive():
		try:
			time.sleep(1)
		except KeyboardInterrupt:
			break
	chatAgent.stop()
	quit_spade()		
