/*
 * Card.cpp
 *
 *  Created on: Apr 23, 2021
 *      Author: jdfre
 */

#include "Card.h"
#include <string>
#include <sstream>

Card::Card(Suit sui, int va) {
	if(va < 2 || va > 14) {
		throw "ValueOutOfBounds";
	}
	suit = sui;
	val = va;
}


bool operator== (const Card &c1, const Card &c2) {
	return (c1.suit == c2.suit && c1.val == c2.val);
}

std::string Card::toString() {
	std::ostringstream outString;

	if(val < 11) {
		outString << val;
	} else if(val == 11) {
		outString << "J";
	} else if(val == 12) {
		outString << "Q";
	} else if(val == 13) {
		outString << "K";
	} else {
		outString << "A";
	}

	outString << "-";

	if(suit == spade) {
		outString << "S";
	} else if(suit == club) {
		outString << "C";
	} else if(suit == heart) {
		outString << "H";
	} else {
		outString << "D";
	}

	return outString.str();

}
