from abstract_gui import AbstractWindowManager,make_component
from abstract_webtools import UserAgentManager,UrlManager,SafeRequest,SoupManager,LinkManager,CipherManager

class GuiGrabber:
    def __init__(self,url="www.example.com"):
        self.window_mgr = AbstractWindowManager()
        self.window_name = self.window_mgr.add_window(title="Gui_Grabber",layout=[],event_handlers=[self.while_window])
        self.url = url
        self.parse_type_choices = ['html.parser', 'lxml', 'html5lib']
        self.window_mgr.while_window()
    def layout(event,values,window):
        # Add a dropdown for selecting BeautifulSoup parsing capabilities
        make_component("theme",'LightGrey1')
        layout = [[make_component("Text",'URL:', size=(8, 1)),
                   make_component("Input",url, key='-URL-',enable_events=True),
                   make_component("Text",'status:'),
                   make_component("Text",'200',key="-STATUS_CODE-"),
                   make_component("Text",f'success: {self.url} is valid',key="-URL_WARNING-"),
                   make_component("Button",'Grab URL',key='-GRAB_URL-',visible=True)],
            [make_component("Checkbox",'Custom User-Agent', default=False, key='-CUSTOMUA-', enable_events=True)],
            [make_component("Text",'User-Agent:', size=(8, 1)),
             make_component("Combo",get_user_agents(), default_value='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36', key='-USERAGENT-', disabled=False)],
            [self.get_cypher_checks()],
            [make_component("Button",'Grab URL'),
             make_component("Button",'Action'),
             make_component("Button",'Get All Text')],
            [make_component("Text",'Parsing Capabilities:', size=(15, 1)),
             make_component("DropDown",parse_type_choices, default_value='html.parser', key='-parse_type-',enable_events=True)],
            [get_multi_line({"key":'-SOURCECODE-'})],
            [make_component("Text",'find soup:'),[[
                make_component("Checkbox",'',default=True,key='-SOUP_TAG_BOOL-',enable_events=True),
                make_component("Combo",[], size=(15, 1),key='-SOUP_TAG-',enable_events=True)],
                                    [make_component("Checkbox",'',default=False,key='-SOUP_ATTRIBUTE_BOOL-',enable_events=True),
                                     make_component("Combo",[], size=(15, 1),key='-SOUP_ATTRIBUTE-',enable_events=True)],
                                    [make_component("Checkbox",'',default=False,key='-SOUP_ATTRIBUTE_1_BOOL-',enable_events=True),
                                     make_component("Combo",[], size=(15, 1),key='-SOUP_ATTRIBUTE_1-',enable_events=True)],
                                    [make_component("Checkbox",'',default=False,key='-SOUP_ATTRIBUTE_2_BOOL-',enable_events=True),
                                     make_component("Combo",[], size=(15, 1),key='-SOUP_ATTRIBUTE_2-',enable_events=True)],
                                    make_component("Input",key='-SOUP_VALUES_INPUT-'),
                                                  make_component("Button",'get soup'),
                                                  make_component("Button",'all soup'),
                                                  make_component("Button",'Send Soup')]],
                  [get_multi_line({"key":"-FIND_ALL_OUTPUT-"})]]
        return layout
GuiGrabber()
