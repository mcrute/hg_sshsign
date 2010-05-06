# vim: set filencoding=utf-8
"""
SSH Key Signing

@author: Mike Crute (mcrute@ag.com)
@organization: American Greetings Interactive
@date: May 03, 2010
"""


import os
import binascii

from hgsshsign._meta import __version__
from hgsshsign.sshagent import SSHAgent

from mercurial.i18n import _
from mercurial import util, commands, match
from mercurial import node as hgnode


class SSHAuthority(object):

    @classmethod
    def from_ui(cls, ui):
        import hgsshsign.keys as keys
        from hgsshsign.keymanifest import KeyManifest

        public_key = absolute_path(ui.config("sshsign", "public_key"))
        public_key = keys.PublicKey.from_file(public_key)

        manifest_file = ui.config("sshsign", "manifest_file")
        if manifest_file:
            manifest = KeyManifest.from_file(absolute_path(manifest_file))
        else:
            manifest = None
            ui.write(_("No key manifest set. You will not be able to verify"
                        " signatures.\n"))

        private_key = ui.config("sshsign", "private_key", None)
        agent_socket = os.environ.get(SSHAgent.AGENT_SOCK_NAME)
        if private_key:
            private_key = keys.load_private_key(absolute_path(private_key))
        elif agent_socket:
            private_key = SSHAgent(agent_socket, key=public_key.blob)
        else:
            raise util.Abort(_("No private key set and no agent running."))

        return cls(public_key, manifest, private_key)

    def __init__(self, public_key, key_manifest=None, private_key=None):
        self.public_key = public_key
        self.key_manifest = key_manifest
        self.private_key = private_key

    def verify(self, data, signature, whom):
        try:
            key = self.key_manifest[whom] # XXX: More elegant error handling.
        except KeyError:
            raise util.Abort(_("No key found for %s" % whom))

        return key.verify(data, signature)

    def sign(self, data):
        import hgsshsign.keys as keys

        return keys.sign_like_agent(data, self.private_key)


def node2txt(repo, node, ver):
    """map a manifest into some text"""
    if ver != "0":
        raise util.Abort(_("unknown signature version"))

    return "%s\n" % hgnode.hex(node)


def absolute_path(path):
    path = os.path.expandvars(path)
    return os.path.expanduser(path)


def sign(ui, repo, *revs, **opts):
    """add a signature for the current or given revision

    If no revision is given, the parent of the working directory is used,
    or tip if no revision is checked out.

    See 'hg help dates' for a list of formats valid for -d/--date.
    """

    mygpg = SSHAuthority.from_ui(ui)
    sigver = "0"
    sigmessage = ""

    date = opts.get('date')
    if date:
        opts['date'] = util.parsedate(date)

    if revs:
        nodes = [repo.lookup(n) for n in revs]
    else:
        nodes = [node for node in repo.dirstate.parents()
                 if node != hgnode.nullid]
        if len(nodes) > 1:
            raise util.Abort(_('uncommitted merge - please provide a '
                               'specific revision'))
        if not nodes:
            nodes = [repo.changelog.tip()]

    for n in nodes:
        hexnode = hgnode.hex(n)
        ui.write(_("Signing %d:%s\n") % (repo.changelog.rev(n),
                                         hgnode.short(n)))
        # build data
        data = node2txt(repo, n, sigver)
        sig = mygpg.sign(data)
        if not sig:
            raise util.Abort(_("Error while signing"))
        sig = binascii.b2a_base64(sig)
        sig = sig.replace("\n", "")
        sigmessage += "%s %s %s\n" % (hexnode, sigver, sig)

    # write it
    if opts['local']:
        repo.opener("localsigs", "ab").write(sigmessage)
        return

    msigs = match.exact(repo.root, '', ['.hgsigs'])
    s = repo.status(match=msigs, unknown=True, ignored=True)[:6]
    if util.any(s) and not opts["force"]:
        raise util.Abort(_("working copy of .hgsigs is changed "
                           "(please commit .hgsigs manually "
                           "or use --force)"))

    repo.wfile(".hgsigs", "ab").write(sigmessage)

    if '.hgsigs' not in repo.dirstate:
        repo.add([".hgsigs"])

    if opts["no_commit"]:
        return

    message = opts['message']
    if not message:
        # we don't translate commit messages
        message = "\n".join(["Added signature for changeset %s"
                             % hgnode.short(n)
                             for n in nodes])
    try:
        repo.commit(message, opts['user'], opts['date'], match=msigs)
    except ValueError, inst:
        raise util.Abort(str(inst))


cmdtable = {
    "sshsign":
        (sign,
         [('l', 'local', None, _('make the signature local')),
          ('f', 'force', None, _('sign even if the sigfile is modified')),
          ('', 'no-commit', None, _('do not commit the sigfile after signing')),
          ('m', 'message', '', _('commit message')),
         ] + commands.commitopts2,
         _('hg sign [OPTION]... [REVISION]...')),
}
