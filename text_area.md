A widget for editing text which may span multiple lines. Supports text selection, soft wrapping, optional syntax highlighting with tree-sitter and a variety of keybindings.

Focusable
Container
Guide¶
Code editing vs plain text editing¶
By default, the TextArea widget is a standard multi-line input box with soft-wrapping enabled.

If you're interested in editing code, you may wish to use the TextArea.code_editor convenience constructor. This is a method which, by default, returns a new TextArea with soft-wrapping disabled, line numbers enabled, and the tab key behavior configured to insert \t.

Syntax highlighting dependencies¶
To enable syntax highlighting, you'll need to install the syntax extra dependencies:


pip
poetry

pip install "textual[syntax]"

This will install tree-sitter and tree-sitter-languages. These packages are distributed as binary wheels, so it may limit your applications ability to run in environments where these wheels are not available. After installing, you can set the language reactive attribute on the TextArea to enable highlighting.

Loading text¶
In this example we load some initial text into the TextArea, and set the language to "python" to enable syntax highlighting.


Output
text_area_example.py
TextAreaExample
▊
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
▎
▊
1  
d
ef
hello(name):
▎
▊
2  
print
(
"hello"
+
name)
▎
▊
3  
▎
▊
4  
def
goodbye(name):
▎
▊
5  
print
(
"goodbye"
+
name)
▎
▊
6  
▎
▊
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
▎


To update the content programmatically, set the text property to a string value.

To update the parser used for syntax highlighting, set the language reactive attribute:


# Set the language to Markdown
text_area.language = "markdown"
Note

More built-in languages will be added in the future. For now, you can add your own.

Reading content from TextArea¶
There are a number of ways to retrieve content from the TextArea:

The TextArea.text property returns all content in the text area as a string.
The TextArea.selected_text property returns the text corresponding to the current selection.
The TextArea.get_text_range method returns the text between two locations.
In all cases, when multiple lines of text are retrieved, the document line separator will be used.

Editing content inside TextArea¶
The content of the TextArea can be updated using the replace method. This method is the programmatic equivalent of selecting some text and then pasting.

Some other convenient methods are available, such as insert, delete, and clear.

Tip

The TextArea.document.end property returns the location at the end of the document, which might be convenient when editing programmatically.

Working with the cursor¶
Moving the cursor¶
The cursor location is available via the cursor_location property, which represents the location of the cursor as a tuple (row_index, column_index). These indices are zero-based and represent the position of the cursor in the content. Writing a new value to cursor_location will immediately update the location of the cursor.


>>> text_area = TextArea()
>>> text_area.cursor_location
(0, 0)
>>> text_area.cursor_location = (0, 4)
>>> text_area.cursor_location
(0, 4)
cursor_location is a simple way to move the cursor programmatically, but it doesn't let us select text.

Selecting text¶
To select text, we can use the selection reactive attribute. Let's select the first two lines of text in a document by adding text_area.selection = Selection(start=(0, 0), end=(2, 0)) to our code:


Output
text_area_selection.py
TextAreaSelection
▊
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
▎
▊
1  
def
hello(name):
▎
▊
2  
print
(
"hello"
+
name)
▎
▊
3  
▎
▊
4  
def
goodbye(name):
▎
▊
5  
print
(
"goodbye"
+
name)
▎
▊
6  
▎
▊
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
▎


Note that selections can happen in both directions, so Selection((2, 0), (0, 0)) is also valid.

Tip

The end attribute of the selection is always equal to TextArea.cursor_location. In other words, the cursor_location attribute is simply a convenience for accessing text_area.selection.end.

More cursor utilities¶
There are a number of additional utility methods available for interacting with the cursor.

Location information¶
Many properties exist on TextArea which give information about the current cursor location. These properties begin with cursor_at_, and return booleans. For example, cursor_at_start_of_line tells us if the cursor is at a start of line.

We can also check the location the cursor would arrive at if we were to move it. For example, get_cursor_right_location returns the location the cursor would move to if it were to move right. A number of similar methods exist, with names like get_cursor_*_location.

Cursor movement methods¶
The move_cursor method allows you to move the cursor to a new location while selecting text, or move the cursor and scroll to keep it centered.


# Move the cursor from its current location to row index 4,
# column index 8, while selecting all the text between.
text_area.move_cursor((4, 8), select=True)
The move_cursor_relative method offers a very similar interface, but moves the cursor relative to its current location.

Common selections¶
There are some methods available which make common selections easier:

select_line selects a line by index. Bound to F6 by default.
select_all selects all text. Bound to F7 by default.
Themes¶
TextArea ships with some builtin themes, and you can easily add your own.

Themes give you control over the look and feel, including syntax highlighting, the cursor, selection, gutter, and more.

Default theme¶
The default TextArea theme is called css, which takes its values entirely from CSS. This means that the default appearance of the widget fits nicely into a standard Textual application, and looks right on both dark and light mode.

When using the css theme, you can make use of component classes to style elements of the TextArea. For example, the CSS code TextArea .text-area--cursor { background: green; } will make the cursor green.

More complex applications such as code editors may want to use pre-defined themes such as monokai. This involves using a TextAreaTheme object, which we cover in detail below. This allows full customization of the TextArea, including syntax highlighting, at the code level.

Using builtin themes¶
The initial theme of the TextArea is determined by the theme parameter.


# Create a TextArea with the 'dracula' theme.
yield TextArea.code_editor("print(123)", language="python", theme="dracula")
You can check which themes are available using the available_themes property.


>>> text_area = TextArea()
>>> print(text_area.available_themes)
{'css', 'dracula', 'github_light', 'monokai', 'vscode_dark'}
After creating a TextArea, you can change the theme by setting the theme attribute to one of the available themes.


text_area.theme = "vscode_dark"
On setting this attribute the TextArea will immediately refresh to display the updated theme.

Custom themes¶
Note

Custom themes are only relevant for people who are looking to customize syntax highlighting. If you're only editing plain text, and wish to recolor aspects of the TextArea, you should use the provided component classes.

Using custom (non-builtin) themes is a two-step process:

Create an instance of TextAreaTheme.
Register it using TextArea.register_theme.
1. Creating a theme¶
Let's create a simple theme, "my_cool_theme", which colors the cursor blue, and the cursor line yellow. Our theme will also syntax highlight strings as red, and comments as magenta.


from rich.style import Style
from textual.widgets.text_area import TextAreaTheme
# ...
my_theme = TextAreaTheme(
    # This name will be used to refer to the theme...
    name="my_cool_theme",
    # Basic styles such as background, cursor, selection, gutter, etc...
    cursor_style=Style(color="white", bgcolor="blue"),
    cursor_line_style=Style(bgcolor="yellow"),
    # `syntax_styles` is for syntax highlighting.
    # It maps tokens parsed from the document to Rich styles.
    syntax_styles={
        "string": Style(color="red"),
        "comment": Style(color="magenta"),
    }
)
Attributes like cursor_style and cursor_line_style apply general language-agnostic styling to the widget. If you choose not to supply a value for one of these attributes, it will be taken from the CSS component styles.

The syntax_styles attribute of TextAreaTheme is used for syntax highlighting and depends on the language currently in use. For more details, see syntax highlighting.

If you wish to build on an existing theme, you can obtain a reference to it using the TextAreaTheme.get_builtin_theme classmethod:


from textual.widgets.text_area import TextAreaTheme

monokai = TextAreaTheme.get_builtin_theme("monokai")
2. Registering a theme¶
Our theme can now be registered with the TextArea instance.


text_area.register_theme(my_theme)
After registering a theme, it'll appear in the available_themes:


>>> print(text_area.available_themes)
{'dracula', 'github_light', 'monokai', 'vscode_dark', 'my_cool_theme'}
We can now switch to it:


text_area.theme = "my_cool_theme"
This immediately updates the appearance of the TextArea:

TextAreaCustomThemes
▊
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
▎
▊
#
 says hello
▎
▊
def hello(name): 
▎
▊
    print(
"hello"
 + name) 
▎
▊
▎
▊
# says goodbye
▄▄
▎
▊
def goodbye(name): 
▎
▊
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
▎

Tab and Escape behavior¶
Pressing the Tab key will shift focus to the next widget in your application by default. This matches how other widgets work in Textual.

To have Tab insert a \t character, set the tab_behavior attribute to the string value "indent". While in this mode, you can shift focus by pressing the Esc key.

Indentation¶
The character(s) inserted when you press tab is controlled by setting the indent_type attribute to either tabs or spaces.

If indent_type == "spaces", pressing Tab will insert up to indent_width spaces in order to align with the next tab stop.

Undo and redo¶
TextArea offers undo and redo methods. By default, undo is bound to Ctrl+Z and redo to Ctrl+Y.

The TextArea uses a heuristic to place checkpoints after certain types of edit. When you call undo, all of the edits between now and the most recent checkpoint are reverted. You can manually add a checkpoint by calling the TextArea.history.checkpoint() instance method.

The undo and redo history uses a stack-based system, where a single item on the stack represents a single checkpoint. In memory-constrained environments, you may wish to reduce the maximum number of checkpoints that can exist. You can do this by passing the max_checkpoints argument to the TextArea constructor.

Read-only mode¶
TextArea.read_only is a boolean reactive attribute which, if True, will prevent users from modifying content in the TextArea.

