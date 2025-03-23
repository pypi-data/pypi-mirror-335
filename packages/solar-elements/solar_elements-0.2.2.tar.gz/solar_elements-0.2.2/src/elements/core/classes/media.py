import os
import hashlib
import mimetypes
from pathlib import Path
from io import BytesIO
from base64 import b64encode
from urllib.request import urlopen
from PIL import Image, ImageOps, ExifTags

#from elements.core import Config
#from elements.core.storage import store, link
#from elements.notes import Note

from .event import Event
from .config import config
from .solar_path import SolarPath

'''
Media is an element that deals with file uploads of binary data, usually
in audio, video, and image formats. 

It's a key component for adding visual media to the Solar system,
through avatars and post images.
'''

class Media(Event):
    namespace = config.get('storage.namespace')
    directory = "media"
    kind = 1063

    # Upload receives a FileUpload class from bottle, and saves
    # it to storage. It also signs if the session is passed.
    @classmethod
    def upload(cls, up, session=None, **metadata):
        up.file.seek(0)
        fbytes = up.file.read()
        size = len(fbytes)
        sha256 = hashlib.sha256(fbytes).hexdigest()

        data = {
            **metadata,
            'm': mimetypes.guess_type(up.filename, strict=False)[0],
            'x': sha256,
            'size': str(size),
            'd': up.filename
        }

        media = cls(**data)
        media._file = up.file

        if session:
            media._author = session.account

        # Make sure we have a folder to save it to
        folder = media.filepath.fs.parent
        folder.mkdir(exist_ok=True, parents=True)

        # Write the file!
        with open(folder / up.filename, "wb") as f:
            up.file.seek(0)
            up.save(f)

        host = config.get('storage.address')
        author = session.account.name if session else config.get('solar.subspace')
        path = media.filepath
        media.tags.add(['url', f'{host}{author}/{path}'])

        if session:
            media.sign(session)

        return media

    @property
    def file(self):
        if self._file:
            return self._file
        else:
            # Pass for now
            return None

    @property
    def filepath(self):
        path = SolarPath(self.name, namespace=self.namespace, subspace=None)
        if self.author:
            path.subspace = self.author.name

        return path

    @property
    def static_url(self):
        return self.tags.getfirst('url')

    # Shorthand for exporting the media as a standard tag
    @property
    def inline(self):
        inline_metadata = ['imeta']
        for tag in self.tags.flatten():
            # Here, we use a 'list comprehension' to cast everything
            # as a string before joining into a space-separated list
            inline_metadata.append(' '.join(str(t) for t in tag))

        return inline_metadata

    # Return the thumbnail if it exists, or the full img
    @property
    def preview(self):
        return self.tags.getfirst('thumb') or self.tags.getfirst('image') or self.tags.getfirst('url')

config['kinds'][Media.kind] = Media

# Pillow is a massive library (11MB!) to integrate for a small task.
# I have considered using ImageMagick bindings but the implementation
# I tried (Wand) was clunkier than I would like. 

class Picture(Media):

    # Uploading a picture is inherently kind of complex because
    # we might need to resize it, transpose it etc. We handle that
    # here before passing it to the regular Media upload function.

    @classmethod
    def upload(cls, up, session=None, **metadata):

        # By default, we save all uploads as JPEGs with
        # a max dimension of 800x600 unless otherwise
        # specified.
        dimensions = metadata.pop('dimensions', (800,600))
        image_format = metadata.pop('format', 'JPEG')

        # Hash the file before transforming it
        up.file.seek(0)
        fbytes = up.file.read()
        metadata['ox'] = hashlib.sha256(fbytes).hexdigest()
        up.file.seek(0)

        # This is the buffer that will hold the new image
        file_buffer = BytesIO()

        # Apply transformations to the image
        with Image.open(up.file) as img:

            # This is needed to flatten .png files to JPEG
            if image_format != "PNG":
                img = img.convert('RGB')

            try:
                img = ImageOps.exif_transpose(img) # Rotate according to exif data
            except ZeroDivisionError as e:
                # This covers a bug with Pillow
                exif = img.getexif()
                orientation = exif[ExifTags.Base.Orientation]
                if orientation == 2:
                    img = ImageOps.mirror()
                elif orientation == 3:
                    img = img.rotate(180)
                elif orientation == 4:
                    img = ImageOps.flip()
                elif orientation == 5:
                    img = ImageOps.mirror().rotate(90, expand=True)
                elif orientation == 6:
                    img = img.rotate(270, expand=True)
                elif orientation == 7:
                    img = ImageOps.mirror().rotate(270, expand=True)
                elif orientation == 8:
                    img = img.rotate(90, expand=True)

            write_dimensions = (min(dimensions[0], img.size[0]), min(dimensions[1], img.size[1]))
            metadata['dim'] = f'{write_dimensions[0]}x{write_dimensions[1]}'
            img = ImageOps.contain(img, write_dimensions, Image.LANCZOS)

            # Write the modified image to the file_buffer
            img.save(file_buffer, format=image_format)

            # Afterwards, we still need to figure out what the name is.
        
            # We look for a value 'name' in the metadata, if it doesn't 
            # exist then we use the existing name for the file.
            basename = metadata.pop('name', os.path.basename(up.filename))

            # We only support these two formats right now. Might be
            # worthwhile to add GIFs / APNGs
            if image_format == "PNG":
                format_suffix = '.png'
            else:
                format_suffix = '.jpeg'

            # Build the name and save it.
            img_name = os.path.splitext(basename)[0] + format_suffix
            file_buffer.name = img_name

        # Save the modified file buffer and continue
        up.file = file_buffer

        return super().upload(up, session, **metadata)

    # 
    def thumbnail(self, **kwargs):
        dimensions = kwargs.get('dimensions', (80,60))
        path = kwargs.get('path', None)
        with Image.open(self.file) as img:
            file_buffer = BytesIO()
            img = ImageOps.fit(img, dimensions, Image.LANCZOS)
            img.save(file_buffer, format="PNG")
            file_buffer.name = self.file.name

            # Make sure we have a folder to save it to
            thumbnails_folder = self.filepath.fs.parent / 'thumbs'
            thumbnails_folder.mkdir(exist_ok=True, parents=True)
            path = thumbnails_folder / file_buffer.name

            # Write the file!
            with open(thumbnails_folder / file_buffer.name, "wb") as f:
                file_buffer.seek(0)
                f.write(file_buffer.getbuffer())
                #img.save(f)

            host = config.get('storage.address')
            author = self.author.name

            path = self.filepath.parent / 'thumbs' / file_buffer.name
            self.tags.add(['thumb', f'{host}{author}/{path}'])

            ## We may need this.
            #b64_image = b64encode(file_buffer.getvalue()).decode()
            #thumbnail = f'data:image/png;charset=utf-8;base64,{b64_image}'
            #return thumbnail
            return None

