# Credentials and destinations, per provider

What each service needs in order to send, and how a destination is checked before a report carrying customer
names goes to it. Extend the table when a channel is added — the value is in not having to work it out twice.

## The credential the person holds

| Service | Credential | Shape | Trap |
|---|---|---|---|
| Gmail / Google Workspace (SMTP) | app password | 16 letters | Google displays it in four groups (`abcd efgh ijkl mnop`) and the login rejects the spaces: pasted as shown, SMTP answers 535 and the message blames the credentials. The account needs two-step verification before app passwords exist at all. Normalize on read, only for that exact shape. |
| Telegram | BotFather token | `<8–12 digits>:<30–40 url-safe chars>` | It is embedded in every request URL (`…/bot<token>/<method>`), so it must never be printed, echoed into an error, or kept in a config file. |

The password/app password and the bot token are the **person's** steps: they are typed at a prompt, or
generated in a web console the agent has no access to. Handing them the finished command is the most that can
be done for them.

## Does the token work? (without printing it)

`GET <api>/bot<token>/getMe` returns the bot's `username` and `first_name`. A 200 from that endpoint proves
the token is valid and names the account, and neither the token nor any part of it appears in the output.
Worth doing whenever the token arrived from somewhere other than the console.

## Discovering the destination

- **A bot only sees chats that wrote to it.** `getUpdates` (or a `--chats` command wrapping it) returns what
  arrived since the last read; an empty list means **nobody has written yet**, which is a step only the person
  can do (open the bot, press Start). Retry after they do it — do not read the empty list as a bug.
- **The sign of the id says whether it is private.** Positive → one-to-one chat; negative → group or
  supergroup (supergroups are prefixed `-100`). A report with customer names/balances goes only to an
  internal one-to-one chat, so check the sign rather than the title.
- **What goes in the config is the id, not a name.** The allowlist is a list of ids; a display name is not a
  check and can be changed by whoever controls the account.