While read_only=True, you can still modify the content programmatically.

While this mode is active, the TextArea receives the -read-only CSS class, which you can use to supply custom styles for read-only mode.

Line separators¶
When content is loaded into TextArea, the content is scanned from beginning to end and the first occurrence of a line separator is recorded.

This separator will then be used when content is later read from the TextArea via the text property. The TextArea widget does not support exporting text which contains mixed line endings.

Similarly, newline characters pasted into the TextArea will be converted.

You can check the line separator of the current document by inspecting TextArea.document.newline:


>>> text_area = TextArea()
>>> text_area.document.newline
'\n'
Line numbers¶
The gutter (column on the left containing line numbers) can be toggled by setting the show_line_numbers attribute to True or False.

Setting this attribute will immediately repaint the TextArea to reflect the new value.

You can also change the start line number (the topmost line number in the gutter) by setting the line_number_start reactive attribute.

Extending TextArea¶
Sometimes, you may wish to subclass TextArea to add some extra functionality. In this section, we'll briefly explore how we can extend the widget to achieve common goals.

Hooking into key presses¶
You may wish to hook into certain key presses to inject some functionality. This can be done by over-riding _on_key and adding the required functionality.

Example - closing parentheses automatically¶
Let's extend TextArea to add a feature which automatically closes parentheses and moves the cursor to a sensible location.


from textual import events
from textual.app import App, ComposeResult
from textual.widgets import TextArea


class ExtendedTextArea(TextArea):
    """A subclass of TextArea with parenthesis-closing functionality."""

    def _on_key(self, event: events.Key) -> None:
        if event.character == "(":
            self.insert("()")
            self.move_cursor_relative(columns=-1)
            event.prevent_default()


class TextAreaKeyPressHook(App):
    def compose(self) -> ComposeResult:
        yield ExtendedTextArea.code_editor(language="python")


app = TextAreaKeyPressHook()
if __name__ == "__main__":
    app.run()
This intercepts the key handler when "(" is pressed, and inserts "()" instead. It then moves the cursor so that it lands between the open and closing parentheses.

Typing "def hello(" into the TextArea now results in the bracket automatically being closed:

TextAreaKeyPressHook
▊
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
▎
▊
1  
def
hello
(
)
▎
▊
▎
▊
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
▎

Advanced concepts¶
Syntax highlighting¶
Syntax highlighting inside the TextArea is powered by a library called tree-sitter.

Each time you update the document in a TextArea, an internal syntax tree is updated. This tree is frequently queried to find location ranges relevant to syntax highlighting. We give these ranges names, and ultimately map them to Rich styles inside TextAreaTheme.syntax_styles.

To illustrate how this works, lets look at how the "Monokai" TextAreaTheme highlights Markdown files.

When the language attribute is set to "markdown", a highlight query similar to the one below is used (trimmed for brevity).


(heading_content) @heading
(link) @link
This highlight query maps heading_content nodes returned by the Markdown parser to the name @heading, and link nodes to the name @link.

Inside our TextAreaTheme.syntax_styles dict, we can map the name @heading to a Rich style. Here's a snippet from the "Monokai" theme which does just that:


TextAreaTheme(
    name="monokai",
    base_style=Style(color="#f8f8f2", bgcolor="#272822"),
    gutter_style=Style(color="#90908a", bgcolor="#272822"),
    # ...
    syntax_styles={
        # Colorise @heading and make them bold
        "heading": Style(color="#F92672", bold=True),
        # Colorise and underline @link
        "link": Style(color="#66D9EF", underline=True),
        # ...
    },
)
To understand which names can be mapped inside syntax_styles, we recommend looking at the existing themes and highlighting queries (.scm files) in the Textual repository.

Tip

You may also wish to take a look at the contents of TextArea._highlights on an active TextArea instance to see which highlights have been generated for the open document.

Adding support for custom languages¶
To add support for a language to a TextArea, use the register_language method.

To register a language, we require two things:

A tree-sitter Language object which contains the grammar for the language.
A highlight query which is used for syntax highlighting.
Example - adding Java support¶
The easiest way to obtain a Language object is using the py-tree-sitter-languages package. Here's how we can use this package to obtain a reference to a Language object representing Java:


from tree_sitter_languages import get_language
java_language = get_language("java")
The exact version of the parser used when you call get_language can be checked via the repos.txt file in the version of py-tree-sitter-languages you're using. This file contains links to the GitHub repos and commit hashes of the tree-sitter parsers. In these repos you can often find pre-made highlight queries at queries/highlights.scm, and a file showing all the available node types which can be used in highlight queries at src/node-types.json.

Since we're adding support for Java, lets grab the Java highlight query from the repo by following these steps:

Open repos.txt file from the py-tree-sitter-languages repo.
Find the link corresponding to tree-sitter-java and go to the repo on GitHub (you may also need to go to the specific commit referenced in repos.txt).
Go to queries/highlights.scm to see the example highlight query for Java.
Be sure to check the license in the repo to ensure it can be freely copied.

Warning

It's important to use a highlight query which is compatible with the parser in use, so pay attention to the commit hash when visiting the repo via repos.txt.

We now have our Language and our highlight query, so we can register Java as a language.


from pathlib import Path

from tree_sitter_languages import get_language

from textual.app import App, ComposeResult
from textual.widgets import TextArea

java_language = get_language("java")
java_highlight_query = (Path(__file__).parent / "java_highlights.scm").read_text()
java_code = """\
class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
"""


class TextAreaCustomLanguage(App):
    def compose(self) -> ComposeResult:
        text_area = TextArea.code_editor(text=java_code)
        text_area.cursor_blink = False

        # Register the Java language and highlight query
        text_area.register_language("java", java_language, java_highlight_query)

        # Switch to Java
        text_area.language = "java"
        yield text_area


app = TextAreaCustomLanguage()
if __name__ == "__main__":
    app.run()
Running our app, we can see that the Java code is highlighted. We can freely edit the text, and the syntax highlighting will update immediately.

Recall that we map names (like @heading) from the tree-sitter highlight query to Rich style objects inside the TextAreaTheme.syntax_styles dictionary. If you notice some highlights are missing after registering a language, the issue may be:

The current TextAreaTheme doesn't contain a mapping for the name in the highlight query. Adding a new key-value pair to syntax_styles should resolve the issue.
The highlight query doesn't assign a name to the pattern you expect to be highlighted. In this case you'll need to update the highlight query to assign to the name.
Tip

The names assigned in tree-sitter highlight queries are often reused across multiple languages. For example, @string is used in many languages to highlight strings.

Navigation and wrapping information¶
If you're building functionality on top of TextArea, it may be useful to inspect the navigator and wrapped_document attributes.

navigator is a DocumentNavigator instance which can give us general information about the cursor's location within a document, as well as where the cursor will move to when certain actions are performed.
wrapped_document is a WrappedDocument instance which can be used to convert document locations to visual locations, taking wrapping into account. It also offers a variety of other convenience methods and properties.
A detailed view of these classes is out of scope, but do note that a lot of the functionality of TextArea exists within them, so inspecting them could be worthwhile.

Reactive attributes¶
Name	Type	Default	Description
language	str | None	None	The language to use for syntax highlighting.
theme	str	"css"	The theme to use.
selection	Selection	Selection()	The current selection.
show_line_numbers	bool	False	Show or hide line numbers.
line_number_start	int	1	The start line number in the gutter.
indent_width	int	4	The number of spaces to indent and width of tabs.
match_cursor_bracket	bool	True	Enable/disable highlighting matching brackets under cursor.
cursor_blink	bool	True	Enable/disable blinking of the cursor when the widget has focus.
soft_wrap	bool	True	Enable/disable soft wrapping.
read_only	bool	False	Enable/disable read-only mode.
Messages¶
TextArea.Changed
TextArea.SelectionChanged
Bindings¶
The TextArea widget defines the following bindings:

Key(s)	Description
up	Move the cursor up.
down	Move the cursor down.
left	Move the cursor left.
ctrl+left	Move the cursor to the start of the word.
ctrl+shift+left	Move the cursor to the start of the word and select.
right	Move the cursor right.
ctrl+right	Move the cursor to the end of the word.
ctrl+shift+right	Move the cursor to the end of the word and select.
home,ctrl+a	Move the cursor to the start of the line.
end,ctrl+e	Move the cursor to the end of the line.
shift+home	Move the cursor to the start of the line and select.
shift+end	Move the cursor to the end of the line and select.
pageup	Move the cursor one page up.
pagedown	Move the cursor one page down.
shift+up	Select while moving the cursor up.
shift+down	Select while moving the cursor down.
shift+left	Select while moving the cursor left.
shift+right	Select while moving the cursor right.
backspace	Delete character to the left of cursor.
ctrl+w	Delete from cursor to start of the word.
delete,ctrl+d	Delete character to the right of cursor.
ctrl+f	Delete from cursor to end of the word.
ctrl+shift+k	Delete the current line.
ctrl+u	Delete from cursor to the start of the line.
ctrl+k	Delete from cursor to the end of the line.
f6	Select the current line.
f7	Select all text in the document.
ctrl+z	Undo.
ctrl+y	Redo.
ctrl+x	Cut selection or line if no selection.
ctrl+c	Copy selection to clipboard.
ctrl+v	Paste from clipboard.
Component classes¶
The TextArea defines component classes that can style various aspects of the widget. Styles from the theme attribute take priority.

