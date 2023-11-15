import random

#In-memory single thread.
#ETAPA 1 - Jogador se inscreve com um alias no torneio, e fica esperando na fila.
#ETAPA 1.1 - Etapa 1 se repete até ter quatro jogadores, então, o matchmaking é chamado.
def doTest():
	result = organizeBrackets(["caio", "luigi", "edu", "gustas"])
	print("Tournament winner:", result)

#ETAPA 2 - Sortear os 4 jogadores, em duas partidas diferentes.
def organizeBrackets(players):
	match1 = []
	match2 = []

	random.shuffle(players)  # Shuffle the players in place

	match1.append(players.pop(0))
	match1.append(players.pop(0))
	match2.append(players.pop(0))
	match2.append(players.pop(0))

	winner1 = doMatch(match1)
	winner2 = doMatch(match2)

	return doMatch([winner1, winner2])


def doMatch(match):
	# jogo acontece e ganhador é retornado
	return random.choice(match)

if (__name__ == '__main__'):
	doTest()

#	Torneio
#endpoint nextTournmentMatch()
#{nextMatch: match_name}

# match_name, player1,	player2,	winner,		isFinal
# game1,		caio,		luigi,		null,	false
# match_name, player1,	player2,	winner,		isFinal
# game2,		edu,		gustas,		null,	false

#if partida is over and user in tournment, if winner = user, next_match.


#channel_name = player conection
#match_name

# inTournament = true





#nome do torneio, players, 
#torneio1, [caio,luigi,rafa,edu]
