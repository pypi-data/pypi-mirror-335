from IPython.display import display, HTML


class RenderHtml(object):
    def __init__(self):            
        self.__html = None

    @property
    def html(self):
        return self.__html

    @html.setter
    def html(self, value):
        self.__html = value

    def __repr__(self):
        display(HTML(self.__html))
        return "" # hacky way to return a string despite not returning anything

class RenderTile(RenderHtml):
    def __init__(self, key, value):     
        RenderHtml.__init__(self)
        self.html = f"""<p style="color:grey">{key}</p><h1 font-size: 3em>{value}</h1>"""
    

class RenderHyperlink(RenderHtml):
    def __init__(self, key, link):   
        RenderHtml.__init__(self)         
        self.html = f"<a href={link}>{key}</a>"

class RenderTitle1(RenderHtml):
    def __init__(self, value):   
        RenderHtml.__init__(self)         
        self.html = f"<h1>{value}</h1>"

class RenderTitle2(RenderHtml):
    def __init__(self, value):   
        RenderHtml.__init__(self)         
        self.html = f"<h2>{value}</h2>"
    
class RenderTitle3(RenderHtml):
    def __init__(self, value):   
        RenderHtml.__init__(self)         
        self.html = f"<h3>{value}</h3>"
    