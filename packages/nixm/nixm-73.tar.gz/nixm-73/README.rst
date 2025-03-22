N I X M
=======


**NAME**


``nixm`` - NIXM


**SYNOPSIS**


|
| ``nixm <cmd> [key=val] [key==val]``
| ``nixm -cviw``
| ``nixm -d`` 
| ``nixm -s``
|

**DESCRIPTION**


``NIXM`` has all you need to program a unix cli program, such as disk
perisistence for configuration files, event handler to handle the
client/server connection, deferred exception handling to not crash
on an error, etc.

``NIXM`` contains all the python3 code to program objects in a functional
way. It provides a base Object class that has only dunder methods, all
methods are factored out into functions with the objects as the first
argument. It is called Object Programming (OP), OOP without the
oriented.

``NIXM`` allows for easy json save//load to/from disk of objects. It
provides an "clean namespace" Object class that only has dunder
methods, so the namespace is not cluttered with method names. This
makes storing and reading to/from json possible.

``NIXM`` is a demo bot, it can connect to IRC, fetch and display RSS
feeds, take todo notes, keep a shopping list and log text. You can
also copy/paste the service file and run it under systemd for 24/7
presence in a IRC channel.

``NIXM`` is Public Domain.


**INSTALL**


installation is done with pipx

|
| ``$ pipx install nixm``
| ``$ pipx ensurepath``
|
| <new terminal>
|
| ``$ nixm srv > nixm.service``
| ``$ sudo mv nixm.service /etc/systemd/system/``
| ``$ sudo systemctl enable nixm --now``
|
| joins ``#nixm`` on localhost
|


**USAGE**


use ``nixm`` to control the program, default it does nothing

|
| ``$ nixm``
| ``$``
|

see list of commands

|
| ``$ nixm cmd``
| ``cfg,cmd,dne,dpl,err,exp,imp,log,mod,mre,nme,``
| ``pwd,rem,req,res,rss,srv,syn,tdo,thr,upt``
|

start daemon

|
| ``$ nixm -d``
| ``$``
|

start service

|
| ``$ nixm -s``
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
| ``tdo`` - add todo item
| ``thr`` - show running threads
| ``upt`` - show uptime
|

**CONFIGURATION**


irc

|
| ``$ nixm cfg server=<server>``
| ``$ nixm cfg channel=<channel>``
| ``$ nixm cfg nick=<nick>``
|

sasl

|
| ``$ nixm pwd <nsvnick> <nspass>``
| ``$ nixm cfg password=<frompwd>``
|

rss

|
| ``$ nixm rss <url>``
| ``$ nixm dpl <url> <item1,item2>``
| ``$ nixm rem <url>``
| ``$ nixm nme <url> <name>``
|

opml

|
| ``$ nixm exp``
| ``$ nixm imp <filename>``
|


**PROGRAMMING**


``nixm`` runs it's modules in the package edit a file in nixm/modules/<name>.py
and add the following for ``hello world``

::

    def hello(event):
        event.reply("hello world !!")


save this and import your filename. Add your module to nixm/modules/face.py
and ``nixm`` can execute the ``hello`` command now.

|
| ``$ nixm hello``
| ``hello world !!``
|

commands run in their own thread, errors are deferred to not have loops
blocking/breaking on exception and can contain your own written python3
code, see the nixt/modules directory for examples.


**FILES**

|
| ``~/.nixm``
| ``~/.local/bin/nixm``
| ``~/.local/pipx/venvs/nixm/*``
|

**AUTHOR**

|
| ``Bart Thate`` <``bthate@dds.nl``>
|

**COPYRIGHT**

|
| ``NIXM`` is Public Domain.
|