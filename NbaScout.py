#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import TextAnalyser
import time
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade import quit_spade
from spade.template import Template
from spade.message import Message

class NbaScoutAgent(Agent):
	class Ponasanje(FSMBehaviour):
		async def on_start(self):
			print(f"Pocetno stanje automata: {self.current_state}")
		async def on_end(self):
			print(f"Zavrsno stanje automata: {self.current_state}")
			
	class StanjeSlanja(State):
		async def run(self):
			msg = Message(
				to = "asankovic@rec.foi.hr",
				body = "OK",
				metadata = {
					"ontology":"nba",
					"language":"english",
					"performative":"inform"})	
			await self.send(msg)
			print("Poslano 'OK'!")
			self.set_next_state(self.agent.STANJE_PRIMANJA)
		
	class StanjePrimanja(State):
		async def run(self):
			self.msg = await self.receive(timeout=300)
			if(self.msg):
				print(f"SCOUT: Primljeno: {self.msg.body}")
				if(self.msg.body == "END"):
					self.set_next_state(self.agent.ZAVRSNO_STANJE)
					return
				TextAnalyser.find_answer(self.msg.body)	
			self.set_next_state(self.agent.STANJE_SLANJA)
			
	class ZavrsnoStanje(State):
		async def run(self):
			print("Shutting down..")
			await self.agent.stop()
			
	async def setup(self):
		print("NbaScout se pokreće")
		fsm = self.Ponasanje()
		
		self.STANJE_SLANJA = "StanjeSlanja"
		self.STANJE_PRIMANJA = "StanjePrimanja"
		self.ZAVRSNO_STANJE = "ZavrsnoStanje"
		
		fsm.add_state(name=self.STANJE_SLANJA, state=self.StanjeSlanja())
		fsm.add_state(name=self.STANJE_PRIMANJA, state=self.StanjePrimanja(), initial = True)
		fsm.add_state(name=self.ZAVRSNO_STANJE, state=self.ZavrsnoStanje())
		
		fsm.add_transition(source=self.STANJE_SLANJA, dest=self.STANJE_PRIMANJA)		
		fsm.add_transition(source=self.STANJE_PRIMANJA, dest=self.STANJE_SLANJA)
		fsm.add_transition(source=self.STANJE_PRIMANJA, dest=self.ZAVRSNO_STANJE)
		
		predlozak = Template(metadata = {"ontology":"nba"})
		
		self.add_behaviour(fsm,predlozak)	

if __name__ == "__main__":
	agent = NbaScoutAgent('agent@rec.foi.hr','tajna')
	pokretanje = agent.start()
	pokretanje.result()
	while agent.is_alive():
		try:
			time.sleep(1)
		except KeyboardInterrupt:
			break
	agent.stop()
	quit_spade()	
