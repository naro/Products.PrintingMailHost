import os
import email.Parser
from datetime import datetime
try:
    from email.message import Message
except ImportError:
    from email import Message
from base64 import decodestring

from AccessControl import ClassSecurityInfo
from Products.PrintingMailHost import LOG
from Products.MailHost.MailHost import MailBase
from StringIO import StringIO

PATCH_PREFIX = '_monkey_'
SAVETO = os.environ.get('PRINTING_MAILHOST_SAVETO', None)

__refresh_module__ = 0


def monkeyPatch(originalClass, patchingClass):
    """Monkey patch original class with attributes from new class
       (Swiped from SpeedPack -- thanks, Christian Heimes!)

    * Takes all attributes and methods except __doc__ and __module__
      from patching class
    * Safes original attributes as _monkey_name
    * Overwrites/adds these attributes in original class
    """
    for name, newAttr in patchingClass.__dict__.items():
        # don't overwrite doc or module informations
        if name not in ('__doc__', '__module__'):
            # safe the old attribute as __monkey_name if exists
            # __dict__ doesn't show inherited attributes :/
            orig = getattr(originalClass, name, None)
            if orig:
                stored_orig_name = PATCH_PREFIX + name
                stored_orig = getattr(originalClass, stored_orig_name, None)
                # don't double-patch on refresh!
                if stored_orig is None:
                    setattr(originalClass, stored_orig_name, orig)
            # overwrite or add the new attribute
            setattr(originalClass, name, newAttr)


class PrintingMailHost:
    """MailHost which prints to output."""
    security = ClassSecurityInfo()

    security.declarePrivate('_send')

    def _send(self, mfrom, mto, messageText, debug=False, immediate=False):
        """Send the message."""
        if isinstance(messageText, str):
            messageText = email.Parser.Parser().parsestr(messageText)
        base64_note = ""
        out = StringIO()
        print >> out, ""
        print >> out, " ---- sending mail ---- "
        print >> out, "From:", mfrom
        print >> out, "To:", mto
        if messageText.get('Content-Transfer-Encoding') == 'base64':
            base64_note = "NOTE: The email payload was originally base64 " \
                          "encoded.  It was decoded for debug purposes."
            body = messageText.get_payload()
            if isinstance(body, list):
                for attachment in body:
                    if isinstance(attachment, Message):
                        messageText.set_payload(
                            decodestring(attachment.get_payload()))
                        break
                    elif isinstance(attachment, str):
                        messageText.set_payload(decodestring(attachment))
                        break
            else:
                messageText.set_payload(decodestring(body))

        print >> out, messageText
        print >> out, " ---- done ---- "
        print >> out, ""
        if base64_note:
            print >> out, base64_note
            print >> out, ""
        value = out.getvalue()
        LOG.info(value)
        if SAVETO and os.path.isdir(SAVETO) and os.access(SAVETO, os.W_OK):
            now = datetime.now().strftime('%Y%m%d-%H%M%S-%f.log')
            fname = os.path.join(SAVETO, now)
            open(fname, 'w').write(value)

if SAVETO is not None:
    if os.path.isdir(SAVETO) and os.access(SAVETO, os.W_OK):
        saveto_text = '\nE-mails will be saved to {0}\n'.format(SAVETO)
    elif os.path.isdir(SAVETO) and not os.access(SAVETO, os.W_OK):
        saveto_text = "\nE-mails can't be saved to {0}. The directory is not writeable.\n".format(SAVETO)
    elif not os.path.isdir(SAVETO):
        saveto_text = "\nE-mails can't be saved to {0}. The directory does not exist.\n".format(SAVETO)
else:
    saveto_text = ''


LOG.warn("""

******************************************************************************

Monkey patching MailHosts to print emails to the terminal instead of
sending them.

NO MAIL WILL BE SENT FROM ZOPE AT ALL!
%s
Turn off debug mode or remove PrintingMailHost from the Products
directory to turn this off.

******************************************************************************
""", saveto_text)

monkeyPatch(MailBase, PrintingMailHost)

# Patch some other mail host implementations.
try:
    from Products.SecureMailHost.SecureMailHost import SecureMailBase
except ImportError:
    pass
else:
    monkeyPatch(SecureMailBase, PrintingMailHost)

try:
    from Products.MaildropHost.MaildropHost import MaildropHost
except ImportError:
    pass
else:
    monkeyPatch(MaildropHost, PrintingMailHost)

try:
    from Products.SecureMaildropHost.SecureMaildropHost import \
        SecureMaildropHost
except ImportError:
    pass
else:
    monkeyPatch(SecureMaildropHost, PrintingMailHost)
