crappy salt debug for template renders
======================================

a simple to use debug module for seeing how a template looks to a minion

it is hacked together out of salts file module. not my original work but am using it to learn some python while I'm at it. 

pretty simple to use
put salt where it can bee seen from the root file_dir
then run salt '\*' saltutil.sync_all
or salt '\*' saltutil.sync_modules


then just point it at the salt:// file you want it to render and tell it the template. 

such as `salt '*' debug.render source=salt://ntp/files/ntp.jinja template=jinja`

so far Two functions exist
--------------------------

## debug.render

```
debug.render
  inputs:
    template: The template type. aka jinja, maco, py, pydsl, ect. 
    source: the location of the file to rendered. so far only tested with salt:// locations
    saltenv: (optional, default "base") the enviroment for the source above
    context: just like file.* this is a context dict for filleing in extra variables.
    defaults: same as context
  output:
    either the rendered output, or jinja errors
```

## debug.yamllint

```
debug.yamllint
  inputs:
    template: The template type. aka jinja, maco, py, pydsl, ect. 
    source: the location of the file to rendered. so far only tested with salt:// locations
    saltenv: (optional, default "base") the enviroment for the source above
    context: just like file.* this is a context dict for filleing in extra variables.
    defaults: same as context
    yamlconf: if you don't want to use the default of relaxed the yamllint config file location.
  output:
    a 2 part dict of the output. part 1 is problems. a list of yaml errors detected in the output of a debug.render performed on the code.
    part 2 source. the output from the debug.render performed
```

