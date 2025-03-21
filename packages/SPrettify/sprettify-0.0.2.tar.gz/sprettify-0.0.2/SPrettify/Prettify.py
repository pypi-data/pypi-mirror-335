"""Module for formatting strings"""
import warnings
class Prettify:
    """Makes string formatting easier and standardized."""
    def __init__(self) -> None:
        self.state = []
        self.headers = []
        self.texts = []
        self.arranged = []
        self.alignment = {'spaces': 0, 'tabs': 0}
        self._head_val = 1
        self._text_val = 0
        self._cache_val = None

    def define_alignment(self,spaces=0,tabs=0):
        "determine alignment from the left side, will only take effect on lines based on when it was defined"
        self.alignment['spaces'] = spaces
        self.alignment['tabs'] = tabs

    def add_tab(self,data="",char="=",lines=30):
        "Add horizontal tabulation" 
        alignment = self._calculate_align()
        format = f"{alignment}{data:{char}^{lines}}"
        self.headers.append(format)
        self.state.append(self._head_val)

    def add_line(self,data=""):
        "Append a line"
        alignment = self._calculate_align()
        data = f"{alignment}{data}"
        self.texts.append(data)
        self.state.append(self._text_val)

    def add_sort(self,key="",value="", separator = ":",align=1):
        "Add a key value based string"
        alignment = self._calculate_align()
        key = '%s%s' % (key, separator)
        format = f"{alignment}{key:{len(key) + align}}{value}"
        self.texts.append(format)
        self.state.append(self._text_val)
    
    def return_states(self) -> list: #List of sorted arguments
        if self.arranged != []:
            return self.arranged

    def prettyprint(self):
        "Print the whole result"
        for text in self._sort_data():
            print(text)

    def prettystring(self):
        "Return the whole string result"
        curr = ""
        for text in self._sort_data():
            try:
                curr += text + "\n"
            except TypeError:
                pass
        return curr

    def _calculate_align(self):
        tab = '\t' #python 3.12 escape char not allowed inside f-strings
        space = ' '
        alignment = f"{tab * self.alignment['tabs']}{space * self.alignment['spaces']}"
        return alignment

    def _sort_data(self):
        track_head = 0
        track_text = 0
        for i in self.state:
            if i:
                self.arranged.append(self.headers[track_head])
                track_head += 1
            elif not i:
                self.arranged.append(self.texts[track_text])
                track_text += 1
        return self.arranged

    def __call__(self):
        self.prettyprint()
    
    def __str__(self):
        return self.prettystring()
    
    def __repr__(self):
        return f"<Prettify {len(self.data)} Objects>"

class PrettyLine:
    """For Single Line Alignment toolsets"""
    def __init__(self) -> None:
        self.data = []
        self.max_spacing_default = 10
        self.max_spacing = None

    def define_spacing(self, spacing: int):
        """
        Predefines a default spacing value that is used on any rows.
        """
        self.max_spacing = spacing

    def append_text(self, data: str, max_spacing: int = None):
        """
        Horizontal alignment of text. Spacing is the maximum amount of spaces consistent throughout regardless of string length, however string length has to be lower than max_spacing count.
        """
        if (not max_spacing and not self.max_spacing):
            warnings.warn(f"User did not specify max_spacing, defaulted to {self.max_spacing_default}.")
            self.max_spacing = self.max_spacing_default
        self.data.append({"data": data, "max_space": max_spacing or self.max_spacing})
    
    def prettyprint(self):
        print(self._sort_data())
    
    def prettystring(self):
        return self._sort_data()

    def _sort_data(self):
        final = ""
        for each in self.data:
            final += f"{each['data']:<{each['max_space']}}"
        return final
    
    def __call__(self):
        self.prettyprint()

    def __str__(self):
        return self.prettystring()
    
    def __repr__(self):
        return f"<PrettyTable {len(self.data)} Objects>"