TextArea offers some component classes which can be used to style aspects of the widget.

Note that any attributes provided in the chosen TextAreaTheme will take priority here.

Class	Description
text-area--cursor	Target the cursor.
text-area--gutter	Target the gutter (line number column).
text-area--cursor-gutter	Target the gutter area of the line the cursor is on.
text-area--cursor-line	Target the line the cursor is on.
text-area--selection	Target the current selection.
text-area--matching-bracket	Target matching brackets.
See also¶
Input - single-line text input widget
TextAreaTheme - theming the TextArea
DocumentNavigator - guides cursor movement
WrappedDocument - manages wrapping the document
EditHistory - manages the undo stack
The tree-sitter documentation website.
The tree-sitter Python bindings repository.
py-tree-sitter-languages repository (provides binary wheels for a large variety of tree-sitter languages).
Additional notes¶
To remove the outline effect when the TextArea is focused, you can set border: none; padding: 0; in your CSS.
Bases: ScrollView

Parameters:

Name	Type	Description	Default
text ¶	str	The initial text to load into the TextArea.	''
language ¶	str | None	The language to use.	None
theme ¶	str	The theme to use.	'css'
soft_wrap ¶	bool	Enable soft wrapping.	True
tab_behavior ¶	Literal['focus', 'indent']	If 'focus', pressing tab will switch focus. If 'indent', pressing tab will insert a tab.	'focus'
read_only ¶	bool	Enable read-only mode. This prevents edits using the keyboard.	False
show_line_numbers ¶	bool	Show line numbers on the left edge.	False
line_number_start ¶	int	What line number to start on.	1
max_checkpoints ¶	int	The maximum number of undo history checkpoints to retain.	50
name ¶	str | None	The name of the TextArea widget.	None
id ¶	str | None	The ID of the widget, used to refer to it from Textual CSS.	None
classes ¶	str | None	One or more Textual CSS compatible class names separated by spaces.	None
disabled ¶	bool	True if the widget is disabled.	False
tooltip ¶	RenderableType | None	Optional tooltip.	None
 BINDINGS class-attributeinstance-attribute¶

BINDINGS = [
    Binding("up", "cursor_up", "Cursor up", show=False),
    Binding(
        "down", "cursor_down", "Cursor down", show=False
    ),
    Binding(
        "left", "cursor_left", "Cursor left", show=False
    ),
    Binding(
        "right", "cursor_right", "Cursor right", show=False
    ),
    Binding(
        "ctrl+left",
        "cursor_word_left",
        "Cursor word left",
        show=False,
    ),
    Binding(
        "ctrl+right",
        "cursor_word_right",
        "Cursor word right",
        show=False,
    ),
    Binding(
        "home,ctrl+a",
        "cursor_line_start",
        "Cursor line start",
        show=False,
    ),
    Binding(
        "end,ctrl+e",
        "cursor_line_end",
        "Cursor line end",
        show=False,
    ),
    Binding(
        "pageup",
        "cursor_page_up",
        "Cursor page up",
        show=False,
    ),
    Binding(
        "pagedown",
        "cursor_page_down",
        "Cursor page down",
        show=False,
    ),
    Binding(
        "ctrl+shift+left",
        "cursor_word_left(True)",
        "Cursor left word select",
        show=False,
    ),
    Binding(
        "ctrl+shift+right",
        "cursor_word_right(True)",
        "Cursor right word select",
        show=False,
    ),
    Binding(
        "shift+home",
        "cursor_line_start(True)",
        "Cursor line start select",
        show=False,
    ),
    Binding(
        "shift+end",
        "cursor_line_end(True)",
        "Cursor line end select",
        show=False,
    ),
    Binding(
        "shift+up",
        "cursor_up(True)",
        "Cursor up select",
        show=False,
    ),
    Binding(
        "shift+down",
        "cursor_down(True)",
        "Cursor down select",
        show=False,
    ),
    Binding(
        "shift+left",
        "cursor_left(True)",
        "Cursor left select",
        show=False,
    ),
    Binding(
        "shift+right",
        "cursor_right(True)",
        "Cursor right select",
        show=False,
    ),
    Binding("f6", "select_line", "Select line", show=False),
    Binding("f7", "select_all", "Select all", show=False),
    Binding(
        "backspace",
        "delete_left",
        "Delete character left",
        show=False,
    ),
    Binding(
        "ctrl+w",
        "delete_word_left",
        "Delete left to start of word",
        show=False,
    ),
    Binding(
        "delete,ctrl+d",
        "delete_right",
        "Delete character right",
        show=False,
    ),
    Binding(
        "ctrl+f",
        "delete_word_right",
        "Delete right to start of word",
        show=False,
    ),
    Binding("ctrl+x", "cut", "Cut", show=False),
    Binding("ctrl+c", "copy", "Copy", show=False),
    Binding("ctrl+v", "paste", "Paste", show=False),
    Binding(
        "ctrl+u",
        "delete_to_start_of_line",
        "Delete to line start",
        show=False,
    ),
    Binding(
        "ctrl+k",
        "delete_to_end_of_line_or_delete_line",
        "Delete to line end",
        show=False,
    ),
    Binding(
        "ctrl+shift+k",
        "delete_line",
        "Delete line",
        show=False,
    ),
    Binding("ctrl+z", "undo", "Undo", show=False),
    Binding("ctrl+y", "redo", "Redo", show=False),
]
Key(s)	Description
up	Move the cursor up.
down	Move the cursor down.
left	Move the cursor left.
ctrl+left	Move the cursor to the start of the word.
ctrl+shift+left	Move the cursor to the start of the word and select.
right	Move the cursor right.
ctrl+right	Move the cursor to the end of the word.
ctrl+shift+right	Move the cursor to the end of the word and select.
home,ctrl+a	Move the cursor to the start of the line.
end,ctrl+e	Move the cursor to the end of the line.
shift+home	Move the cursor to the start of the line and select.
shift+end	Move the cursor to the end of the line and select.
pageup	Move the cursor one page up.
pagedown	Move the cursor one page down.
shift+up	Select while moving the cursor up.
shift+down	Select while moving the cursor down.
shift+left	Select while moving the cursor left.
shift+right	Select while moving the cursor right.
backspace	Delete character to the left of cursor.
ctrl+w	Delete from cursor to start of the word.
delete,ctrl+d	Delete character to the right of cursor.
ctrl+f	Delete from cursor to end of the word.
ctrl+shift+k	Delete the current line.
ctrl+u	Delete from cursor to the start of the line.
ctrl+k	Delete from cursor to the end of the line.
f6	Select the current line.
f7	Select all text in the document.
ctrl+z	Undo.
ctrl+y	Redo.
ctrl+x	Cut selection or line if no selection.
ctrl+c	Copy selection to clipboard.
ctrl+v	Paste from clipboard.
 COMPONENT_CLASSES class-attribute¶

COMPONENT_CLASSES = {
    "text-area--cursor",
    "text-area--gutter",
    "text-area--cursor-gutter",
    "text-area--cursor-line",
    "text-area--selection",
    "text-area--matching-bracket",
}
TextArea offers some component classes which can be used to style aspects of the widget.

Note that any attributes provided in the chosen TextAreaTheme will take priority here.

Class	Description
text-area--cursor	Target the cursor.
text-area--gutter	Target the gutter (line number column).
text-area--cursor-gutter	Target the gutter area of the line the cursor is on.
text-area--cursor-line	Target the line the cursor is on.
text-area--selection	Target the current selection.
text-area--matching-bracket	Target matching brackets.
 available_languages property¶

available_languages
A list of the names of languages available to the TextArea.

The values in this list can be assigned to the language reactive attribute of TextArea.

The returned list contains the builtin languages plus those registered via the register_language method. Builtin languages will be listed before user-registered languages, but there are no other ordering guarantees.

 available_themes property¶

available_themes
A list of the names of the themes available to the TextArea.

The values in this list can be assigned theme reactive attribute of TextArea.

You can retrieve the full specification for a theme by passing one of the strings from this list into TextAreaTheme.get_by_name(theme_name: str).

Alternatively, you can directly retrieve a list of TextAreaTheme objects (which contain the full theme specification) by calling TextAreaTheme.builtin_themes().

 cursor_at_end_of_line property¶

cursor_at_end_of_line
True if and only if the cursor is at the end of a row.

 cursor_at_end_of_text property¶

cursor_at_end_of_text
True if and only if the cursor is at the very end of the document.

 cursor_at_first_line property¶

cursor_at_first_line
True if and only if the cursor is on the first line.

 cursor_at_last_line property¶

cursor_at_last_line
True if and only if the cursor is on the last line.

 cursor_at_start_of_line property¶

cursor_at_start_of_line
True if and only if the cursor is at column 0.

 cursor_at_start_of_text property¶

cursor_at_start_of_text
True if and only if the cursor is at location (0, 0)

 cursor_blink class-attributeinstance-attribute¶

cursor_blink = reactive(True, init=False)
True if the cursor should blink.

 cursor_location propertywritable¶

cursor_location
The current location of the cursor in the document.

This is a utility for accessing the end of TextArea.selection.

 cursor_screen_offset property¶

cursor_screen_offset
The offset of the cursor relative to the screen.

 document instance-attribute¶

