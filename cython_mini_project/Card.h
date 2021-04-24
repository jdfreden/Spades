/*
 * Card.h
 *
 *  Created on: Apr 23, 2021
 *      Author: jdfre
 */

#ifndef CARD_H_
#define CARD_H_

#include <string>

enum Suit { spade, club, heart, diamond };

class Card {
	public:
	Suit suit;
	int val;

	Card(Suit sui, int va);

	friend bool operator== (const Card &c1, const Card &c2);
	std::string toString();
};


#endif /* CARD_H_ */

