import logging

HAS_YAMLLINT=True
try:
    from yamllint.config import YamlLintConfig, YamlLintConfigError
    from yamllint.linter import PROBLEM_LEVELS
    from yamllint import linter
except ImportError:
    HAS_YAMLLINT=False

log = logging.getLogger(__name__)

__virtualname__ = "lint"

def __virtual__():
    if HAS_YAMLLINT:
        return __virtualname__
    else:
        return (False,"YAMLLint Not installed")



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

def yaml(
        source,
        render=None,
        saltenv=None,
        yamlconf=None, #'/root/.config/yamllint/config',
        **kwargs):
    '''
    lint the output after detecting a sucsessful render.

    source (required)
        managed source file

    render (optional)
       The render options passed to slsutil.renderer other wise file is cached and loaded as stream

    saltenv (optional)
        the saltenv to use, defaults to minions enviroment or base if not set.

    yamlconf (optional)
        yamllint config file to use, if not set will default to a extended relaxed format.

    **kwargs (optional)
        Extra kwargs passed to slsutil.renderer if render is set other wise ignored.

    '''

    if yamlconf is not None:
        conf = YamlLintConfig(file=yamlconf)
    else:
        conf = YamlLintConfig('extends: relaxed')
    if saltenv is None:
        saltenv = __salt__.config.get('saltenv','base')
        if saltenv is None:
            saltenv = 'base'
        log.debug('saltenv is %s',saltenv)

    if render is None:
        cache = __salt__.cp.cache_file(source,saltenv)
        if cache == False:
            return (False,"Template was unable to be cached")
        yaml_stream = open(cache,"r")
        yaml_out = yaml_stream.read(-1)
    else:
        kwargs.update({"saltenv": saltenv })
        yaml_out = __salt__.slsutil.renderer(path=source,default_renderer=render, **kwargs)
    problems = []
    for problem in linter.run(yaml_out,conf):
        problems.append({'line':problem.line,'column': problem.column, 'level': problem.level,'comment':problem.message})
    log.debug('my problems %s',problems)
    output = {"source":yaml_out,'problems':problems}
    return output
