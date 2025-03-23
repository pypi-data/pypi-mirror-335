from ..text_ope import *


def test_template_text():
    template = "My name is {{ name }} and I am {{ age }}"
    result = template_text(template, data={"name": "zhangsan", "age": 18})
    print(result)