document = Document(text)
The document this widget is currently editing.

 gutter_width property¶

gutter_width
The width of the gutter (the left column containing line numbers).

Returns:

Type	Description
int	The cell-width of the line number column. If show_line_numbers is False returns 0.
 history instance-attribute¶

history = EditHistory(
    max_checkpoints=max_checkpoints,
    checkpoint_timer=2.0,
    checkpoint_max_characters=100,
)
A stack (the end of the list is the top of the stack) for tracking edits.

 indent_type instance-attribute¶

indent_type = 'spaces'
Whether to indent using tabs or spaces.

 indent_width class-attributeinstance-attribute¶

indent_width = reactive(4, init=False)
The width of tabs or the multiple of spaces to align to on pressing the tab key.

If the document currently open contains tabs that are currently visible on screen, altering this value will immediately change the display width of the visible tabs.

 is_syntax_aware property¶

is_syntax_aware
True if the TextArea is currently syntax aware - i.e. it's parsing document content.

 language class-attributeinstance-attribute¶

language = language
The language to use.

This must be set to a valid, non-None value for syntax highlighting to work.

If the value is a string, a built-in language parser will be used if available.

If you wish to use an unsupported language, you'll have to register it first using TextArea.register_language.

 line_number_start class-attributeinstance-attribute¶

line_number_start = reactive(1, init=False)
The line number the first line should be.

 match_cursor_bracket class-attributeinstance-attribute¶

match_cursor_bracket = reactive(True, init=False)
If the cursor is at a bracket, highlight the matching bracket (if found).

 matching_bracket_location property¶

matching_bracket_location
The location of the matching bracket, if there is one.

 navigator instance-attribute¶

navigator = DocumentNavigator(wrapped_document)
Queried to determine where the cursor should move given a navigation action, accounting for wrapping etc.

 read_only class-attributeinstance-attribute¶

read_only = reactive(False)
True if the content is read-only.

Read-only means end users cannot insert, delete or replace content.

The document can still be edited programmatically via the API.

 selected_text property¶

selected_text
The text between the start and end points of the current selection.

 selection class-attributeinstance-attribute¶

selection = reactive(
    Selection(), init=False, always_update=True
)
The selection start and end locations (zero-based line_index, offset).

This represents the cursor location and the current selection.

The Selection.end always refers to the cursor location.

If no text is selected, then Selection.end == Selection.start is True.

The text selected in the document is available via the TextArea.selected_text property.

 show_line_numbers class-attributeinstance-attribute¶

show_line_numbers = reactive(False, init=False)
True to show the line number column on the left edge, otherwise False.

Changing this value will immediately re-render the TextArea.

 soft_wrap class-attributeinstance-attribute¶

soft_wrap = reactive(True, init=False)
True if text should soft wrap.

 text propertywritable¶

text
The entire text content of the document.

 theme class-attributeinstance-attribute¶

theme = theme
The name of the theme to use.

Themes must be registered using TextArea.register_theme before they can be used.

Syntax highlighting is only possible when the language attribute is set.

 wrap_width property¶

wrap_width
The width which gets used when the document wraps.

Accounts for gutter, scrollbars, etc.

 wrapped_document instance-attribute¶

wrapped_document = WrappedDocument(document)
The wrapped view of the document.

 Changed dataclass¶

Changed(text_area)
Bases: Message

Posted when the content inside the TextArea changes.

Handle this message using the on decorator - @on(TextArea.Changed) or a method named on_text_area_changed.

 control property¶

control
The TextArea that sent this message.

 text_area instance-attribute¶

text_area
The text_area that sent this message.

 SelectionChanged dataclass¶

SelectionChanged(selection, text_area)
Bases: Message

Posted when the selection changes.

This includes when the cursor moves or when text is selected.

 selection instance-attribute¶

selection
The new selection.

 text_area instance-attribute¶

text_area
The text_area that sent this message.

 action_copy ¶

action_copy()
Copy selection to clipboard.

 action_cursor_down ¶

action_cursor_down(select=False)
Move the cursor down one cell.

Parameters:

Name	Type	Description	Default
select ¶	bool	If True, select the text while moving.	False
 action_cursor_left ¶

action_cursor_left(select=False)
Move the cursor one location to the left.

If the cursor is at the left edge of the document, try to move it to the end of the previous line.

If text is selected, move the cursor to the start of the selection.

Parameters:

Name	Type	Description	Default
select ¶	bool	If True, select the text while moving.	False
 action_cursor_line_end ¶

action_cursor_line_end(select=False)
Move the cursor to the end of the line.

 action_cursor_line_start ¶

action_cursor_line_start(select=False)
Move the cursor to the start of the line.

 action_cursor_page_down ¶

action_cursor_page_down()
Move the cursor and scroll down one page.

 action_cursor_page_up ¶

action_cursor_page_up()
Move the cursor and scroll up one page.

 action_cursor_right ¶

action_cursor_right(select=False)
Move the cursor one location to the right.

If the cursor is at the end of a line, attempt to go to the start of the next line.

If text is selected, move the cursor to the end of the selection.

Parameters:

Name	Type	Description	Default
select ¶	bool	If True, select the text while moving.	False
 action_cursor_up ¶

action_cursor_up(select=False)
Move the cursor up one cell.

Parameters:

Name	Type	Description	Default
select ¶	bool	If True, select the text while moving.	False
 action_cursor_word_left ¶

action_cursor_word_left(select=False)
Move the cursor left by a single word, skipping trailing whitespace.

Parameters:

Name	Type	Description	Default
select ¶	bool	Whether to select while moving the cursor.	False
 action_cursor_word_right ¶

action_cursor_word_right(select=False)
Move the cursor right by a single word, skipping leading whitespace.

 action_cut ¶

action_cut()
Cut text (remove and copy to clipboard).

 action_delete_left ¶

action_delete_left()
Deletes the character to the left of the cursor and updates the cursor location.

If there's a selection, then the selected range is deleted.

 action_delete_line ¶

action_delete_line()
Deletes the lines which intersect with the selection.

 action_delete_right ¶

action_delete_right()
Deletes the character to the right of the cursor and keeps the cursor at the same location.

If there's a selection, then the selected range is deleted.

 action_delete_to_end_of_line ¶

action_delete_to_end_of_line()
Deletes from the cursor location to the end of the line.

 action_delete_to_end_of_line_or_delete_line async¶

action_delete_to_end_of_line_or_delete_line()
Deletes from the cursor location to the end of the line, or deletes the line.

The line will be deleted if the line is empty.

 action_delete_to_start_of_line ¶

action_delete_to_start_of_line()
Deletes from the cursor location to the start of the line.

 action_delete_word_left ¶

action_delete_word_left()
Deletes the word to the left of the cursor and updates the cursor location.

 action_delete_word_right ¶

action_delete_word_right()
Deletes the word to the right of the cursor and keeps the cursor at the same location.

Note that the location that we delete to using this action is not the same as the location we move to when we move the cursor one word to the right. This action does not skip leading whitespace, whereas cursor movement does.

 action_paste ¶

action_paste()
Paste from local clipboard.

 action_redo ¶

action_redo()
Redo the most recently undone batch of edits.

 action_select_all ¶

action_select_all()
Select all the text in the document.

 action_select_line ¶

action_select_line()
Select all the text on the current line.

 action_undo ¶

action_undo()
Undo the edits since the last checkpoint (the most recent batch of edits).

 cell_width_to_column_index ¶

cell_width_to_column_index(cell_width, row_index)
Return the column that the cell width corresponds to on the given row.

Parameters:

Name	Type	Description	Default
cell_width ¶	int	The cell width to convert.	required
row_index ¶	int	The index of the row to examine.	required
Returns:

Type	Description
int	The column corresponding to the cell width on that row.
 check_consume_key ¶

check_consume_key(key, character=None)
Check if the widget may consume the given key.

As a textarea we are expecting to capture printable keys.

Parameters:

Name	Type	Description	Default
key ¶	str	A key identifier.	required
character ¶	str | None	A character associated with the key, or None if there isn't one.	None
Returns:

Type	Description
bool	True if the widget may capture the key in it's Key message, or False if it won't.
 clamp_visitable ¶

clamp_visitable(location)
Clamp the given location to the nearest visitable location.

Parameters:

Name	Type	Description	Default
location ¶	Location	The location to clamp.	required
Returns:

Type	Description
Location	The nearest location that we could conceivably navigate to using the cursor.
 clear ¶

clear()
Delete all text from the document.

Returns:

Type	Description
EditResult	An EditResult relating to the deletion of all content.
 code_editor classmethod¶

code_editor(
    text="",
    *,
    language=None,
    theme="monokai",
    soft_wrap=False,
    tab_behavior="indent",
    read_only=False,
    show_line_numbers=True,
    line_number_start=1,
    max_checkpoints=50,
    name=None,
    id=None,
    classes=None,
    disabled=False,
    tooltip=None
)
Construct a new TextArea with sensible defaults for editing code.

This instantiates a TextArea with line numbers enabled, soft wrapping disabled, "indent" tab behavior, and the "monokai" theme.

Parameters:

