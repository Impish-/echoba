from wtforms.widgets import html_params, HTMLString


class DivWidget(object):
    def __init__(self, html_tag='div', prefix_label=True):
        self.html_tag = html_tag
        self.prefix_label = prefix_label

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        html = ['<%s %s>' % (self.html_tag, html_params(**kwargs))]
        for subfield in field:
            if self.prefix_label:
                html.append('<div style="display:inline">%s %s;&nbsp;</div>' % (subfield.label, subfield()))
            else:
                html.append('<div style="display:inline">%s %s;&nbsp;</div>' % (subfield(), subfield.label))
        html.append('</%s>' % self.html_tag)
        return HTMLString(''.join(html))