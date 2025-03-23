# Copyright (c) 2021-2024 Datalayer, Inc.
#
# Datalayer License

"""Configuration for the Development Jupyter server."""

import os

from pathlib import Path

c.ServerApp.answer_yes = True

#################
# Datalayer
#################

c.DatalayerExtensionApp.run_url = os.environ.get("DATALAYER_RUN_URL", None)
c.DatalayerExtensionApp.white_label = bool(os.environ.get("DATALAYER_WHITE_LABEL", None))
c.DatalayerExtensionApp.Launcher.category = "Datalayer"
c.DatalayerExtensionApp.Launcher.name = "Datalayer Runtimes"
c.DatalayerExtensionApp.Launcher.rank = 0
c.DatalayerExtensionApp.Launcher.icon_svg_url = "https://raw.githubusercontent.com/datalayer/icons/main/svg/data1/jupyter-base.svg"
c.DatalayerExtensionApp.Brand.name = "Datalayer"
c.DatalayerExtensionApp.Brand.about = "Accelerated and Trusted Jupyter"
c.DatalayerExtensionApp.Brand.docs_url = "https://docs.datalayer.io"
c.DatalayerExtensionApp.Brand.support_url = "https://datalayer.io/support"
c.DatalayerExtensionApp.Brand.pricing_url = "https://datalayer.io/pricing"
c.DatalayerExtensionApp.Brand.terms_url = "https://datalayer.io/terms"
c.DatalayerExtensionApp.Brand.privacy_url = "https://datalayer.io/privacy"

#################
# Logging
#################

c.ServerApp.log_level = 'INFO'

#################
# Network
#################

c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8686
c.ServerApp.port_retries = 0

#################
# Browser
#################

c.ServerApp.open_browser = False

#################
# Terminal
#################

c.ServerApp.terminals_enabled = True

#################
# Authentication
#################

c.IdentityProvider.token = '60c1661cc408f978c309d04157af55c9588ff9557c9380e4fb50785750703da6'

#################
# Security
#################

c.ServerApp.disable_check_xsrf = False
ORIGIN = '*'
# c.ServerApp.allow_origin = ORIGIN
c.ServerApp.allow_origin_pat = '.*'
c.ServerApp.allow_credentials = True
c.ServerApp.tornado_settings = {
  'headers': {
#    'Access-Control-Allow-Origin': ORIGIN,
    'Access-Control-Allow-Methods': '*',
    'Access-Control-Allow-Headers': 'Accept, Accept-Encoding, Accept-Language, Authorization, Cache-Control, Connection, Content-Type, Host, Origin, Pragma, Referer, sec-ch-ua, sec-ch-ua-mobile, sec-ch-ua-platform, Sec-Fetch-Dest, Sec-Fetch-Mode, Sec-Fetch-Site, Upgrade, User-Agent, X-XSRFToken, X-Datalayer, Expires',
    'Access-Control-Allow-Credentials': 'true',
    'Content-Security-Policy': f"frame-ancestors 'self' {ORIGIN} ",
  },
  'cookie_options': {
    'SameSite': 'None',
    'Secure': True
  }
}
c.IdentityProvider.cookie_options = {
  "SameSite": "None",
  "Secure": True,
}

#################
# Server Extensions
#################

c.ServerApp.jpserver_extensions = {
    'datalayer': True,
    'jupyterlab': True,
    'jupyter_iam': True,
    'jupyter_kernels': True,
#    'jupyter_react': True,
    'jupyter_server_terminals': True,
}

#################
# Contents
#################

# c.FileContentsManager.delete_to_trash = False
content_dir_path = Path(__file__).parent / '..' / 'notebooks'
content_dir = content_dir_path.resolve().as_posix()
c.ServerApp.root_dir = content_dir
c.ServerApp.preferred_dir = content_dir

c.ContentsManager.allow_hidden = True

#################
# URLs
#################

c.ServerApp.base_url = '/api/jupyter-server'
c.ServerApp.default_url = '/api/jupyter-server/lab'

#################
# Kernel
#################

# See
# https://github.com/jupyterlab/jupyterlab/pull/11841
# https://github.com/jupyter-server/jupyter_server/pull/657
c.ZMQChannelsWebsocketConnection.kernel_ws_protocol = None # None or ''

#################
# JupyterLab
#################

c.LabApp.collaborative = False


#################
# NbGrader
#################

c.CourseDirectory.root = content_dir
c.CourseDirectory.course_id = "course-1"
c.Exchange.root = content_dir + "/courses_exchange"
