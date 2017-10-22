from __future__ import absolute_import, print_function

import itertools
import logging
import os
import tempfile


import salt.ext.six as six

try:
    import grp
    import pwd
except ImportError:
    pass


HAS_YAMLLINT=True
try:
    from yamllint.config import YamlLintConfig, YamlLintConfigError
    from yamllint.linter import PROBLEM_LEVELS
    from yamllint import linter
except ImportError:
    HAS_YAMLLINT=False


# salty libs
import salt.utils
import salt.utils.find
import salt.utils.filebuffer
import salt.utils.files
import salt.utils.atomicfile
import salt.utils.url

log = logging.getLogger(__name__)

HASHES = [
            ['sha512',128],
            ['sha384',96],
            ['sha256',64],
            ['sha224',56],
            ['sha1',40],
            ['md5',32],
         ]





def __virtual__():
    return True


def _error(ret,err_msg):
    ret['result'] = False
    ret['comment'] = err_msg
    return ret


def _get_bkroot():
    return os.path.join(__salt__['config.get']('cachedir'), 'file_backup')


def __clean_tmp(sfn):
    if sfn.startswith(tempfile.gettempdir()):
        all_roots = itertools.chain.from_iterable(
                six.itervalues(__opts__['file_roots']))
        in_roots = any(sfn.startswith(root) for root in all_roots)
        if os.path.exists(sfn) and not in_roots:
            os.remove(sfn)


def render(
        template,
        source,
        saltenv='base',
        context=None,
        defaults=None,
        **kwargs):
    '''
    Define a simple render test to find out what the output of a render is on a minion

    template (required)
        template format
    
    source (required)
        managed source file

    source_hash (optional)
       hash of the source file

    context (optional)
       variables to add to the environment
  
    default (optional)
       default values for the context_dict
    '''
    sfn = ''
    if template and source:
        sfn = __salt__['cp.cache_file'](source,saltenv)
    if not sfn or not os.path.exists(sfn):
        return sfn, {}, 'Source file {0!r} not found'.format(source)
    if template in salt.utils.templates.TEMPLATE_REGISTRY:
        context_dict = defaults if defaults else {}
        if context:
            context_dict.update(context)
        data = salt.utils.templates.TEMPLATE_REGISTRY[template](
           sfn,
           source=source,
           saltenv=saltenv,
           context=context_dict,
           salt=__salt__,
           pillar=__pillar__,
           grains=__grains__,
           opts=__opts__,
           **kwargs)
    else:
        return sfn, {}, 'Specified template format {0} is not supported'.format(template)

    if data['result']:
       sfn = data['data']
    myfile=open(sfn)
    mydata=myfile.read()
    __clean_tmp(sfn)
    return mydata

def yamllint(
        template,
        source,
        saltenv='base',
        context=None,
        defaults=None,
        yamlconf=None, #'/root/.config/yamllint/config',
        **kwargs):
    '''
    lint the output after detecting a sucsessful render.

    template (required)
        template format

    source (required)
        managed source file

    source_hash (optional)
       hash of the source file

    context (optional)
       variables to add to the environment

    default (optional)
       default values for the context_dict
    '''
    if HAS_YAMLLINT:
        if yamlconf is not None:
            conf = YamlLintConfig(file=yamlconf)
        else:
            conf = YamlLintConfig('extends: relaxed')
        yaml_out = render(template,source,saltenv,context,defaults,**kwargs)
        problems = []
        for problem in linter.run(yaml_out,conf):
            problems.append({'line':problem.line,'column': problem.column, 'level': problem.level,'comment':problem.message})
        log.debug('my problems {0}'.format(problems))
        output = {"source":yaml_out,'problems':problems}
        return output
    else:
        return False, 'yamllint is not installed'

