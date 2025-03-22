A A I
=====


**NAME**


``oaai`` - Open Authorative Artificial Intelligence (AAI)


**SYNOPSIS**


|
| ``oaai <cmd> [key=val] [key==val]``
| ``oaai -civw``
| ``oaai -d``
| ``oaai -s``
|


**DESCRIPTION**


``oaai`` has all you need to program a unix cli program, such as disk
perisistence for configuration files, event handler to handle the
client/server connection, deferred exception handling to not crash
on an error, etc.

``oaai`` contains all the python3 code to program objects in a functional
way. It provides a base Object class that has only dunder methods, all
methods are factored out into functions with the objects as the first
argument. It is called Object Programming (OP), OOP without the
oriented.

``oaai`` allows for easy json save//load to/from disk of objects. It
provides an "clean namespace" Object class that only has dunder
methods, so the namespace is not cluttered with method names. This
makes storing and reading to/from json possible.

``oaai`` is a demo bot, it can connect to IRC, fetch and display RSS
feeds, take todo notes, keep a shopping list and log text. You can
also copy/paste the service file and run it under systemd for 24/7
presence in a IRC channel.

``oaai`` is Public Domain.


**INSTALL**


installation is done with pipx

|
| ``$ pipx install oaai``
| ``$ pipx ensurepath``
|
| <new terminal>
|
| ``$ oaai srv > oaai.service``
| ``$ sudo mv oaai.service /etc/systemd/system/``
| ``$ sudo systemctl enable oaai --now``
|
| joins ``#oaai`` on localhost
|

if you run oaai locally from source you might need to add your
current directory to sys.path

|
| ``export PYTHONPATH="."``
|


**USAGE**

use ``oaai`` to control the program, default it does nothing

|
| ``$ oaai``
| ``$``
|

see list of commands

|
| ``$ oaai cmd``
| ``cfg,cmd,dne,dpl,err,exp,imp,log,mod,mre,nme,``
| ``pwd,rem,req,res,rss,srv,syn,tdo,thr,upt``
|

start daemon

|
| ``$ oaai -d``
| ``$``
|

start service

|
| ``$ oaai -s``
| ``<runs until ctrl-c>``
|


**COMMANDS**


here is a list of available commands

|
| ``cfg`` - irc configuration
| ``cmd`` - commands
| ``dpl`` - sets display items
| ``err`` - show errors
| ``exp`` - export opml (stdout)
| ``imp`` - import opml
| ``log`` - log text
| ``mre`` - display cached output
| ``pwd`` - sasl nickserv name/pass
| ``rem`` - removes a rss feed
| ``res`` - restore deleted feeds
| ``req`` - reconsider
| ``rss`` - add a feed
| ``syn`` - sync rss feeds
| ``thr`` - show running threads
| ``upt`` - show uptime
|


**CONFIGURATION**


irc

|
| ``$ oaai cfg server=<server>``
| ``$ oaai cfg channel=<channel>``
| ``$ oaai cfg nick=<nick>``
|

sasl

|
| ``$ oaai pwd <nsvnick> <nspass>``
| ``$ oaai cfg password=<frompwd>``
|

rss

|
| ``$ oaai rss <url>``
| ``$ oaai dpl <url> <item1,item2>``
| ``$ oaai rem <url>``
| ``$ oaai nme <url> <name>``
|

opml

|
| ``$ oaai exp``
| ``$ oaai imp <filename>``
|


**PROGRAMMING**


``oaai`` runs it's modules in the package, to add your own command  edit
a file in oaai/modules/hello.py and add the following for ``hello world``

::

    def hello(event):
        event.reply("hello world !!")


save this and run

|
| ``$ bin/oaai tbl > oaai/modules/tbl.py``
| ``$ pipx install . --force``
|

program can execute the ``hello`` command now.

|
| ``$ oaai hello``
| ``hello world !!``
|


**FILES**

|
| ``~/.oaai``
| ``~/.local/bin/oaai``
| ``~/.local/pipx/venvs/oaai/*``
|

**AUTHOR**

|
| ``Bart Thate`` <``bthate@dds.nl``>
|

**COPYRIGHT**

|
| ``oaai`` is Public Domain.
|