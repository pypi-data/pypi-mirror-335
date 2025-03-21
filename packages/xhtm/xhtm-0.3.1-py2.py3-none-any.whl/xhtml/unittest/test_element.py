# coding:utf-8

import unittest

from xhtml.element.doc import HtmlDoc
from xhtml.element.tag import Br
from xhtml.element.tag import Div
from xhtml.element.tag import Form
from xhtml.element.tag import Input
from xhtml.element.tag import Span


class TestHtmlDoc(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.title: str = "Login"
        cls.html: HtmlDoc = HtmlDoc()
        cls.html.head.title.text = cls.title
        cls.user: Input = Input({"type": "text", "name": "username", "placeholder": "Username"})  # noqa:E501
        cls.user.attrs.std_style.width.v = "200px"
        cls.user.attrs.std_style.height.v = "30px"
        cls.word: Input = Input({"type": "password", "name": "password", "placeholder": "Password"})  # noqa:E501
        cls.word.attrs.std_style.width.v = "200px"
        cls.word.attrs.std_style.height.v = "30px"
        cls.post: Input = Input({"type": "submit", "value": "Submit"})
        cls.post.attrs.std_style.width.v = "200px"
        cls.post.attrs.std_style.height.v = "30px"
        cls.form: Form = Form({"method": "post"})
        cls.form.add(Div(attrs={"style": "text-align: center;"}, child=[cls.user, Br()]))  # noqa: E501
        cls.form.add(Span(attrs={"style": "display: block; margin-bottom: 10px;"}))  # noqa: E501
        cls.form.add(Div(attrs={"style": "text-align: center;"}, child=[cls.word, Br()]))  # noqa: E501
        cls.form.add(Span(attrs={"style": "display: block; margin-bottom: 20px;"}))  # noqa: E501
        cls.form.add(Div(attrs={"style": "text-align: center;"}, child=[cls.post, Br()]))  # noqa: E501
        cls.root: Div = Div()
        cls.root.add(cls.form)
        cls.root.attrs.std_style.height.v = "60vh"
        cls.root.attrs.std_style.display.v = "grid"
        cls.root.attrs.std_style.place_items.v = "center"
        cls.html.body.add(cls.root)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_html(self):
        self.assertIsInstance(str(self.html), str)

    def test_std_attrs(self):
        self.assertEqual(len(self.html.attrs), 0)
        self.assertEqual(self.html.attrs.xmlns.v, "")
        self.assertEqual(self.html.attrs.std_accesskey.v, "")
        self.assertEqual(self.html.attrs.std_class.v, "")
        self.assertEqual(self.html.attrs.std_contenteditable.v, "")
        self.assertEqual(self.html.attrs.std_contextmenu.v, "")
        self.assertEqual(self.html.attrs.std_dir.v, "")
        self.assertEqual(self.html.attrs.std_draggable.v, "")
        self.assertEqual(self.html.attrs.std_dropzone.v, "")
        self.assertEqual(self.html.attrs.std_enterkeyhint.v, "")
        self.assertEqual(self.html.attrs.std_hidden.v, "")
        self.assertEqual(self.html.attrs.std_id.v, "")
        self.assertEqual(self.html.attrs.std_inert.v, "")
        self.assertEqual(self.html.attrs.std_inputmode.v, "")
        self.assertEqual(self.html.attrs.std_lang.v, "")
        self.assertEqual(self.html.attrs.std_popover.v, "")
        self.assertEqual(self.html.attrs.std_spellcheck.v, "")
        self.assertEqual(self.html.attrs.std_tabindex.v, "")
        self.assertEqual(self.html.attrs.std_title.v, "")
        self.assertEqual(self.html.attrs.std_translate.v, "")
        self.assertNotIn("test", self.html.attrs)
        self.html.attrs["test"] = "unit"
        self.assertEqual(self.html.attrs["test"].v, "unit")
        self.assertEqual(len(self.html.attrs), 20)
        self.assertIsInstance(self.html.attrs.keys(), tuple)
        self.assertIsInstance(self.html.attrs.values(), tuple)
        self.assertIsInstance(self.html.attrs.items(), tuple)
        self.assertNotIn("unit", self.html.attrs)
        self.html.attrs.hit("unit", "test")
        self.assertEqual(self.html.attrs["unit"].v, "test")
        self.assertEqual(len(self.html.attrs), 21)

    def test_css_style(self):
        self.assertEqual(self.root.attrs.std_style.margin.v, "")
        self.assertEqual(self.root.attrs.std_style.margin_top.v, "")
        self.assertEqual(self.root.attrs.std_style.margin_bottom.v, "")
        self.assertEqual(self.root.attrs.std_style.margin_left.v, "")
        self.assertEqual(self.root.attrs.std_style.margin_right.v, "")
        self.assertEqual(self.root.attrs.std_style.text_align.v, "")
        self.assertEqual(self.root.attrs.std_style.vertical_align.v, "")

    def test_form(self):
        self.assertEqual(self.form.attrs.method.v, "post")

    def test_input(self):
        self.assertEqual(self.user.attrs.name.v, "username")
        self.assertEqual(self.user.attrs.placeholder.v, "Username")
        self.assertEqual(self.user.attrs.type.v, "text")
        self.assertEqual(self.user.attrs.value.v, "")


if __name__ == "__main__":
    unittest.main()