Name	Type	Description	Default
text ¶	str	The initial text to load into the TextArea.	''
language ¶	str | None	The language to use.	None
theme ¶	str	The theme to use.	'monokai'
soft_wrap ¶	bool	Enable soft wrapping.	False
tab_behavior ¶	Literal['focus', 'indent']	If 'focus', pressing tab will switch focus. If 'indent', pressing tab will insert a tab.	'indent'
show_line_numbers ¶	bool	Show line numbers on the left edge.	True
line_number_start ¶	int	What line number to start on.	1
name ¶	str | None	The name of the TextArea widget.	None
id ¶	str | None	The ID of the widget, used to refer to it from Textual CSS.	None
classes ¶	str | None	One or more Textual CSS compatible class names separated by spaces.	None
disabled ¶	bool	True if the widget is disabled.	False
tooltip ¶	RenderableType | None	Optional tooltip	None
 delete ¶

delete(start, end, *, maintain_selection_offset=True)
Delete the text between two locations in the document.

Parameters:

Name	Type	Description	Default
start ¶	Location	The start location.	required
end ¶	Location	The end location.	required
maintain_selection_offset ¶	bool	If True, the active Selection will be updated such that the same text is selected before and after the selection, if possible. Otherwise, the cursor will jump to the end point of the edit.	True
Returns:

Type	Description
EditResult	An EditResult containing information about the edit.
 edit ¶

edit(edit)
Perform an Edit.

Parameters:

Name	Type	Description	Default
edit ¶	Edit	The Edit to perform.	required
Returns:

Type	Description
EditResult	Data relating to the edit that may be useful. The data returned
EditResult	may be different depending on the edit performed.
 find_matching_bracket ¶

find_matching_bracket(bracket, search_from)
If the character is a bracket, find the matching bracket.

Parameters:

Name	Type	Description	Default
bracket ¶	str	The character we're searching for the matching bracket of.	required
search_from ¶	Location	The location to start the search.	required
Returns:

Type	Description
Location | None	The Location of the matching bracket, or None if it's not found.
Location | None	If the character is not available for bracket matching, None is returned.
 get_column_width ¶

get_column_width(row, column)
Get the cell offset of the column from the start of the row.

Parameters:

Name	Type	Description	Default
row ¶	int	The row index.	required
column ¶	int	The column index (codepoint offset from start of row).	required
Returns:

Type	Description
int	The cell width of the column relative to the start of the row.
 get_cursor_down_location ¶

get_cursor_down_location()
Get the location the cursor will move to if it moves down.

Returns:

Type	Description
Location	The location the cursor will move to if it moves down.
 get_cursor_left_location ¶

get_cursor_left_location()
Get the location the cursor will move to if it moves left.

Returns:

Type	Description
Location	The location of the cursor if it moves left.
 get_cursor_line_end_location ¶

get_cursor_line_end_location()
Get the location of the end of the current line.

Returns:

Type	Description
Location	The (row, column) location of the end of the cursors current line.
 get_cursor_line_start_location ¶

get_cursor_line_start_location(smart_home=False)
Get the location of the start of the current line.

Parameters:

Name	Type	Description	Default
smart_home ¶	bool	If True, use "smart home key" behavior - go to the first non-whitespace character on the line, and if already there, go to offset 0. Smart home only works when wrapping is disabled.	False
Returns:

Type	Description
Location	The (row, column) location of the start of the cursors current line.
 get_cursor_right_location ¶

get_cursor_right_location()
Get the location the cursor will move to if it moves right.

Returns:

Type	Description
Location	the location the cursor will move to if it moves right.
 get_cursor_up_location ¶

get_cursor_up_location()
Get the location the cursor will move to if it moves up.

Returns:

Type	Description
Location	The location the cursor will move to if it moves up.
 get_cursor_word_left_location ¶

get_cursor_word_left_location()
Get the location the cursor will jump to if it goes 1 word left.

Returns:

Type	Description
Location	The location the cursor will jump on "jump word left".
 get_cursor_word_right_location ¶

get_cursor_word_right_location()
Get the location the cursor will jump to if it goes 1 word right.

Returns:

Type	Description
Location	The location the cursor will jump on "jump word right".
 get_line ¶

get_line(line_index)
Retrieve the line at the given line index.

You can stylize the Text object returned here to apply additional styling to TextArea content.

Parameters:

Name	Type	Description	Default
line_index ¶	int	The index of the line.	required
Returns:

Type	Description
Text	A rich.Text object containing the requested line.
 get_target_document_location ¶

get_target_document_location(event)
Given a MouseEvent, return the row and column offset of the event in document-space.

Parameters:

Name	Type	Description	Default
event ¶	MouseEvent	The MouseEvent.	required
Returns:

Type	Description
Location	The location of the mouse event within the document.
 get_text_range ¶

get_text_range(start, end)
Get the text between a start and end location.

Parameters:

Name	Type	Description	Default
start ¶	Location	The start location.	required
end ¶	Location	The end location.	required
Returns:

Type	Description
str	The text between start and end.
 insert ¶

insert(
    text, location=None, *, maintain_selection_offset=True
)
Insert text into the document.

Parameters:

Name	Type	Description	Default
text ¶	str	The text to insert.	required
location ¶	Location | None	The location to insert text, or None to use the cursor location.	None
maintain_selection_offset ¶	bool	If True, the active Selection will be updated such that the same text is selected before and after the selection, if possible. Otherwise, the cursor will jump to the end point of the edit.	True
Returns:

Type	Description
EditResult	An EditResult containing information about the edit.
 load_text ¶

load_text(text)
Load text into the TextArea.

This will replace the text currently in the TextArea and clear the edit history.

Parameters:

Name	Type	Description	Default
text ¶	str	The text to load into the TextArea.	required
 move_cursor ¶

move_cursor(
    location, select=False, center=False, record_width=True
)
Move the cursor to a location.

Parameters:

Name	Type	Description	Default
location ¶	Location	The location to move the cursor to.	required
select ¶	bool	If True, select text between the old and new location.	False
center ¶	bool	If True, scroll such that the cursor is centered.	False
record_width ¶	bool	If True, record the cursor column cell width after navigating so that we jump back to the same width the next time we move to a row that is wide enough.	True
 move_cursor_relative ¶

move_cursor_relative(
    rows=0,
    columns=0,
    select=False,
    center=False,
    record_width=True,
)
Move the cursor relative to its current location in document-space.

Parameters:

Name	Type	Description	Default
rows ¶	int	The number of rows to move down by (negative to move up)	0
columns ¶	int	The number of columns to move right by (negative to move left)	0
select ¶	bool	If True, select text between the old and new location.	False
center ¶	bool	If True, scroll such that the cursor is centered.	False
record_width ¶	bool	If True, record the cursor column cell width after navigating so that we jump back to the same width the next time we move to a row that is wide enough.	True
 record_cursor_width ¶

record_cursor_width()
Record the current cell width of the cursor.

This is used where we navigate up and down through rows. If we're in the middle of a row, and go down to a row with no content, then we go down to another row, we want our cursor to jump back to the same offset that we were originally at.

 redo ¶

redo()
Redo the most recently undone batch of edits.

 register_language ¶

register_language(name, language, highlight_query)
Register a language and corresponding highlight query.

Calling this method does not change the language of the TextArea. On switching to this language (via the language reactive attribute), syntax highlighting will be performed using the given highlight query.

If a string name is supplied for a builtin supported language, then this method will update the default highlight query for that language.

Registering a language only registers it to this instance of TextArea.

Parameters:

Name	Type	Description	Default
name ¶	str	The name of the language.	required
language ¶	'Language'	A tree-sitter Language object.	required
highlight_query ¶	str	The highlight query to use for syntax highlighting this language.	required
 register_theme ¶

register_theme(theme)
Register a theme for use by the TextArea.

After registering a theme, you can set themes by assigning the theme name to the TextArea.theme reactive attribute. For example text_area.theme = "my_custom_theme" where "my_custom_theme" is the name of the theme you registered.

If you supply a theme with a name that already exists that theme will be overwritten.

 replace ¶

replace(
    insert, start, end, *, maintain_selection_offset=True
)
Replace text in the document with new text.

Parameters:

Name	Type	Description	Default
insert ¶	str	The text to insert.	required
start ¶	Location	The start location	required
end ¶	Location	The end location.	required
maintain_selection_offset ¶	bool	If True, the active Selection will be updated such that the same text is selected before and after the selection, if possible. Otherwise, the cursor will jump to the end point of the edit.	True
Returns:

Type	Description
EditResult	An EditResult containing information about the edit.
 scroll_cursor_visible ¶

scroll_cursor_visible(center=False, animate=False)
Scroll the TextArea such that the cursor is visible on screen.

Parameters:

Name	Type	Description	Default
center ¶	bool	True if the cursor should be scrolled to the center.	False
animate ¶	bool	True if we should animate while scrolling.	False
Returns:

Type	Description
Offset	The offset that was scrolled to bring the cursor into view.
 select_all ¶

select_all()
Select all of the text in the TextArea.

 select_line ¶

select_line(index)
Select all the text in the specified line.

Parameters:

Name	Type	Description	Default
index ¶	int	The index of the line to select (starting from 0).	required
 undo ¶

undo()
Undo the edits since the last checkpoint (the most recent batch of edits).

 update_highlight_query ¶

update_highlight_query(name, highlight_query)
Update the highlight query for an already registered language.

Parameters:

Name	Type	Description	Default
name ¶	str	The name of the language.	required
highlight_query ¶	str	The highlight query to use for syntax highlighting this language.	required
 Highlight module-attribute¶

