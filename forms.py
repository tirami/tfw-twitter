import re

#########
# Util
#########
url_re = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def validate_text(text):
    return True, None # free text is always valid


def validate_url(text):
    if url_re.match(text):
        return True, None
    else:
        if len(text) == 0:
            return False, "Please provide a URL."
        else:
            return False, "Please provide a URL. {} is not a valid.".format(text)


class FormField(object):
    def __init__(self, input_type, name, label, placeholder="", validator=validate_text, required=False):
        self.type = input_type
        self.name = name
        self.label = label
        self.placeholder = placeholder
        self.validator = validator
        self.required = required
        self.value = ""
        self.has_error = False
        self.error_msg = None

    def validate(self):
        if not self.value:
            if self.required:
                return False, '{} is required.'.format(self.name)
            else:
                return True, None
        else:
            return self.validator(self.value)


class Form(object):
    def __init__(self, values, fields):
        self.fields = []
        self.values = values
        self.__dict__.update(fields)
        for key, field in fields.iteritems():
            self.add_field(field)

    def add_field(self, field):
        field.value = self.values[field.name]
        self.fields.append(field)

    def named_values(self):
        return {field.name: str(field.value) for field in self.fields}

    def validate(self):
        has_passed = True
        for field in self.fields:
            ok, msg = field.validate()
            field.has_error = not ok
            field.error_msg = msg
            if field.has_error:
                has_passed = False
        return has_passed
