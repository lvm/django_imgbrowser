import mimetypes
import os
from django.conf import settings

try:
    import Image
except ImportError:
    try:
        from PIL import Image
        _imaging = Image.core
    except ImportError as e:
        print "Install: PIL or Pillow\n%s" % e

def guess_extension_by_filename(filename):
    try:
        return os.path.splitext(filename)[1]
    except ValueError as err:
        print "Something's wrong with this filename: %s.\n%s"%(filename, err)

def guess_extension_by_mimetype(filename):
    try:
        return mimetypes.guess_extension( mimetypes.guess_type(filename)[0] )
    except ValueError as err:
        print "Something's wrong with this filename: %s.\n%s"%(filename, err)

def thumbnail_name(filename):
    filename_noext = os.path.splitext(filename)[0]
    return "%s.thumb%s"%(filename_noext, guess_extension_by_filename(filename))

def has_thumbnail(filename):
    filename_noext = os.path.splitext(os.path.basename(filename))[0]
    return os.path.isfile(os.path.join(settings.MEDIA_ROOT, "%s.thumb%s"%(
                filename_noext,guess_extension_by_filename(filename))))

def generate_thumbnail(filename, size=(100,100)):
    filename_noext = os.path.splitext(os.path.basename(filename))[0]
    thumbnail = os.path.join(settings.MEDIA_ROOT, "%s.thumb%s"%(
            filename_noext,guess_extension_by_filename(filename)))
    original = os.path.join(settings.MEDIA_ROOT, os.path.basename(filename))

    if os.path.isfile(original):
        thumb = Image.open(original)
        thumb.thumbnail(size, Image.ANTIALIAS)
        thumb.save(thumbnail, thumb.format)

    return thumbnail
