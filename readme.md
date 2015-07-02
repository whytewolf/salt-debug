crappy salt debug for template renders
======================================




_**do not use in a production enviroment**_
a simple to use debug module for seeing how a template looks to a minion

it is hacked together out of salts file module. not my original work but am using it to learn some python while I'm at it. 

pretty simple to use
just point it at the salt:// file you want it to render and tell it the template. 

such as `salt '*' debug.render source=salt://ntp/files/ntp.jinja template=jinja`
