

identifier = 'edu.cmu.sv.componentGraph'
name = 'Component Graph'
version = '1.0.0'

def menu_items():
    """menu_items() -> tuple of (str,function)
    It returns a list of pairs containing text for the menu and a
    callback function that will be executed when that menu item is selected.
    """
    from test_form import TestForm

    test_form = TestForm()

    def show_test_form():
        print 'test3'
        test_form.show()
        test_form.activateWindow()
        test_form.draw_graph()
        test_form.raise_()
        
    def show_api_form():
        test_form.show()
        test_form.activateWindow()
        test_form.draw_api_to_api()
        test_form.raise_()
    
    def show_mashup_form():
        test_form.show()
        test_form.activateWindow()
        test_form.draw_mashup_to_mashup()
        test_form.raise_()
        
    def show_member_mashup_form():
        test_form.show()
        test_form.activateWindow()
        test_form.draw_member_mashup()
        test_form.raise_()

    lst = []
    lst.append(("Test Form", show_test_form))
    lst.append(("Api to Api", show_api_form))
    lst.append(("Mashup to Mashup", show_mashup_form))
    lst.append(("Member Mashups", show_member_mashup_form))
    return tuple(lst)
