from . import common
from conjure import juju
from conjure import utils
from conjure import controllers
from conjure.api.models import model_info
from conjure.app_config import app
from subprocess import CalledProcessError
import json
import os
import sys


def finish():
    return controllers.use('steps').render()


def render():
    info = model_info(app.current_model)
    # Set our provider type environment var so that it is
    # exposed in future processing tasks
    app.env['JUJU_PROVIDERTYPE'] = info['ProviderType']

    bundle = os.path.join(
        app.config['spell-dir'], 'bundle.yaml')
    bundle_scripts = os.path.join(
        app.config['spell-dir'], 'conjure/steps'
    )

    pre_exec_sh = os.path.join(bundle_scripts, '00_pre.sh')

    # Pre processing
    if os.path.isfile(pre_exec_sh) \
       and os.access(pre_exec_sh, os.X_OK):
        utils.info("Setting up prerequisites")
        try:
            sh = common.run_script(pre_exec_sh)
            if sh.returncode > 0:
                raise Exception(
                    "Cannot execute pre-processing script: {}".format(
                        sh.stderr.decode('utf8')))
            result = json.loads(sh.stdout.decode('utf8'))
            app.log.debug("pre execution done: {}".format(result))
        except CalledProcessError as e:
            utils.warning(
                "Failure in pre processor: {}".format(e))
            sys.exit(1)

    # juju deploy
    try:
        utils.info("Deploying charms")
        juju.deploy(bundle)
    except Exception as e:
        utils.error("Problem with deployment: {}".format(e))
        sys.exit(1)
    finish()