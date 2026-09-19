# JBC Discord Bot

a discord bot (WIP) with valorant and football (currently only chelsea) integrations, running on my homelab.

## Commands
 
All commands use the `!` prefix. Arguments in `[square brackets]` are optional, and `<angle brackets>` are required.
 
Wherever a command takes `[name#tag]`, you can leave it out if you've saved an account with `!setaccount`. `[region]` defaults to `eu` (other options include `na`, `ap` and `kr`).
 
### Quick reference
 
| Command | What it does |
| --- | --- |
| `!rank [name#tag] [region]` | Shows current rank and RR |
| `!todayrr [name#tag] [region]` | Shows net RR and W/L over the last 14 hours |
| `!recentgames [name#tag] [region] [count]` | Shows recent competitive games with agent, K/D/A and RR |
| `!crosshair <code>` | Renders a preview image of a crosshair code |
| `!setaccount <name#tag> [region]` | Saves your Riot ID so you can skip it in other commands |
| `!myaccount` | Shows your saved account |
| `!clearaccount` | Removes your saved account |
 
### Stats
 
**`!rank [name#tag] [region]`**
Shows the player's current rank and RR, with the rank icon.
```
!rank wad2k#jbc
!rank wad2k#jbc na
!rank
```
 
**`!todayrr [name#tag] [region]`**
Shows net RR gained or lost, and the win/loss count, for games played in the last 14 hours.
```
!todayrr wad2k#jbc
!todayrr
```
 
**`!recentgames [name#tag] [region] [count]`**
Lists recent competitive games. Each game shows the map, agent, K/D/A (with KDA ratio), round score, RR change and how long ago it was played. The footer shows your W/L record, overall K/D and net RR.
`count` is how many games to show: 1-10, default 5.
```
!recentgames
!recentgames wad2k#jbc
!recentgames wad2k#jbc eu 8
```
 
### Crosshair
 
**`!crosshair <code>`**
Renders a preview image from a Valorant crosshair code.
```
!crosshair 0;P;h;0;0l;5;0v;3;0g;1;0o;2;0a;1;0f;0;1b;0
```
 
### Saved account
 
**`!setaccount <name#tag> [region]`**
Saves your Riot ID (and region) to your Discord user. The bot checks the account exists before saving it. Once set, you can run `!rank`, `!todayrr` and `!recentgames` with no arguments.
```
!setaccount wad2k#jbc
!setaccount wad2k#jbc na
```
 
**`!myaccount`**
Shows the account you currently have saved.
 
**`!clearaccount`**
Removes your saved account.


## Dev Setup (for those who want to contribute 🤓)

Moved this stuff to the wiki.