Highlight = Tuple[StartColumn, EndColumn, HighlightName]
A tuple representing a syntax highlight within one line.

 Location module-attribute¶

Location = Tuple[int, int]
A location (row, column) within the document. Indexing starts at 0.

 Document ¶

Document(text)
Bases: DocumentBase

A document which can be opened in a TextArea.

 end property¶

end
Returns the location of the end of the document.

 line_count property¶

line_count
Returns the number of lines in the document.

 lines property¶

lines
Get the document as a list of strings, where each string represents a line.

Newline characters are not included in at the end of the strings.

The newline character used in this document can be found via the Document.newline property.

 newline property¶

newline
Get the Newline used in this document (e.g. ' ', ' '. etc.)

 start property¶

start
Returns the location of the start of the document (0, 0).

 text property¶

text
Get the text from the document.

 get_index_from_location ¶

get_index_from_location(location)
Given a location, returns the index from the document's text.

Parameters:

Name	Type	Description	Default
location ¶	Location	The location in the document.	required
Returns:

Type	Description
int	The index in the document's text.
 get_line ¶

get_line(index)
Returns the line with the given index from the document.

Parameters:

Name	Type	Description	Default
index ¶	int	The index of the line in the document.	required
Returns:

Type	Description
str	The string representing the line.
 get_location_from_index ¶

get_location_from_index(index)
Given a codepoint index in the document's text, returns the corresponding location.

Parameters:

Name	Type	Description	Default
index ¶	int	The index in the document's text.	required
Returns:

Type	Description
Location	The corresponding location.
Raises:

Type	Description
ValueError	If the index is doesn't correspond to a location in the document.
 get_size ¶

get_size(tab_width)
The Size of the document, taking into account the tab rendering width.

Parameters:

Name	Type	Description	Default
tab_width ¶	int	The width to use for tab indents.	required
Returns:

Type	Description
Size	The size (width, height) of the document.
 get_text_range ¶

get_text_range(start, end)
Get the text that falls between the start and end locations.

Returns the text between start and end, including the appropriate line separator character as specified by Document._newline. Note that _newline is set automatically to the first line separator character found in the document.

Parameters:

Name	Type	Description	Default
start ¶	Location	The start location of the selection.	required
end ¶	Location	The end location of the selection.	required
Returns:

Type	Description
str	The text between start (inclusive) and end (exclusive).
 replace_range ¶

replace_range(start, end, text)
Replace text at the given range.

This is the only method by which a document may be updated.

Parameters:

Name	Type	Description	Default
start ¶	Location	A tuple (row, column) where the edit starts.	required
end ¶	Location	A tuple (row, column) where the edit ends.	required
text ¶	str	The text to insert between start and end.	required
Returns:

Type	Description
EditResult	The EditResult containing information about the completed replace operation.
 DocumentBase ¶
Bases: ABC

Describes the minimum functionality a Document implementation must provide in order to be used by the TextArea widget.

 end abstractmethodproperty¶

end
Returns the location of the end of the document.

 line_count abstractmethodproperty¶

line_count
Returns the number of lines in the document.

 lines abstractmethodproperty¶

lines
Get the lines of the document as a list of strings.

The strings should not include newline characters. The newline character used for the document can be retrieved via the newline property.

 newline abstractmethodproperty¶

newline
Return the line separator used in the document.

 start abstractmethodproperty¶

start
Returns the location of the start of the document (0, 0).

 text abstractmethodproperty¶

text
The text from the document as a string.

 get_line abstractmethod¶

get_line(index)
Returns the line with the given index from the document.

This is used in rendering lines, and will be called by the TextArea for each line that is rendered.

Parameters:

Name	Type	Description	Default
index ¶	int	The index of the line in the document.	required
Returns:

Type	Description
str	The str instance representing the line.
 get_size abstractmethod¶

get_size(indent_width)
Get the size of the document.

The height is generally the number of lines, and the width is generally the maximum cell length of all the lines.

Parameters:

Name	Type	Description	Default
indent_width ¶	int	The width to use for tab characters.	required
Returns:

Type	Description
Size	The Size of the document bounding box.
 get_text_range abstractmethod¶

get_text_range(start, end)
Get the text that falls between the start and end locations.

Parameters:

Name	Type	Description	Default
start ¶	Location	The start location of the selection.	required
end ¶	Location	The end location of the selection.	required
Returns:

Type	Description
str	The text between start (inclusive) and end (exclusive).
 query_syntax_tree ¶

query_syntax_tree(query, start_point=None, end_point=None)
Query the tree-sitter syntax tree.

The default implementation always returns an empty list.

To support querying in a subclass, this must be implemented.

Parameters:

Name	Type	Description	Default
query ¶	'Query'	The tree-sitter Query to perform.	required
start_point ¶	tuple[int, int] | None	The (row, column byte) to start the query at.	None
end_point ¶	tuple[int, int] | None	The (row, column byte) to end the query at.	None
Returns:

Type	Description
dict[str, list['Node']]	A dict mapping captured node names to lists of Nodes with that name.
 replace_range abstractmethod¶

replace_range(start, end, text)
Replace the text at the given range.

Parameters:

Name	Type	Description	Default
start ¶	Location	A tuple (row, column) where the edit starts.	required
end ¶	Location	A tuple (row, column) where the edit ends.	required
text ¶	str	The text to insert between start and end.	required
Returns:

Type	Description
EditResult	The new end location after the edit is complete.
 DocumentNavigator ¶

DocumentNavigator(wrapped_document)
Cursor navigation in the TextArea is "wrapping-aware".

Although the cursor location (the selection) is represented as a location in the raw document, when you actually move the cursor, it must take wrapping into account (otherwise things start to look really confusing to the user where wrapping is involved).

Your cursor visually moves through the wrapped version of the document, rather than the raw document. So, for example, pressing down on the keyboard may move your cursor to a position further along the current raw document line, rather than on to the next line in the raw document.

The DocumentNavigator class manages that behavior.

Given a cursor location in the unwrapped document, and a cursor movement action, this class can inform us of the destination the cursor will move to considering the current wrapping width and document content. It can also translate between document-space (a location/(row,col) in the raw document), and visual-space (x and y offsets) as the user will see them on screen after the document has been wrapped.

For this to work correctly, the wrapped_document and document must be synchronised. This means that if you make an edit to the document, you must then update the wrapped document, and then you may query the document navigator.

Naming conventions:

A "location" refers to a location, in document-space (in the raw document). It is entirely unrelated to visually positioning. A location in a document can appear in any visual position, as it is influenced by scrolling, wrapping, gutter settings, and the cell width of characters to its left.

A "wrapped section" refers to a portion of the line accounting for wrapping. For example the line "ABCDEF" when wrapped at width 3 will result in 2 sections: "ABC" and "DEF". In this case, we call "ABC" is the first section/wrapped section.

A "wrap offset" is an integer representing the index at which wrapping occurs in a document-space line. This is a codepoint index, rather than a visual offset. In "ABCDEF" with wrapping at width 3, there is a single wrap offset of 3.

"Smart home" refers to a modification of the "home" key behavior. If smart home is enabled, the first non-whitespace character is considered to be the home location. If the cursor is currently at this position, then the normal home behavior applies. This is designed to make cursor movement more useful to end users.

Parameters:

Name	Type	Description	Default
wrapped_document ¶	WrappedDocument	The WrappedDocument to be used when making navigation decisions.	required
 last_x_offset instance-attribute¶

last_x_offset = 0
Remembers the last x offset (cell width) the cursor was moved horizontally to, so that it can be restored on vertical movement where possible.

 clamp_reachable ¶

clamp_reachable(location)
Given a location, return the nearest location that corresponds to a reachable location in the document.

Parameters:

Name	Type	Description	Default
location ¶	Location	A location.	required
Returns:

Type	Description
Location	The nearest reachable location in the document.
 get_location_above ¶

get_location_above(location)
Get the location visually aligned with the cell above the given location.

Parameters:

Name	Type	Description	Default
location ¶	Location	The location to start from.	required
Returns:

Type	Description
Location	The cell above the given location.
 get_location_at_y_offset ¶

get_location_at_y_offset(location, vertical_offset)
Apply a visual vertical offset to a location and check the resulting location.

Parameters:

Name	Type	Description	Default
location ¶	Location	The location to start from.	required
vertical_offset ¶	int	The vertical offset to move (negative=up, positive=down).	required
Returns:

Type	Description
Location	The location after the offset has been applied.
 get_location_below ¶

get_location_below(location)
Given a location in the raw document, return the raw document location corresponding to moving down in the wrapped representation of the document.

Parameters:

Name	Type	Description	Default
location ¶	Location	The location in the raw document.	required
Returns:

Type	Description
Location	The location which is visually below the given location.
 get_location_end ¶

get_location_end(location)
Get the location corresponding to the end of the current section.

Parameters:

Name	Type	Description	Default
location ¶	Location	The current location.	required
Returns:

Type	Description
Location	The location corresponding to the end of the wrapped line.
 get_location_home ¶

get_location_home(location, smart_home=False)
Get the "home location" corresponding to the given location.

Parameters:

Name	Type	Description	Default
location ¶	Location	The location to consider.	required
smart_home ¶	bool	Enable/disable 'smart home' behavior.	False
Returns:

