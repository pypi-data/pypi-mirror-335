""" Edo File Wrapper """
# --------------------------------------------------------------------------------------------- #

import base64
import logging
import mimetypes
import os
import shutil

# --------------------------------------------------------------------------------------------- #

import magic

# --------------------------------------------------------------------------------------------- #

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------------------------- #


class File:
    """ File class """

    # ----------------------------------------------------------------------------------------- #

    def __init__(self, filepath: str = None, filename: str = None, content: bytes = None,
                 mime: str = None, fetch: bool = False):
        """ Creates a File object. """

        # 1. ...
        self.filepath = filepath
        self.filename = filename

        # 2. ...
        self.mime = mime
        self.content = content

        # 3. ...
        self.fetch = fetch

        # 4. ...
        self._size = None
        self._validate()

    # ----------------------------------------------------------------------------------------- #

    @property
    def size(self):
        """ Returns the size of the file content. """
        return len(self.content) if self.content else self._size

    # ----------------------------------------------------------------------------------------- #

    def __str__(self):
        return f"({self.mime}): {self.filename}. {File.get_size(self.size)}. ({self._data_type()})"

    # ----------------------------------------------------------------------------------------- #

    def __repr__(self):
        return f"({File}):({self.mime}):({self.filename}):({self.size})"

    # ----------------------------------------------------------------------------------------- #

    def get_content(self):
        """ Get's the file content as binary. """

        # 1. ...
        if not self.content and self.filepath and os.path.isfile(self.filepath):

            # 1.1 ...
            with open(self.filepath, 'rb') as file:
                self.content = file.read()

        # 2. ...
        return self.content

    # ----------------------------------------------------------------------------------------- #

    def to_dict(self):
        """ Converts to dictionary. """

        # 1. ...
        self._validate()

        # 2. ...
        return {
            "filepath": self.filepath,
            "filename": self.filename,
            "mime": self.mime,
            "size": self.size,
            "fetch": self.fetch,
            "content": self._encode_content()
        }

    # ----------------------------------------------------------------------------------------- #

    @classmethod
    def from_dict(cls, data: dict):
        """ Loads from dictionary. """

        # 1. ...
        obj = None
        if data:

            # 1.1 ...
            filepath = data["filepath"] if "filepath" in data else None
            filename = data["filename"] if "filename" in data else None

            # 1.2 ...
            mime = data["mime"] if "mime" in data else None
            fetch = data["fetch"] if "fetch" in data else None

            # 1.3 ...
            content = data["content"] if "content" in data else None
            content = File._decode_content(content)

            # 1.4 ...
            obj = cls(
                filepath = filepath,
                filename = filename,
                content = content,
                mime = mime,
                fetch = fetch
            )

            # 1.5 ...
            obj._validate()

        # 2. ...
        return obj

    # ----------------------------------------------------------------------------------------- #

    def write(self, outpath: str = None, verbose: bool = True):
        """
        Writes the file content to disk.
            - If 'content' is available, it writes the content to 'outpath'.
            - If 'content' is not available but 'filepath' is, 
                it copies the file from 'filepath' to 'outpath'.
        """

        # 1. ...
        outpath = outpath.strip() if outpath else (self.filepath.strip() if self.filepath else None)
        if outpath:

            # 1.1 ...
            out_dir = os.path.dirname(outpath)

            # 1.2 ...
            if not os.path.exists(out_dir):
                os.makedirs(out_dir, exist_ok=True)

            # 1.3 ...
            if os.path.isdir(outpath):
                outpath = os.path.join(outpath, self.filename)

            # 1.4 ...
            if (self.content and ((outpath != self.filepath) or (self.filepath and
                not os.path.exists(self.filepath)))):

                # 2.1 ...
                with open(outpath, 'wb') as f:
                    f.write(self.content)

            # 1.5 ...
            elif self.filepath and os.path.exists(self.filepath):

                # 1.1 ...
                if outpath != self.filepath:
                    shutil.copy(self.filepath, outpath)

            # 1.6 ...
            else:
                raise FileNotFoundError(f"Source file not found: {self.filepath}")

            # 1.7 ...
            if verbose:
                logger.info("File.write(): data saved at %s", outpath)

    # ----------------------------------------------------------------------------------------- #

    def _data_type(self):
        """ 
        Returns the load type at export:
            If should load the file content to export. (data)
            If should keep only the file path to export. (link)
        """

        # 1. ...
        return "data" if self.fetch else "link"

    # ----------------------------------------------------------------------------------------- #

    def _validate(self):
        """ Validates inputs fields. Keeps content lazy until necessary. """

        # 1. ...
        if self.filepath:
            self.filepath = self.filepath.strip()

            # 1.1 ...
            if not self.filename:
                self.filename = os.path.basename(self.filepath)

            # 1.2 ...
            if not self._size and not self.content and os.path.isfile(self.filepath):
                self._size = os.path.getsize(self.filepath)

            # 1.3 ...
            if not self.mime:
                self.mime = File.get_mime_from_path(self.filepath)

        # 2. ...
        if self.content and not self.mime:
            self.mime = File.get_mime_from_content(self.content)

        # 3. ...
        if self.filename and not self.mime:
            self.mime = File.get_mime_from_name(self.filename)

        # 4. ...
        if not self.mime:
            self.mime = "application/octet-stream"

        # 5. ...
        if self.filename:
            self.filename = self.filename.strip()

        # 6. ...
        if self.mime:
            self.mime = self.mime.strip()

    # ----------------------------------------------------------------------------------------- #

    def _encode_content(self):
        """ Encodes the content. """

        # 1. ...
        encoded_content = None
        if self.fetch or (not self.filepath and self.content):

            # 1.1 ...
            content = self.get_content()
            if content:

                # 2.1 ...
                encoded_content = base64.b64encode(content).decode('utf-8')

        # 2. ...
        return encoded_content

    # ----------------------------------------------------------------------------------------- #

    @staticmethod
    def _decode_content(content: str):
        """ Decodes the content. """

        # 1. ...
        decoded_content = None
        if content:

            # 1.1 ...
            decoded_content = base64.b64decode(content)

        # 2. ...
        return decoded_content

    # ----------------------------------------------------------------------------------------- #

    @staticmethod
    def get_mime_from_name(filename: str):
        """
        Returns the mime of a filename.
        """

        # 1. ...
        return mimetypes.guess_type(filename)[0] or "application/octet-stream"

    # ----------------------------------------------------------------------------------------- #

    @staticmethod
    def get_mime_from_path(filepath: str):
        """
        Returns the mime of a filepath.
        """

        # 1. ...
        mime = magic.Magic(mime=True)
        return mime.from_file(filepath)

    # ----------------------------------------------------------------------------------------- #

    @staticmethod
    def get_mime_from_content(content: bytes):
        """
        Returns the mime of the content.
        """

        # 1. ...
        mime = magic.Magic(mime=True)
        return mime.from_buffer(content)

    # ----------------------------------------------------------------------------------------- #

    @staticmethod
    def get_size(bytes_size: int) -> str:
        """
        Takes the size of a file in bytes and returns a formatted string
        with the appropriate size unit (KB, MB, GB, etc.).
        """

        # 1. ...
        output = None
        if bytes_size and (bytes_size > 0):

            # 1.1 Units...
            units = ["bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]

            # 1.2 Determine which unit to use...
            unit_index = 0
            while (bytes_size >= 1024) and (unit_index < len(units) - 1):

                # 2.1 ...
                bytes_size /= 1024.0
                unit_index += 1

            # 1.3 Formats...
            output = f"{bytes_size:.1f} {units[unit_index]}"

        # 2. ...
        return output

    # ----------------------------------------------------------------------------------------- #


# --------------------------------------------------------------------------------------------- #
