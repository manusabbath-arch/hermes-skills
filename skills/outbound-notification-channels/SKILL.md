---
name: outbound-notification-channels
description: "Use when adding an outbound channel (email, chat, webhook, ntfy) so a report or alert leaves the machine without attaching it by hand: secrets in the OS store, off by default, injected transport, and delivery is not the same as generating the artifact."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [notifications, email, telegram, webhook, secrets, scheduler]
    category: software-development
    related_skills: [unattended-run-verification, agent-ready-project]
---

# Adding an outbound channel (email, chat, webhook)


## Cuándo NO aplicarla

Si el pedido es el texto de un mensaje o el diseño de un informe, se responde **solo eso**.
Esta skill aplica cuando hay que **abrir un canal** que publica hacia afuera.

When the ask is "make the report/alerts reach someone without me attaching them by hand" — a daily report by
email, an alert to a phone, a webhook on a threshold. The system already has the hard part: commands that
produce the number **with its provenance**, a gate, and guards. The channel is a **new door to the same room**,
not a new source of figures and not a new path to the data.

## The shape every outbound channel repeats

Copy the channel that already exists in the repo (the mail sender, if there is one) instead of inventing a second shape. The pieces:

1. **Off by default, and a hand run cannot publish.** Nothing is sent until a config file exists outside the repo (`config/<channel>.txt`); the file names the destination (recipients, chat ids) —
and **never the secret**. But "off by default" stops being a guard the moment the file exists: the send path
refuses a manual `--enviar` unless the scheduler set a marker env var (the launcher script exports it) or an
explicit `--confirmar-envio` was passed, and returns its own exit code when it refuses. The draft path
(`--a-archivo`, which renders and never sends) keeps working with no marker at all — that is what makes the
guard liveable while reviewing the text.
2. **The secret lives in the OS secret store**, not in the repo and not in the config file. The config reader
must **reject** a `password:`/`token:`/`key:`/`clave:` line with an error that points at the store (the OS secret store: `keyring` → Windows Credential Manager, or the platform equivalent). Read it at run time, never print it, the agent never types it.
3. **Inject the transport.** `enviar(..., smtp=...)` / `enviar(..., http=...)`: no test touches the network. Use
the standard library (`smtplib`, `urllib`) before adding a dependency.
4. **Opt-in flag on the existing command, not a new pipeline.** `cmd --enviar` / `cmd --telegram`, so the report
and the channel stay one code path. Return a string starting with `Enviado`/`Sent` on success and an exit code
the caller can act on.
5. **Wire it into the scheduler, but keep the scheduler agent-free.** A scheduled job that runs commands must
not gain an agent inside it; the transport is a plain module. (Write it into the scheduled-job contract: no agent inside the launcher.)
6. **Log the outcome.** Print what was sent and to whom (it lands in the job log). Watch that the artifact was
**produced**, not that the message **arrived** — those are different checks and only the second is delivery.
7. **The provenance travels with the message.** Any number that leaves through an external channel cites its
source and date; the channel is never a fresh source of figures.

## Turning it on (one time, and the order matters)

Writing the module is the easy half. The channel only works once the credential and the destination are in
place, and those steps have a dependency order that a naive how-to tends to get wrong:

