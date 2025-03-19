# Copier-colle qui utilise la fonction de Windows (pour avoir la fenêtre classique qui s'ouvre)

import os

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\","/"):
    from Orange.widgets.orangecontrib.AAIT.utils import SimpleDialogQt
else:
    from orangecontrib.AAIT.utils import SimpleDialogQt
if os.name=='nt':
    import os.path

    from win32com.shell import shell, shellcon
    def win32_shellcopy(src, dest):
        """
        Copy files and directories using Windows shell.

        :param src: Path or a list of paths to copy. Filename portion of a path
                    (but not directory portion) can contain wildcards ``*`` and
                    ``?``.
        :param dst: destination directory.
        :returns: ``True`` if the operation completed successfully,
                  ``False`` if it was aborted by user (completed partially).
        :raises: ``WindowsError`` if anything went wrong. Typically, when source
                 file was not found.

        .. seealso:
            `SHFileperation on MSDN <http://msdn.microsoft.com/en-us/library/windows/desktop/bb762164(v=vs.85).aspx>`
        """
        if not os.path.exists(src):
            SimpleDialogQt.BoxError("Error file not exist : "+src)
            return
        if isinstance(src, str):
            src = os.path.abspath(src)
        else:  # iterable
            src = '\0'.join(os.path.abspath(path) for path in src)

        result, aborted = shell.SHFileOperation((
            0,
            shellcon.FO_COPY,
            src,
            os.path.abspath(dest),
            shellcon.FOF_NOCONFIRMMKDIR,  # flags
            None,
            None))

        if not aborted and result != 0:
            # Note: raising a WindowsError with correct error code is quite
            # difficult due to SHFileOperation historical idiosyncrasies.
            # Therefore we simply pass a message.
            raise WindowsError('SHFileOperation failed: 0x%08x' % result)

        return not aborted
