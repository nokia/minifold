#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# Authors:
#   Marc-Olivier Buob <marc-olivier.buob@nokia-bell-labs.com>

# Beautiful soup tests

try:
    from bs4           import BeautifulSoup
    from minifold.html import remove_tags, sanitize_html

    def test_remove_tags_flat():
        s = "<html><body>ab<i>xxxx</i>cd</i><b>yyyyy</b>ef</body></html>"
        soup = BeautifulSoup(s, features = "lxml")
        tags = ["i", "b"]
        remove_tags(soup, tags)
        assert str(soup) == "<html><body>abcdef</body></html>"

    HTML1 = """
    <body>
        <script>script1</script>
        hi
        <div>hello<script>script2</script></div>
    </body>
    """

    EXPECTED1 = "<html><body>hi<div>hello</div></body></html>"
    EXPECTED1 = """<html><body>

        hi
        <div>hello</div>
</body>
</html>"""

    def test_remove_tags_rec():
        soup = BeautifulSoup(HTML1, features = "lxml")
        remove_tags(soup, ["script"])
        assert str(soup) == EXPECTED1

    HTML2 = """
    <html>
        <head>
            <style>style1</style>
            <script>script1</script>
        </head>
        <body>
            <script src="foo.js"></script>
            <script>script2</script>
            <h1 class="title">title1</h1>
            <p class="descrition">par1
               <script>script3</script>
               <div id="plop">
                   coucou
                   bonjour
               </div>
               <img width=100 src="toto.png"/>
            </p></body></html>
    """

    EXPECTED2 = """<body>
 <h1>
  title1
 </h1>
 <p>
  par1
 </p>
 <div>
  coucou
                   bonjour
 </div>
 <img src="toto.png"/>
</body>"""

    def test_sanitize_html():
        assert sanitize_html(HTML2) == EXPECTED2
except ImportError:
    pass
