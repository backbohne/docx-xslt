from zipfile import ZipFile

class Package(object):
    """ZipFile wrapper to append/update/remove files from zip"""

    def __init__(self, filename=None):
        self.filename = filename
        self.content = {}

    def read(self, filename=None):
        filename = filename or self.filename
        with ZipFile(filename, 'r') as zip:
            for filename in zip.namelist():
                self.content[filename] = zip.read(filename)

    def write(self, filename=None):
        filename = filename or self.filename
        with ZipFile(filename, 'w') as zip:
            for filename, content in self.content.items():
                zip.writestr(filename, content)

    def get(self, filename):
        if self.has(filename):
            return self.content[filename]
        else:
            raise IndexError("%s does not exists" % filename)

    def has(self, filename):
        return filename in self.content

    def update(self, filename, content):
        if self.has(filename):
            self.content[filename] = content
        else:
            raise IndexError("%s does not exists" % filename)

    def append(self, filename, content):
        if self.has(filename):
            raise IndexError("%s does already exists" % filename)
        else:
            self.content[filename] = content

    def remove(self, filename):
        if self.has(filename):
            del self.content[filename]
        else:
            raise IndexError("%s does not exists" % filename)
