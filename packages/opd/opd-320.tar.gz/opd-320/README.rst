**NAME**


``opd`` - **O** riginal **P** rogrammer **D** aemon


**SYNOPSIS**

|
| ``opd <cmd> [key=val] [key==val]``
| ``opd [-cdsv]`` 
|

**DESCRIPTION**

``opd`` is a python3 bot, it can connect to IRC, fetch and display RSS
feeds, take todo notes, keep a shopping list and log text. You can
also copy/paste the service file and run it under systemd for 24/7
presence in a IRC channel.

``opd`` has all you need to program a unix cli program, such as disk
perisistence for configuration files, event handler to handle the
client/server connection, deferred exception handling to not crash
on an error, etc.

``opd`` contains python3 code to program objects in a functional way.
It provides a base Object class that has only dunder methods, all
methods are factored out into functions with the objects as the first
argument. It is called Object Programming (OP), OOP without the
oriented.

``opd`` allows for easy json save//load to/from disk of objects. It
provides an "clean namespace" Object class that only has dunder
methods, so the namespace is not cluttered with method names. This
makes storing and reading to/from json possible.

``opd`` is Public Domain.

**INSTALL**

installation is done with pipx

|
| ``$ pipx install opd``
| ``$ pipx ensurepath``
|
| <new terminal>
|
| ``$ opd srv > opd.service``
| ``$ sudo mv opd.service /etc/systemd/system/``
| ``$ sudo systemctl enable opd --now``
|
| joins ``#opd`` on localhost
|

**USAGE**

use ``opd`` to control the program, default it does nothing

|
| ``$ opd``
| ``$``
|

see list of commands

|
| ``$ opd cmd``
| ``cfg,cmd,dne,dpl,err,exp,imp,log,mod,mre,nme,``
| ``now,pwd,rem,req,res,rss,srv,syn,tdo,thr,upt``
|


start a console

|
| ``$ opd -c``
| ``>``
|

start daemon

|
| ``$ opd``
| ``$``
|

start service
|

| ``$ opd -s``
| ``<runs until ctrl-c>``
|

**COMMANDS**

here is a list of available commands

|
| ``cmd`` - commands
| ``dpl`` - sets display items
| ``err`` - show errors
| ``exp`` - export opml (stdout)
| ``imp`` - import opml
| ``log`` - log text
| ``mre`` - display cached output
| ``now`` - show genocide stats
| ``pwd`` - sasl nickserv name/pass
| ``rem`` - removes a rss feed
| ``res`` - restore deleted feeds
| ``req`` - reconsider
| ``rss`` - add a feed
| ``syn`` - sync rss feeds
| ``tdo`` - add todo item
| ``thr`` - show running threads
| ``upt`` - show uptime
|

**CONFIGURATION**

irc

|
| ``$ opd cfg server=<server>``
| ``$ opd cfg channel=<channel>``
| ``$ opd cfg nick=<nick>``
|

sasl

|
| ``$ opd pwd <nsvnick> <nspass>``
| ``$ opd cfg password=<frompwd>``
|

rss

|
| ``$ opd rss <url>``
| ``$ opd dpl <url> <item1,item2>``
| ``$ opd rem <url>``
| ``$ opd nme <url> <name>``
|

opml

|
| ``$ opd exp``
| ``$ opd imp <filename>``
|

**SOURCE**

|
| source is at `https://github.com/bthate/opd  <https://github.com/bthate/opd>`_
|

**FILES**

|
| ``~/.opd``
| ``~/.local/bin/opd``
| ``~/.local/pipx/venvs/opd/*``
|

**AUTHOR**

|
| Bart Thate <``bthate@dds.nl``>
|

**COPYRIGHT**

|
| ``OPD`` is Public Domain.
|