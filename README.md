# Discord Bot

This discord bot allows some simple moderation and the ability to play Hangman, Minesweeper, and 2048 within Discord. Its main purpose is not moderation though, and more entertainment.
There is a second, unrelated bot in the /ryan folder, but that was just a small test.

This uses a SQL server, so that needs to be set up. The format of the database is:

```SQL
+--------+-----------------+------+-----+---------+-------+
| Field  | Type            | Null | Key | Default | Extra |
+--------+-----------------+------+-----+---------+-------+
| user   | varchar(50)     | NO   | PRI | NULL    |       |
| server | varchar(50)     | NO   | PRI | NULL    |       |
| coins  | bigint unsigned | NO   |     | 10      |       |
| gifted | bigint unsigned | NO   |     | 0       |       |
+--------+-----------------+------+-----+---------+-------+
```

## Commands

### Games

- games hangman
  Play Hangman
- games minesweeper
  Play Minesweeper
- games 2048
  Play 2048

### QTC Coins

- bet
  Bet QTC coins on heads or tails, or the middle of the coin
- check-balance
  Check QTC balance of a user
- leaderboard
  Check QTC coin leaderboard for the server
- gift
  Gift QTC coins to another user

### Moderation

- warn
  Warn a person
- remove-warns
  Remove specified amount of warns from user
- reset-warns
  Pardon user of all warns
- check-warns
  Check the amount of warns of a user
- lock
  Prevent members from speaking in a channel
- unlock
  Allow members to speak in a channel
- mute
  Prevent person from speaking
- unmute
  Allow person to speak after being muted

### Miscellaneous

- roll-dice
  Roll specified amount of dices with a select number of sides
- 8-ball
  Ask the 8-ball a question
- flip-coin
  Flip a coin
- thick-of-it
  Respond with the lyrics to Thick of It by KSI
- pyan
  Ping Pyan
- speak
  Make the bot say anything
- profile
  View anybody in the server's profile