1. **The secret goes into the OS store first, and nobody reads it.** The person may hand it over as a file
   (a note, a `.txt` on the desktop) instead of typing it at the prompt. Move it **file → store inside one
   process** and print back only its *shape* (length, whether re-reading the store returns the same string,
   whether it matches the provider's format) — never the value, not even a prefix. Check the shape *before*
   storing, so a wrong file fails loudly without the value ever entering the transcript or a log. Then tell
   the person to delete the plain-text file: it is already redundant and it is a secret sitting in the open.
   Do the move in a one-shot process that never prints the value (length and read-back match only).
2. **Label the store entry with the real identity of the service**, not a placeholder copied from an example
   in the docs: the sending address, the bot's actual `@username`. The config and the reader both key on that
   label, and a placeholder leaves a future reader unable to tell which account the entry belongs to. To fix
   a label, copy store→store in a single process (the value never leaves it), verify the copy equals the
   original, then delete the old entry.
3. **The config file must exist before the destination id can be discovered.** A bot API only reveals chats
   that have already written to it, and the lookup command needs the config to know *which* bot's token to
   use — so the order is: write the config with a **provisional destination**, run the discovery, put the
   real id in. A how-to that says "discover the id, then create the config" cannot be followed; when you hit
   one, that order *is* the bug — fix it in every copy (a module docstring and an integration doc are usually
   two).
4. **Prove it with one real send, per path.** The text message and the attachment are different API calls:
   the test command proves the first and says nothing about the second. Probe the attachment with a throwaway
   file before the scheduled job depends on it, then have the person confirm what arrived — an API answering
   "sent" is all you have, and their screen is the only witness. Separately, probe the **credential alone**
   with a call that has no side effect — a bot's `getMe`, an SMTP connect + `starttls` + `login` that closes
   without sending — so a bad secret is diagnosed before anything is published to a real destination.
5. **Decide what the scheduled job does while a credential is still missing.** A channel switched on but
   unable to authenticate fails on every run, and the warning lands in the job log — not in the chat, so
   nobody sees it. Either keep the config out until the last credential exists, or keep it in and say plainly
   where the warning goes. Do not leave a silent daily failure as an accident.

Per-provider credential shapes, discovery commands and destination checks:
`references/credenciales-y-destinos.md`.

## What the scheduled run will actually do: read it, do not infer it

The channel matters only through the job that fires it. Before saying when the next message goes out — and
before promising anything to the person — read the scheduler's own record instead of reasoning from the
command that created it:

- **Read the trigger and its settings.** On Windows `schtasks /query /tn "<name>" /xml` gives the exact day
  set (`DaysOfWeek`), the start time, `StartWhenAvailable`, the execution time limit and the battery rule. A
  job created "daily" is often a weekday set, and a job for a daily report can still be Mon–Fri.
- **A missed start is not a lost run.** With `StartWhenAvailable` a run skipped because the machine was off
  fires as soon as it is back on, so the report goes out late rather than missing. Say it explicitly: the
  person's worry ("the machine will be off") usually points at the wrong failure.
- **Resolve the date before naming a day.** "Tomorrow at 07:30" is a claim about the calendar and about the
  day set — check both. Naming a weekday the schedule does not cover is a small error that costs trust in
  everything else you said about the channel.
- **Two dependencies, not one.** A report built from a live source needs that source reachable, not just the
  machine on: an off server or an off-hours window fails the run on its own. Name which dependency is which,
  or the person reads a source outage as "the channel broke".

## A reply bot is a new door, not a new path to the data

If the channel can **receive** (a bot that answers questions), two hard limits:

- **Closed command catalog, never generated SQL/queries.** Map each question to an existing vetted command. A
bot that writes its own query is a second path to the data — exactly what a "one door to the data" doctrine
forbids (a read-only database MCP is still a second path).
- **Allowlist by identity** (numeric chat/user id, not the bot's obscurity). A bot without an allowlist is usable
by anyone who finds its name; a one-owner/team bot must list the ids and silently drop the rest. Keep the bot
out of the scheduled job.
- Respect the system's own access rules: if the data source has an off-hours window or goes offline, the bot
says so instead of forcing a query.
- **Read-only by default; a bot that WRITES is a separate design.** Answering with a command's output is safe
and reusable. Letting a message change state (record a decision, log an authorization, close a case) is a
**write path** into the versioned store and needs its own rules *before* it exists: who did it and when, keyed
by an internal id rather than a person's name (customer/third-party names never enter the versioned store), and
a **draft the human confirms** instead of a silent commit. Until that is designed, the bot only reports.
When it *is* designed, the invariants that decide whether it holds up are: state in the versioned book and
not in the process (a restart must not lose a half-answered message), a deterministic id derived from
`chat:message_id` so a redelivered update is the same record and a keyboard pressed a week later cannot
claim a record that already closed, every failure path answering with text instead of raising into the
listener loop, and the book actually reaching the versioned store — the job that commits the other ledger
has to be taught about the new file, or the loop "closes" in a local file nobody diffs. Full recipe,
schema and tests: `references/chat-write-loops.md`.
- **The catalog can only call first-class commands.** Before promising a question to the chat, check the
capability is reachable *as a command* and not just as a bare script — a module that runs but has no
`<cli> <sub>` entry cannot be catalogued, so promoting it (subcommand + its line in the CLI docstring, which a
test may enforce) is the first step, not the bot.
- **Grep the catalog for the word before wiring a new handler, or one message gets two answers.** A word
that already maps to a command (`/carga` listing pending loads) is taken: a second handler that normalizes
that same word answers the same update twice — one real reply and one wrong one, from the operator's point
of view a bot that is broken. Pick a word that is free and put it in the help text in the same change.

## Keeping the reply half listening

A bot that only answers while somebody runs its command is not a channel — "the bot is up" then means "a
terminal somewhere is open". Turning the listening half on is a separate job from sending, with its own rules:

- **The listener starts without a person, at logon, and relistens when it dies.** The mechanism is the OS's. On
  Windows a scheduler task can carry the settings that matter (`StartWhenAvailable`,
  `MultipleInstances=IgnoreNew`, a restart count and interval) but creating one needs elevation: `schtasks
  /Create` answers *access denied* for a plain user, on a custom folder and in the root alike. The no-admin
  route is a small launcher in the user's own Startup folder that calls the project's wrapper script. Give the
  wrapper the loop the scheduler would have given you — relaunch while the child exits non-zero — and **let it
  exit 0 when the channel is off** (no config, no secret), so a switched-off channel does not spin forever.
- **Two listeners on the same bot steal each other's messages.** Every poll advances the update offset, so the
  two answer alternate messages and each one looks broken. If the mechanism you chose has no single-instance
  guard, enforce it in the program (a lock or claim that refuses a second start); do not rely on the launcher
  being launched once.
- **To check the listener is alive, match the process NAME, not a substring of its command line.** The shell
  running the check carries the search string in *its own* command line, so a command-line filter matches the
  checker and reports a healthy process that is not there — and a `Stop-Process` over that match kills your own
  tool shells mid-session. Filter on the interpreter (`Name -like 'python*'`) plus the pattern.
- **Process count is not the number of listeners: a launcher chain repeats the same command line.** A
  wrapper that re-executes its child (`uv run … python cli.py …` → `python.exe` → `python.exe`, or a `.vbs` →
  `powershell` → `python`) leaves two or three pids whose `CommandLine` is identical and whose start time is
  the same. That is ONE listener, and calling it a duplicate is a claim about the user's machine that will
  be wrong. Do not settle it by counting or by `ParentProcessId` alone: ask which pid owns the connection to
  the provider — `netstat -ano | grep <provider ip>` and look at the `ESTABLISHED` line's last column. One
  socket, one poller.
- **`schtasks /End` kills the launcher, not its grandchild, so every restart cycle adds a poller.** The
  task's `wscript`/`powershell` dies and the interpreter under it keeps polling — invisible until the two
  start stealing each other's updates. To restart a chain: enumerate by name *and* command pattern, kill
  every pid of the chain, verify the count reached zero, and only then start exactly one, verifying again
  after it has come up.
- **Start the interpreter unbuffered if the log is what you will read next.** A listener's output is block-
  buffered once it goes through a pipe, so its log can stay empty for hours while it works — and then you
  cannot tell "listening since 23:44" from "died at 23:45".
- **A liveness check that enumerates processes can report a false red while the machine is loaded.** Two heavy
  test suites running at once made a "is the bot listening" check go PASS → FAIL → PASS with no code change:
  the enumeration simply did not see the listeners' pids among the dozens of short-lived interpreters. Re-run
  that check **alone** before believing it, and never declare it red or edit the check over it — the failure was
  in the measurement, not in the channel. The inverse is the same trap: a green from that check under load is
  worth as much as the red.

## Choosing the channel

| Channel | Cost / friction | Reach | When |
|---|---|---|---|
| Email | already built, free | whoever reads mail | default; lowest friction |
| Telegram | free, no paperwork, minutes | internal 1–2 people | first channel for an operator; nobody else uses it |
| WhatsApp Business | business verification, own number, approved template, per-message fee | where the team already is (field staff) | when reach matters; start with the slow step (verification) |

Privacy: a report with customer names/balances goes to an **internal** recipient only, never a group with third
parties, and never via a public URL.

## Pitfalls

- **"Off by default" is a file that may already be there: read it in the same command that decides, never
the line before.** Measured (17/10/26): the enable file `config/enviar.txt`
existed, and an agent ran `decisiones-mail --enviar` "to verify the channel before its first scheduled
run". The mail reached a real recipient two days early. The guard check (`ls <file> || echo "off"`) was a
separate line, so the send ran in the same shell anyway. Prove the rendering through the command's own
draft path (`--a-archivo <file>`, which never sends), and if the enable file is present the send IS live:
say so before running it, or make the command refuse to send unless the scheduler set an env var or an
explicit confirmation flag was passed.
- **A manual run of the send command lands in the same log the freshness check reads.** The next gate run
reports whatever your hand-run's exit code says, and the day you test the channel is the day its green
turns red (or a real red turns green). It is not a false alarm —the command did run and did exit that
way— so investigate the log entry, not the check, and never edit the log to hide it.
- **A secret in the config file is the default mistake.** Put the check in the loader itself (reject a secret
line), so a later edit cannot reintroduce it.
- **A fake transport that returns a fixed success proves nothing about the request.** Have the stub record the
URL/payload and assert on it; and remember the real send is only proven by the one manual `--probar` run.
- **"The report was generated" is not "the message was delivered."** Do not let a freshness/health check that
watches the artifact pass for delivery; delivery needs its own signal.
- **Do not re-query the live source to build the channel.** The channel formats and ships what the command
already produced.
- **A reply bot inside the cron/scheduled job** turns a dumb sender into an agent in the production loop.
- **A chat message has a hard size cap, and an over-long report fails to arrive silently.** Telegram caps a
message at 4,096 characters; a full decisions/agenda document ran ~6,100 and the API answers 400 — *nothing*
reaches the chat, while the sender still thinks it succeeded. Trim to a safe margin (leave room for a subject
line and the provenance seal), **cut at a line break** rather than mid-sentence, say in the message that it was
trimmed, and assert the length in a test. "The command produced it" does not mean "the chat can carry it".
- **Don't add a library for one HTTP POST.** stdlib `urllib` (plus a small multipart writer for file uploads) is
  enough and keeps the dependency surface flat.
- **A credential's displayed form is not necessarily its usable form.** A Gmail app password is 16 letters
  that Google shows grouped in fours (`abcd efgh ijkl mnop`); pasted as shown, `smtplib` answers 535 and the
  error blames the credentials, which sends you after the wrong cause. Normalize on read — and only for that
  exact shape, so a real password carrying legitimate spaces is left untouched.
- **Check that the destination is internal by its id, not by its name.** A Telegram private chat has a
  positive id; groups and supergroups are negative — and the display name ("the company", a person's name)
  cannot tell you which one you got. The privacy rule is about the recipient, so the id is the check.
- **Your own test fixture can trip the repo's secret scanner.** A fake credential assigned to a name
  containing "password"/"token" (`fake.get_password = ...`) is exactly what a scanner looks for. Write the
  fake differently instead of disabling the guard: `monkeypatch.setattr("mod.func", ...)`, or a small class
  with the method defined inside it.
- **A failed run writes its error where the data goes — and the repair belongs in the producer, not in the
  cleanup.** A report that pipes a query's output into a dated file leaves the driver's error message in that
  file when the source is down, and a later reader — or the report's own cache — parses it as data. The fix is
  on the writer's side: the command that owns the artifact **must not touch the destination when the run
  failed**; it writes what came out beside it (`<salida>.fallida`), says so, and exits non-zero. Deleting the
  poisoned file afterwards is damage control: it also destroys the evidence that the run happened, and it does
  nothing for the next failure. When a consumer writes the destination itself, it has copied the guarded writer
  with the guard removed — grep for the siblings of that call path, they usually share the defect — and prove
  the repair by running the real command against the real, failing source with a throwaway destination.

## Verification

- Unit tests: config parsing (off when absent; secret line rejected; destination required), message building,
  the no-secret path does not connect, a stub transport records one call per destination.
- End-to-end: a `--probar`/`--test` command that sends a real message to one destination. That manual run is the
  only proof the credentials and the network path work; do it **before** wiring the channel into the scheduler,
  and register it in the write-up.
- **Proving the guard without sending a second message.** When the guard is the marker-env-var/confirmation pair,
  all four directions are provable with zero sends: (a) a hand `--enviar` against the **real** config refuses
  with its own exit code, and a stubbed transport proves it was never called; (b) the marker var plus a
  `--config` pointing at a file that does not exist passes the guard and "off" decides, exit 0; (c) a small
  launcher script that exports the var and runs `python -c "import os; print(os.environ.get('<VAR>'))"` shows the
  **child** sees it, which is exactly what the scheduled job depends on; (d) the launcher is parsed without being
  executed (`[scriptblock]::Create((Get-Content -Raw <script.ps1>))`) so a one-line edit cannot break the
  scheduled path days before it first runs. Then state plainly what is left unproven: the real scheduled send.

## Fuente canónica

Repo-tap `manusabbath-arch/hermes-skills` (`skills/outbound-notification-channels`). Editar acá, nunca la copia instalada.
