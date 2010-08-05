#------------------------------------------------------------------------------
# Copyright (c) 2010, Enthought Inc
# All rights reserved.
# 
# This software is provided without warranty under the terms of the BSD license.

# 
# Author: Enthought Inc
# Description: <Enthought pyface code editor>
#------------------------------------------------------------------------------

# Standard library imports
import math

# System library imports
from PyQt4 import QtCore, QtGui, Qt
from pygments.lexers import get_lexer_by_name

# Local imports
from find_widget import FindWidget
from gutters import LineNumberWidget
from replace_widget import ReplaceWidget
from pygments_highlighter import PygmentsHighlighter


class CodeWidget(QtGui.QPlainTextEdit):
    """ A widget for viewing and editing code.
    """

    ###########################################################################
    # CodeWidget interface
    ###########################################################################

    def __init__(self, parent, should_highlight_current_line=True, font=None, lexer=None):
        super(CodeWidget, self).__init__(parent)

        self.highlighter = PygmentsHighlighter(self.document(), get_lexer_by_name(lexer))
        self.line_number_widget = LineNumberWidget(self)

        if font is None:
            point_size = QtGui.QApplication.font().pointSize()
            font = QtGui.QFont('Monospace', point_size)
            font.setStyleHint(QtGui.QFont.TypeWriter)
        self.set_font(font)

        # Whether we should highlight the current line or not.
        self.should_highlight_current_line = should_highlight_current_line

        # What that highlight color should be.
        self.line_highlight_color = QtGui.QColor(QtCore.Qt.yellow).lighter(160)

        # Auto-indentation behavior
        self.auto_indent = True
        self.smart_backspace = True

        # Tab settings
        self.tabs_as_spaces = True
        self.tab_width = 4

        self.indent_character = ':'
        self.comment_character = '#'

        # Set up gutter widget and current line highlighting
        self.blockCountChanged.connect(self.update_line_number_width)
        self.updateRequest.connect(self.update_line_numbers)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        
        self.update_line_number_width()
        self.highlight_current_line()

        # Don't wrap text
        self.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)

        # Key bindings
        self.indent_key = Qt.QKeySequence(Qt.Qt.Key_Tab)
        self.unindent_key = Qt.QKeySequence(Qt.Qt.SHIFT + Qt.Qt.Key_Backtab)
        self.comment_key = Qt.QKeySequence(Qt.Qt.CTRL + Qt.Qt.Key_Slash)
        self.backspace_key = Qt.QKeySequence(Qt.Qt.Key_Backspace)

    def set_font(self, font):
        """ Set the new QFont.
        """
        self.document().setDefaultFont(font)
        self.line_number_widget.set_font(font)
        self.update_line_number_width()

    def update_line_number_width(self, nblocks=0):
        """ Update the width of the line number widget.
        """
        self.setViewportMargins(self.line_number_widget.digits_width(), 0, 0, 0)

    def update_line_numbers(self, rect, dy):
        """ Update the line numbers.
        """
        if dy:
            self.line_number_widget.scroll(0, dy)
        self.line_number_widget.update(
            0, rect.y(), self.line_number_widget.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_width()

    def highlight_current_line(self):
        """ Highlight the line with the cursor.
        """
        if self.should_highlight_current_line:
            selection = QtGui.QTextEdit.ExtraSelection()
            selection.format.setBackground(self.line_highlight_color)
            selection.format.setProperty(
                QtGui.QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            self.setExtraSelections([selection])

    def autoindent_newline(self):
        tab = '\t'
        if self.tabs_as_spaces:
            tab = ' '*self.tab_width

        cursor = self.textCursor()
        text = cursor.block().text()
        trimmed = text.trimmed()
        current_indent_pos = self._get_indent_position(text)

        cursor.beginEditBlock()

        # Create the new line. There is no need to move to the new block, as
        # the insertBlock will do that automatically
        cursor.insertBlock()

        # Remove any leading whitespace from the current line
        after = cursor.block().text()
        trimmed_after = after.trimmed()
        pos = after.indexOf(trimmed_after)
        for i in range(pos):
            cursor.deleteChar()

        if self.indent_character and trimmed.endsWith(self.indent_character):
            # indent one level
            indent = text[:current_indent_pos] + tab
        else:
            # indent to the same level
            indent = text[:current_indent_pos]
        cursor.insertText(indent)

        cursor.endEditBlock()
        self.ensureCursorVisible()

    def block_indent(self):
        cursor = self.textCursor()

        if not cursor.hasSelection():
            # Insert a tabulator
            self.line_indent(cursor)

        else:
            # Indent every selected line
            sel_blocks = self._get_selected_blocks()

            cursor.clearSelection()
            cursor.beginEditBlock()

            for block in sel_blocks:
                cursor.setPosition(block.position())
                self.line_indent(cursor)

            cursor.endEditBlock()
            self._show_selected_blocks(sel_blocks)

    def block_unindent(self):
        cursor = self.textCursor()

        if not cursor.hasSelection():
            # Unindent current line
            position = cursor.position()
            cursor.beginEditBlock()

            removed = self.line_unindent(cursor)
            position = max(position-removed, 0)

            cursor.endEditBlock()
            cursor.setPosition(position)
            self.setTextCursor(cursor)

        else:
            # Unindent every selected line
            sel_blocks = self._get_selected_blocks()

            cursor.clearSelection()
            cursor.beginEditBlock()

            for block in sel_blocks:
                cursor.setPosition(block.position())
                self.line_unindent(cursor)

            cursor.endEditBlock()
            self._show_selected_blocks(sel_blocks)

    def block_comment(self):
        """the comment char will be placed at the first non-whitespace
            char of the first line. For example:
                if foo:
                    bar
            will be commented as:
                #if foo:
                #    bar
        """
        cursor = self.textCursor()

        if not cursor.hasSelection():
            text = cursor.block().text()
            current_indent_pos = self._get_indent_position(text)

            if text[current_indent_pos] == self.comment_character:
                self.line_uncomment(cursor, current_indent_pos)
            else:
                self.line_comment(cursor, current_indent_pos)

        else:
            sel_blocks = self._get_selected_blocks()
            text = sel_blocks[0].text()
            indent_pos = self._get_indent_position(text)

            comment = True
            for block in sel_blocks:
                text = block.text()
                if len(text) > indent_pos and \
                        text[indent_pos] == self.comment_character:
                    # Already commented.
                    comment = False
                    break

            cursor.clearSelection()
            cursor.beginEditBlock()

            for block in sel_blocks:
                cursor.setPosition(block.position())
                if comment:
                    if block.length() < indent_pos:
                        cursor.insertText(' ' * indent_pos)
                    self.line_comment(cursor, indent_pos)
                else:
                    self.line_uncomment(cursor, indent_pos)
            cursor.endEditBlock()
            self._show_selected_blocks(sel_blocks)

    def line_comment(self, cursor, position):
        cursor.movePosition(Qt.QTextCursor.StartOfBlock)
        cursor.movePosition(Qt.QTextCursor.Right,
                            Qt.QTextCursor.MoveAnchor, position)
        cursor.insertText(self.comment_character)

    def line_uncomment(self, cursor, position=0):
        cursor.movePosition(Qt.QTextCursor.StartOfBlock)
        new_text = cursor.block().text().remove(position, 1)
        cursor.movePosition(Qt.QTextCursor.EndOfBlock,
                            Qt.QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertText(new_text)

    def line_indent(self, cursor):
        tab = '\t'
        if self.tabs_as_spaces:
            tab = '    '

        cursor.insertText(tab)

    def line_unindent(self, cursor):
        """ Unindents the cursor's line. Returns the number of characters 
            removed.
        """
        tab = '\t'
        if self.tabs_as_spaces:
            tab = '    '

        cursor.movePosition(Qt.QTextCursor.StartOfBlock)
        if cursor.block().text().startsWith(tab):
            new_text = cursor.block().text().remove(0, len(tab))
            cursor.movePosition(Qt.QTextCursor.EndOfBlock,
                                Qt.QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            cursor.insertText(new_text)
            return len(tab)
        else:
            return 0

    def word_under_cursor(self):
        """ Return the word under the cursor.
        """
        cursor = self.textCursor()
        cursor.select(Qt.QTextCursor.WordUnderCursor)
        return unicode(cursor.selectedText())

    ###########################################################################
    # QWidget interface
    ###########################################################################

    def keyPressEvent(self, event):
        key_sequence = Qt.QKeySequence(event.key() + int(event.modifiers()))

        # If the cursor is in the middle of the first line, pressing the "up"
        # key causes the cursor to go to the start of the first line, i.e. the
        # beginning of the document. Likewise, if the cursor is somewhere in the
        # last line, the "down" key causes it to go to the end.
        cursor = self.textCursor()
        if key_sequence.matches(Qt.QKeySequence(Qt.Qt.Key_Up)):
            cursor.movePosition(QtGui.QTextCursor.StartOfLine)
            if cursor.atStart():
                self.setTextCursor(cursor)
                event.accept()
        elif key_sequence.matches(Qt.QKeySequence(Qt.Qt.Key_Down)):
            cursor.movePosition(QtGui.QTextCursor.EndOfLine)
            if cursor.atEnd():
                self.setTextCursor(cursor)
                event.accept()

        elif self.auto_indent and \
                key_sequence.matches(Qt.QKeySequence(Qt.Qt.Key_Return)):
            event.accept()
            return self.autoindent_newline()
        elif key_sequence.matches(self.indent_key):
            event.accept()
            return self.block_indent()
        elif key_sequence.matches(self.unindent_key):
            event.accept()
            return self.block_unindent()
        elif key_sequence.matches(self.comment_key):
            event.accept()
            return self.block_comment()
        elif self.auto_indent and self.smart_backspace and \
                key_sequence.matches(self.backspace_key) and \
                self._backspace_should_unindent():
            event.accept()
            return self.block_unindent()

        return super(CodeWidget, self).keyPressEvent(event)

    def resizeEvent(self, event):
        QtGui.QPlainTextEdit.resizeEvent(self, event)
        contents = self.contentsRect()
        self.line_number_widget.setGeometry(QtCore.QRect(contents.left(),
            contents.top(), self.line_number_widget.digits_width(),
            contents.height()))

    ###########################################################################
    # Private methods
    ###########################################################################

    def _get_indent_position(self, line):
        trimmed = line.trimmed()
        if trimmed.size() != 0:
            return line.indexOf(trimmed)
        else:
            # if line is all spaces, treat it as the indent position
            return line.size()

    def _show_selected_blocks(self, selected_blocks):
        """ Assumes contiguous blocks
        """
        cursor = self.textCursor()
        cursor.clearSelection()
        cursor.setPosition(selected_blocks[0].position())
        cursor.movePosition(Qt.QTextCursor.StartOfBlock)
        cursor.movePosition(Qt.QTextCursor.NextBlock, 
                            Qt.QTextCursor.KeepAnchor, len(selected_blocks))
        cursor.movePosition(Qt.QTextCursor.EndOfBlock, 
                            Qt.QTextCursor.KeepAnchor)

        self.setTextCursor(cursor)

    def _get_selected_blocks(self):
        cursor = self.textCursor()
        if cursor.position() > cursor.anchor():
            move_op = Qt.QTextCursor.PreviousBlock
            start_pos = cursor.anchor()
            end_pos = cursor.position()
        else:
            move_op = Qt.QTextCursor.NextBlock
            start_pos = cursor.position()
            end_pos = cursor.anchor()

        cursor.setPosition(start_pos)
        cursor.movePosition(Qt.QTextCursor.StartOfBlock)
        blocks = [cursor.block()]

        while cursor.movePosition(Qt.QTextCursor.NextBlock):
            block = cursor.block()
            if block.position() < end_pos:
                blocks.append(block)

        return blocks

    def _backspace_should_unindent(self):
        cursor = self.textCursor()
        # Don't unindent if we have a selection.
        if cursor.hasSelection():
            return False
        column = cursor.columnNumber()
        # Don't unindent if we are at the beggining of the line
        if column < self.tab_width:
            return False
        else:
            # Unindent if we are at the indent position
            return column == self._get_indent_position(cursor.block().text())


class AdvancedCodeWidget(QtGui.QWidget):
    """ Advanced widget for viewing and editing code, with support
        for search & replace
    """

    ###########################################################################
    # AdvancedCodeWidget interface
    ###########################################################################

    def __init__(self, parent, font=None, lexer=None):
        super(AdvancedCodeWidget, self).__init__(parent)

        self.code = CodeWidget(self, font=font, lexer=lexer)
        self.find = FindWidget(self)
        self.find.hide()
        self.replace = ReplaceWidget(self)
        self.replace.hide()
        self.replace.replace_button.setEnabled(False)
        self.replace.replace_all_button.setEnabled(False)

        self.active_find_widget = None
        self.previous_find_widget = None

        self.code.selectionChanged.connect(self._update_replace_enabled)

        self.find.line_edit.returnPressed.connect(self.find_next)
        self.find.next_button.clicked.connect(self.find_next)
        self.find.prev_button.clicked.connect(self.find_prev)

        self.replace.line_edit.returnPressed.connect(self.find_next)
        self.replace.line_edit.textChanged.connect(
            self._update_replace_all_enabled)
        self.replace.next_button.clicked.connect(self.find_next)
        self.replace.prev_button.clicked.connect(self.find_prev)
        self.replace.replace_button.clicked.connect(self.replace_next)
        self.replace.replace_all_button.clicked.connect(self.replace_all)

        layout = QtGui.QVBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(0)
        layout.addWidget(self.code)
        layout.addWidget(self.find)
        layout.addWidget(self.replace)

        self.setLayout(layout)

        # Key bindings
        self.replace_key = Qt.QKeySequence(Qt.Qt.CTRL + Qt.Qt.Key_R)

    def enable_find(self):
        self.replace.hide()
        self.find.show()
        self.find.setFocus()
        if (self.active_find_widget == self.replace or
            (not self.active_find_widget and
             self.previous_find_widget == self.replace)):
            self.find.line_edit.setText(self.replace.line_edit.text())
        self.find.line_edit.selectAll()
        self.active_find_widget = self.find

    def enable_replace(self):
        self.find.hide()
        self.replace.show()
        self.replace.setFocus()
        if (self.active_find_widget == self.find or
            (not self.active_find_widget and
             self.previous_find_widget == self.find)):
            self.replace.line_edit.setText(self.find.line_edit.text())
        self.replace.line_edit.selectAll()
        self.active_find_widget = self.replace

    def find_in_document(self, search_text, direction='forward', replace=None):
        """ Finds the next occurance of the desired text and optionally
            replaces it. If 'replace' is None, a regular search will
            be executed, otherwise it will replace the occurance with
            the value of 'replace'.

            Returns the number of occurances found (0 or 1)
        """

        if not search_text:
            return
        wrap = self.active_find_widget.wrap_action.isChecked()

        document = self.code.document()
        find_cursor = None

        flags = QtGui.QTextDocument.FindFlags(0)
        if self.active_find_widget.case_action.isChecked():
            flags |= QtGui.QTextDocument.FindCaseSensitively
        if self.active_find_widget.word_action.isChecked():
            flags |= QtGui.QTextDocument.FindWholeWords
        if direction == 'backward':
            flags |= QtGui.QTextDocument.FindBackward

        find_cursor = document.find(search_text, self.code.textCursor(), flags)
        if find_cursor.isNull() and wrap:
            if direction == 'backward':
                find_cursor = document.find(search_text, document.characterCount()-1, flags)
            else:
                find_cursor = document.find(search_text, 0, flags)

        if not find_cursor.isNull():
            if replace is not None:
                find_cursor.beginEditBlock()
                find_cursor.removeSelectedText()
                find_cursor.insertText(replace)
                find_cursor.endEditBlock()
                find_cursor.movePosition(
                    Qt.QTextCursor.Left, Qt.QTextCursor.MoveAnchor,len(replace))
                find_cursor.movePosition(
                    Qt.QTextCursor.Right,Qt.QTextCursor.KeepAnchor,len(replace))
                self.code.setTextCursor(find_cursor)
            else:
                self.code.setTextCursor(find_cursor)
            return find_cursor
        else:
            #else not found: beep or indicate?
            return None

    def find_next(self):
        if not self.active_find_widget:
            self.enable_find()
        search_text = unicode(self.active_find_widget.line_edit.text())
        cursor = self.find_in_document(search_text=search_text)

        if cursor:
            return 1
        return 0

    def find_prev(self):
        if not self.active_find_widget:
            self.enable_find()
        search_text = unicode(self.active_find_widget.line_edit.text())
        cursor = self.find_in_document(search_text=search_text,
                                       direction='backward')
        if cursor:
            return 1
        return 0

    def replace_next(self):
        search_text = self.replace.line_edit.text()
        replace_text = self.replace.replace_edit.text()

        cursor = self.code.textCursor()
        if cursor.selectedText() == search_text:
            cursor.beginEditBlock()
            cursor.removeSelectedText()
            cursor.insertText(replace_text)
            cursor.endEditBlock()
            return self.find_next()
        return 0

    def replace_all(self):
        search_text = unicode(self.replace.line_edit.text())
        replace_text = unicode(self.replace.replace_edit.text())

        count = 0
        cursor = self.code.textCursor()
        cursor.beginEditBlock()
        while self.find_in_document(search_text=search_text,
                                    replace=replace_text) != None:
            count += 1
        cursor.endEditBlock()
        return count

    def print_(self, printer):
        """ Convenience method to call 'print_' on the CodeWidget.
        """
        self.code.print_(printer)

    ###########################################################################
    # QWidget interface
    ###########################################################################

    def keyPressEvent(self, event):
        key_sequence = Qt.QKeySequence(event.key() + int(event.modifiers()))

        if key_sequence.matches(Qt.QKeySequence.Find):
            self.enable_find()
        elif key_sequence.matches(self.replace_key):
            self.enable_replace()
        elif key_sequence.matches(Qt.Qt.Key_Escape):
            if self.active_find_widget:
                self.find.hide()
                self.replace.hide()
                self.code.setFocus()
                self.previous_find_widget = self.active_find_widget
                self.active_find_widget = None

        return super(AdvancedCodeWidget, self).keyPressEvent(event)

    ###########################################################################
    # Private methods
    ###########################################################################

    def _update_replace_enabled(self):
        selection = self.code.textCursor().selectedText()
        find_text = self.replace.line_edit.text()
        self.replace.replace_button.setEnabled(selection == find_text)

    def _update_replace_all_enabled(self, text):
        self.replace.replace_all_button.setEnabled(len(text))


if __name__ == '__main__':

    def set_trace():
        from PyQt4.QtCore import pyqtRemoveInputHook
        pyqtRemoveInputHook()
        import pdb
        pdb.Pdb().set_trace(sys._getframe().f_back)

    import sys

    app = QtGui.QApplication(sys.argv)
    window = AdvancedCodeWidget(None)

    if len(sys.argv) > 1:
        f = open(sys.argv[1], 'r')
        window.code.setPlainText(f.read())

    window.resize(640, 640)
    window.show()
    sys.exit(app.exec_())