Type	Description
Location	The home location, relative to the given location.
 get_location_left ¶

get_location_left(location)
Get the location to the left of the given location.

Note that if the given location is at the start of the line, then this will return the end of the preceding line, since that's where you would expect the cursor to move.

Parameters:

Name	Type	Description	Default
location ¶	Location	The location to start from.	required
Returns:

Type	Description
Location	The location to the right.
 get_location_right ¶

get_location_right(location)
Get the location to the right of the given location.

Note that if the given location is at the end of the line, then this will return the start of the following line, since that's where you would expect the cursor to move.

Parameters:

Name	Type	Description	Default
location ¶	Location	The location to start from.	required
Returns:

Type	Description
Location	The location to the right.
 is_end_of_document ¶

is_end_of_document(location)
Check if a location is at the end of the document.

Parameters:

Name	Type	Description	Default
location ¶	Location	The location to examine.	required
Returns:

Type	Description
bool	True if and only if the cursor is at the end of the document.
 is_end_of_document_line ¶

is_end_of_document_line(location)
True if the location is at the end of a line in the document.

Note that the "end" of a line is equal to its length (one greater than the final index), since there is a space at the end of the line for the cursor to rest.

Parameters:

Name	Type	Description	Default
location ¶	Location	The location to examine.	required
Returns:

Type	Description
bool	True if and only if the document is at the end of a line in the document.
 is_end_of_wrapped_line ¶

is_end_of_wrapped_line(location)
True if the location is at the end of a wrapped line.

Parameters:

Name	Type	Description	Default
location ¶	Location	The location to examine.	required
Returns:

Type	Description
bool	True if and only if the cursor is on the last wrapped section of any line.
 is_first_document_line ¶

is_first_document_line(location)
Check if the given location is on the first line in the document.

Parameters:

Name	Type	Description	Default
location ¶	Location	The location to examine.	required
Returns:

Type	Description
bool	True if and only if the cursor is on the first line of the document.
 is_first_wrapped_line ¶

is_first_wrapped_line(location)
Check if the given location is on the first wrapped section of the first line in the document.

Parameters:

Name	Type	Description	Default
location ¶	Location	The location to examine.	required
Returns:

Type	Description
bool	True if and only if the cursor is on the first wrapped section of the first line.
 is_last_document_line ¶

is_last_document_line(location)
Check if the given location is on the last line of the document.

Parameters:

Name	Type	Description	Default
location ¶	Location	The location to examine.	required
Returns:

Type	Description
bool	True when the location is on the last line of the document.
 is_last_wrapped_line ¶

is_last_wrapped_line(location)
Check if the given location is on the last wrapped section of the last line.

That is, the cursor is visually on the last rendered row.

Parameters:

Name	Type	Description	Default
location ¶	Location	The location to examine.	required
Returns:

Type	Description
bool	True if and only if the cursor is on the last section of the last line.
 is_start_of_document ¶

is_start_of_document(location)
Check if a location is at the start of the document.

Parameters:

Name	Type	Description	Default
location ¶	Location	The location to examine.	required
Returns:

Type	Description
bool	True if and only if the cursor is at document location (0, 0)
 is_start_of_document_line ¶

is_start_of_document_line(location)
True when the location is at the start of the first document line.

Parameters:

Name	Type	Description	Default
location ¶	Location	The location to check.	required
Returns:

Type	Description
bool	True if the location is at column index 0.
 is_start_of_wrapped_line ¶

is_start_of_wrapped_line(location)
True when the location is at the start of the first wrapped line.

Parameters:

Name	Type	Description	Default
location ¶	Location	The location to check.	required
Returns:

Type	Description
bool	True if the location is at column index 0.
 Edit dataclass¶

Edit(
    text,
    from_location,
    to_location,
    maintain_selection_offset,
)
Implements the Undoable protocol to replace text at some range within a document.

 bottom property¶

bottom
The Location impacted by this edit that is nearest the end of the document.

 from_location instance-attribute¶

from_location
The start location of the insert.

 maintain_selection_offset instance-attribute¶

maintain_selection_offset
If True, the selection will maintain its offset to the replacement range.

 text instance-attribute¶

text
The text to insert. An empty string is equivalent to deletion.

 to_location instance-attribute¶

to_location
The end location of the insert

 top property¶

top
The Location impacted by this edit that is nearest the start of the document.

 after ¶

after(text_area)
Hook for running code after an Edit has been performed via Edit.do and side effects such as re-wrapping the document and refreshing the display have completed.

For example, we can't record cursor visual offset until we know where the cursor will land after wrapping has been performed, so we must wait until here to do it.

Parameters:

Name	Type	Description	Default
text_area ¶	TextArea	The TextArea this operation was performed on.	required
 do ¶

do(text_area, record_selection=True)
Perform the edit operation.

Parameters:

Name	Type	Description	Default
text_area ¶	TextArea	The TextArea to perform the edit on.	required
record_selection ¶	bool	If True, record the current selection in the TextArea so that it may be restored if this Edit is undone in the future.	True
Returns:

Type	Description
EditResult	An EditResult containing information about the replace operation.
 undo ¶

undo(text_area)
Undo the edit operation.

Looks at the data stored in the edit, and performs the inverse operation of Edit.do.

Parameters:

Name	Type	Description	Default
text_area ¶	TextArea	The TextArea to undo the insert operation on.	required
Returns:

Type	Description
EditResult	An EditResult containing information about the replace operation.
 EditHistory dataclass¶

EditHistory(
    max_checkpoints,
    checkpoint_timer,
    checkpoint_max_characters,
)
Manages batching/checkpointing of Edits into groups that can be undone/redone in the TextArea.

 checkpoint_max_characters instance-attribute¶

checkpoint_max_characters
Maximum number of characters that can appear in a batch before a new batch is formed.

 checkpoint_timer instance-attribute¶

checkpoint_timer
Maximum number of seconds since last edit until a new batch is created.

 redo_stack property¶

redo_stack
A copy of the redo stack, with references to the original Edits.

 undo_stack property¶

undo_stack
A copy of the undo stack, with references to the original Edits.

 checkpoint ¶

checkpoint()
Ensure the next recorded edit starts a new batch.

 clear ¶

clear()
Completely clear the history.

 record ¶

record(edit)
Record an Edit so that it may be undone and redone.

Determines whether to batch the Edit with previous Edits, or create a new batch/checkpoint.

This method must be called exactly once per edit, in chronological order.

A new batch/checkpoint is created when:

The undo stack is empty.
The checkpoint timer expires.
The maximum number of characters permitted in a checkpoint is reached.
A redo is performed (we should not add new edits to a batch that has been redone).
The programmer has requested a new batch via a call to force_new_batch.
e.g. the TextArea widget may call this method in some circumstances.
Clicking to move the cursor elsewhere in the document should create a new batch.
Movement of the cursor via a keyboard action that is NOT an edit.
Blurring the TextArea creates a new checkpoint.
The current edit involves a deletion/replacement and the previous edit did not.
The current edit is a pure insertion and the previous edit was not.
The edit involves insertion or deletion of one or more newline characters.
An edit which inserts more than a single character (a paste) gets an isolated batch.
Parameters:

Name	Type	Description	Default
edit ¶	Edit	The edit to record.	required
 EditResult dataclass¶

EditResult(end_location, replaced_text)
Contains information about an edit that has occurred.

 end_location instance-attribute¶

end_location
The new end Location after the edit is complete.

 replaced_text instance-attribute¶

replaced_text
The text that was replaced.

 LanguageDoesNotExist ¶
Bases: Exception

Raised when the user tries to use a language which does not exist. This means a language which is not builtin, or has not been registered.

 Selection ¶
Bases: NamedTuple

A range of characters within a document from a start point to the end point. The location of the cursor is always considered to be the end point of the selection. The selection is inclusive of the minimum point and exclusive of the maximum point.

 end class-attributeinstance-attribute¶

end = (0, 0)
The end location of the selection.

If you were to click and drag a selection inside a text-editor, this is where you finished dragging.

 is_empty property¶

is_empty
Return True if the selection has 0 width, i.e. it's just a cursor.

 start class-attributeinstance-attribute¶

start = (0, 0)
The start location of the selection.

If you were to click and drag a selection inside a text-editor, this is where you started dragging.

 cursor classmethod¶

cursor(location)
Create a Selection with the same start and end point - a "cursor".

Parameters:

Name	Type	Description	Default
location ¶	Location	The location to create the zero-width Selection.	required
 SyntaxAwareDocument ¶

SyntaxAwareDocument(text, language)
Bases: Document

A wrapper around a Document which also maintains a tree-sitter syntax tree when the document is edited.

The primary reason for this split is actually to keep tree-sitter stuff separate, since it isn't supported in Python 3.7. By having the tree-sitter code isolated in this subclass, it makes it easier to conditionally import. However, it does come with other design flaws (e.g. Document is required to have methods which only really make sense on SyntaxAwareDocument).

If you're reading this and Python 3.7 is no longer supported by Textual, consider merging this subclass into the Document superclass.

Parameters:

Name	Type	Description	Default
text ¶	str	The initial text contained in the document.	required
language ¶	str | Language	The language to use. You can pass a string to use a supported language, or pass in your own tree-sitter Language object.	required
 language instance-attribute¶

language = get_language(language)
The tree-sitter Language or None if tree-sitter is unavailable.

 get_line ¶

