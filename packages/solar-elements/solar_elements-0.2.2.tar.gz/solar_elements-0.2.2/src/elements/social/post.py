import mimetypes

from elements import Event, Media, Picture, FileUpload, config
from elements.core.libs.utilities import slugify
from markdown import markdown

'''

=====================#
 //   8         8
//  ################
/   #              #
    #    Posts     #
    #              #
    ################

Posts are the bread-and-butter of the Solar
system. Most of the time, someone making a
contribution to the system will do so by
making a Post.

A Post contains parseable markdown in the
content body. It may also contain convenience
functions for linking media components
as tags of ['media', 'media/npc/test'] which
will be hydrated on load and exported in
accordance with NIP-92 (media attachments).

'''

class Post(Event):
    kind = 30023
    directory = 'posts'

    @classmethod
    def new(cls, **data):
        post = cls(**data)

        if post.title is None:
            post.tags.add(['d', str(int(post.created_at))])
        else:
            post.tags.add(['d', post.name])
            
        if post.tags.get('published_at') is None:
            post.tags.add(['published_at', str(int(post.created_at))])

        return post

    # Take a FileUpload and attach it to the post.
    def attach(self, upload : FileUpload, **kwargs):

        # A MIME Type is internet shorthand for telling about the
        # type of media file we're working with.
        mimetype, enc = mimetypes.guess_type(upload.filename, strict=False)

        # Basic metadata passed to the media constructor
        meta = { 'name': upload.filename, 'author': self.author }

        if mimetype.startswith('image'):
            dimensions = kwargs.get('dimensions')
            if dimensions:
                meta['dimensions'] = dimensions

            m = Picture.upload(upload, **meta)
            
            # If 'thumbnail' is passed, use the values to generate
            # a thumbnail of the attached image before saving.
            thumbnail = kwargs.get('thumbnail')
            if thumbnail:
                m.thumbnail(dimensions=thumbnail)
        else:
            m = Media.upload(upload, **meta)

        path = m.save()
        self.tags.add(['media', m.address])
        self.tags.add(m.inline)
    
        return m

    @property
    def imeta(self):
        if self._imeta is None:
            self._imeta = []
            imeta = self.tags.getall('imeta')

            for metadata in imeta:
                media_data = {}
                for tag in metadata:
                    k, v = tag.split(' ', 1)
                    media_data[k] = v

                self._imeta.append(media_data)

        return self._imeta

    def load_media(self):
        x = [i.get('x') for i in self.imeta]
        db = config.get('db')
        q = db.query({ "#x": x })
        self._media = q.events
        return self._media

    @property
    def media(self):
        if self._media is None:
            self.load_media()

        return self._media

    @property
    def name(self):
        title = self.tags.getfirst('title')
        if title:
            return slugify(title)
        else:
            return super().name

    # This is the property we use to parse
    # the post's markdown content into HTML
    #
    # It could stand to include a HTML sanitizing
    # library like 'bleach' to avoid XSS. I think
    # that this will work well enough though.
    @property
    def html(self):
        sanitized = self.content.replace('<', '&lt;').replace('>', '&gt;')
        return markdown(sanitized)

    def html_preview(self, number_of_chars=200):
        sanitized = self.content[:number_of_chars].replace('<', '&lt;').replace('>', '&gt;')
        return markdown(sanitized)

    def __getattr__(self, attr):
        return self.meta.get(attr)

config['kinds'][Post.kind] = Post