get_line(index)
Return the string representing the line, not including new line characters.

Parameters:

Name	Type	Description	Default
line_index ¶		The index of the line.	required
Returns:

Type	Description
str	The string representing the line.
 prepare_query ¶

prepare_query(query)
Prepare a tree-sitter tree query.

Queries should be prepared once, then reused.

To execute a query, call query_syntax_tree.

Parameters:

Name	Type	Description	Default
query ¶	str	The string query to prepare.	required
Returns:

Type	Description
Query | None	The prepared query.
 query_syntax_tree ¶

query_syntax_tree(query, start_point=None, end_point=None)
Query the tree-sitter syntax tree.

The default implementation always returns an empty list.

To support querying in a subclass, this must be implemented.

Parameters:

Name	Type	Description	Default
query ¶	Query	The tree-sitter Query to perform.	required
start_point ¶	tuple[int, int] | None	The (row, column byte) to start the query at.	None
end_point ¶	tuple[int, int] | None	The (row, column byte) to end the query at.	None
Returns:

Type	Description
dict[str, list['Node']]	A tuple containing the nodes and text captured by the query.
 replace_range ¶

replace_range(start, end, text)
Replace text at the given range.

Parameters:

Name	Type	Description	Default
start ¶	Location	A tuple (row, column) where the edit starts.	required
end ¶	Location	A tuple (row, column) where the edit ends.	required
text ¶	str	The text to insert between start and end.	required
Returns:

Type	Description
EditResult	The new end location after the edit is complete.
 TextAreaTheme dataclass¶

TextAreaTheme(
    name,
    base_style=None,
    gutter_style=None,
    cursor_style=None,
    cursor_line_style=None,
    cursor_line_gutter_style=None,
    bracket_matching_style=None,
    selection_style=None,
    syntax_styles=dict(),
)
A theme for the TextArea widget.

Allows theming the general widget (gutter, selections, cursor, and so on) and mapping of tree-sitter tokens to Rich styles.

For example, consider the following snippet from the markdown.scm highlight query file. We've assigned the heading_content token type to the name heading.


(heading_content) @heading
Now, we can map this heading name to a Rich style, and it will be styled as such in the TextArea, assuming a parser which returns a heading_content node is used (as will be the case when language="markdown").


TextAreaTheme('my_theme', syntax_styles={'heading': Style(color='cyan', bold=True)})
We can register this theme with our TextArea using the TextArea.register_theme method, and headings in our markdown files will be styled bold cyan.

 base_style class-attributeinstance-attribute¶

base_style = None
The background style of the text area. If None the parent style will be used.

 bracket_matching_style class-attributeinstance-attribute¶

bracket_matching_style = None
The style to apply to matching brackets. If None, a legible Style will be generated.

 cursor_line_gutter_style class-attributeinstance-attribute¶

cursor_line_gutter_style = None
The style to apply to the gutter of the line the cursor is on. If None, a legible Style will be generated.

 cursor_line_style class-attributeinstance-attribute¶

cursor_line_style = None
The style to apply to the line the cursor is on.

 cursor_style class-attributeinstance-attribute¶

cursor_style = None
The style of the cursor. If None, a legible Style will be generated.

 gutter_style class-attributeinstance-attribute¶

gutter_style = None
The style of the gutter. If None, a legible Style will be generated.

 name instance-attribute¶

name
The name of the theme.

 selection_style class-attributeinstance-attribute¶

selection_style = None
The style of the selection. If None a default selection Style will be generated.

 syntax_styles class-attributeinstance-attribute¶

syntax_styles = field(default_factory=dict)
The mapping of tree-sitter names from the highlight_query to Rich styles.

 apply_css ¶

apply_css(text_area)
Apply CSS rules from a TextArea to be used for fallback styling.

If any attributes in the theme aren't supplied, they'll be filled with the appropriate base CSS (e.g. color, background, etc.) and component CSS (e.g. text-area--cursor) from the supplied TextArea.

Parameters:

Name	Type	Description	Default
text_area ¶	TextArea	The TextArea instance to retrieve fallback styling from.	required
 builtin_themes classmethod¶

builtin_themes()
Get a list of all builtin TextAreaThemes.

Returns:

Type	Description
list[TextAreaTheme]	A list of all builtin TextAreaThemes.
 get_builtin_theme classmethod¶

get_builtin_theme(theme_name)
Get a TextAreaTheme by name.

Given a theme_name, return the corresponding TextAreaTheme object.

Parameters:

Name	Type	Description	Default
theme_name ¶	str	The name of the theme.	required
Returns:

Type	Description
TextAreaTheme | None	The TextAreaTheme corresponding to the name or None if the theme isn't found.
 get_highlight ¶

get_highlight(name)
Return the Rich style corresponding to the name defined in the tree-sitter highlight query for the current theme.

Parameters:

Name	Type	Description	Default
name ¶	str	The name of the highlight.	required
Returns:

Type	Description
Style | None	The Style to use for this highlight, or None if no style.
 ThemeDoesNotExist ¶
Bases: Exception

Raised when the user tries to use a theme which does not exist. This means a theme which is not builtin, or has not been registered.

 WrappedDocument ¶

WrappedDocument(document, width=0, tab_width=4)
A view into a Document which wraps the document at a certain width and can be queried to retrieve lines from the wrapped version of the document.

Allows for incremental updates, ensuring that we only re-wrap ranges of the document that were influenced by edits.

By default, a WrappedDocument is wrapped with width=0 (no wrapping). To wrap the document, use the wrap() method.

Parameters:

Name	Type	Description	Default
document ¶	DocumentBase	The document to wrap.	required
width ¶	int	The width to wrap at.	0
tab_width ¶	int	The maximum width to consider for tab characters.	4
 document instance-attribute¶

document = document
The document wrapping is performed on.

 height property¶

height
The height of the wrapped document.

 lines property¶

lines
The lines of the wrapped version of the Document.

Each index in the returned list represents a line index in the raw document. The list[str] at each index is the content of the raw document line split into multiple lines via wrapping.

Note that this is expensive to compute and is not cached.

Returns:

Type	Description
list[list[str]]	A list of lines from the wrapped version of the document.
 wrapped property¶

wrapped
True if the content is wrapped. This is not the same as wrapping being "enabled". For example, an empty document can have wrapping enabled, but no wrapping has actually occurred.

In other words, this is True if the length of any line in the document is greater than the available width.

 get_offsets ¶

get_offsets(line_index)
Given a line index, get the offsets within that line where wrapping should occur for the current document.

Parameters:

Name	Type	Description	Default
line_index ¶	int	The index of the line within the document.	required
Raises:

Type	Description
ValueError	When line_index is out of bounds.
Returns:

Type	Description
list[int]	The offsets within the line where wrapping should occur.
 get_sections ¶

get_sections(line_index)
Return the sections for the given line index.

When wrapping is enabled, a single line in the document can visually span multiple lines. The list returned represents that visually (each string in the list represents a single section (y-offset) after wrapping happens).

Parameters:

Name	Type	Description	Default
line_index ¶	int	The index of the line to get sections for.	required
Returns:

Type	Description
list[str]	The wrapped line as a list of strings.
 get_tab_widths ¶

get_tab_widths(line_index)
Return a list of the tab widths for the given line index.

Parameters:

Name	Type	Description	Default
line_index ¶	int	The index of the line in the document.	required
Returns:

Type	Description
list[int]	An ordered list of the expanded width of the tabs in the line.
 get_target_document_column ¶

get_target_document_column(line_index, x_offset, y_offset)
Given a line index and the offsets within the wrapped version of that line, return the corresponding column index in the raw document.

Parameters:

Name	Type	Description	Default
line_index ¶	int	The index of the line in the document.	required
x_offset ¶	int	The x-offset within the wrapped line.	required
y_offset ¶	int	The y-offset within the wrapped line (supports negative indexing).	required
Returns:

Type	Description
int	The column index corresponding to the line index and y offset.
 location_to_offset ¶

location_to_offset(location)
Convert a location in the document to an offset within the wrapped/visual display of the document.

Parameters:

Name	Type	Description	Default
location ¶	Location	The location in the document.	required
Returns:

Type	Description
Offset	The Offset in the document's visual display corresponding to the given location.
 offset_to_location ¶

offset_to_location(offset)
Given an offset within the wrapped/visual display of the document, return the corresponding location in the document.

Parameters:

Name	Type	Description	Default
offset ¶	Offset	The y-offset within the document.	required
Raises:

Type	Description
ValueError	When the given offset does not correspond to a line in the document.
Returns:

Type	Description
Location	The Location in the document corresponding to the given offset.
 wrap ¶

wrap(width, tab_width=None)
Wrap and cache all lines in the document.

Parameters:

Name	Type	Description	Default
width ¶	int	The width to wrap at. 0 for no wrapping.	required
tab_width ¶	int | None	The maximum width to consider for tab characters. If None, reuse the tab width.	None
 wrap_range ¶

wrap_range(start, old_end, new_end)
Incrementally recompute wrapping based on a performed edit.

This must be called after the source document has been edited.

Parameters:

Name	Type	Description	Default
start ¶	Location	The start location of the edit that was performed in document-space.	required
old_end ¶	Location	The old end location of the edit in document-space.	required
new_end ¶	Location	The new end location of the edit in document-space.	required