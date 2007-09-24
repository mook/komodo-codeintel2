# Copyright (c) 2005-2006 ActiveState Software Inc.
#
# Contributors:
#   Eric Promislow (EricP@ActiveState.com)

"""
Tcl lexing support for codeintel/tclcile.py

Get all the lexed tokens from SilverCity, and then return them
on demand to the caller (usually a Tcl pseudo-parser).

Usage:
import tcl_lexer
lexer = lex_wrapper.Lexer(code)
while 1:
    tok = lexer.get_next_token()
    if tok[0] == EOF_STYLE:
        break;
    # tok is an array of (style, text, start-col, start-line, end-col, end-line)
    # column and line numbers are all zero-based.
"""

import copy
import re
import sys
import string

import SilverCity
from SilverCity import ScintillaConstants
import shared_lexer
from shared_lexer import EOF_STYLE

from codeintel2 import lang_tcl

class TclLexerClassifier:
    """ This classifier is similar to the parser-level classifier, but
    it works on the SilverCity "raw" tokens as opposed to the
    tokens that get created by the lexer layer.  There should be some
    folding though."""    

    def is_comment(self, ttype):
        return ttype == ScintillaConstants.SCE_TCL_COMMENT
        
    @property
    def style_comment(self):
        return ScintillaConstants.SCE_TCL_COMMENT
        
    @property
    def style_default(self):
        return ScintillaConstants.SCE_TCL_DEFAULT

    @property
    def style_operator(self):
        return ScintillaConstants.SCE_TCL_OPERATOR

#---- global data

op_re = re.compile(r'(.*?)([\\\{\}\[\]])(.*)')

class TclLexer(shared_lexer.Lexer):
    def __init__(self, code):
        shared_lexer.Lexer.__init__(self)
        self.q = []
        self.classifier = TclLexerClassifier()
        lang_tcl.TclLexer().tokenize_by_style(code, self._fix_token_list)
        # Tcl.TclLexer().tokenize_by_style(code, self._fix_token_list)
        # self._fix_token_list(q_tmp) # Updates self.q in place
        self.string_types = [ScintillaConstants.SCE_TCL_STRING,
                         ScintillaConstants.SCE_TCL_CHARACTER,
                         ScintillaConstants.SCE_TCL_LITERAL
                         ]
        
    def _fix_token_list(self, **tok):
        """ Same as perl_lexer: split op tokens into separate
            recognizable operators.
        """
        if tok['start_column'] > shared_lexer.MAX_REASONABLE_LIMIT:
            return
        tval = tok['text']
        if tok['style'] == ScintillaConstants.SCE_TCL_OPERATOR and len(tval) > 1:
            # In Tcl rely on white-space to separate arg things except for braces and brackets
            col = tok['start_column']
            tval_accum = ""
            new_tokens = []
            while True:
                m = op_re.match(tval)
                if m:
                    before, op, after = m.groups()
                    if op == '\\':
                        if len(after) > 0:
                            tval_accum += before + op + after[0]
                            tval = after[1:]
                        else:
                            new_tokens.append(tval_accum + before + op)
                            break
                    else:
                        tval_accum += before
                        if len(tval_accum) > 0:
                            new_tokens.append(tval_accum)
                        new_tokens.append(op)
                        tval = after
                else:           
                    tval_accum += tval
                    if len(tval_accum) > 0:
                        new_tokens.append(tval_accum)
                    break
            if len(new_tokens) == 1:           
                self.q.append(tok)
            else:
                col = tok['start_column']
                for stxt in new_tokens:
                    new_tok = copy.copy(tok)
                    new_tok['text'] = stxt
                    new_tok['start_column'] = col
                    new_tok['end_column'] = col + len(stxt) - 1
                    col = new_tok['end_column']
                    self.q.append(new_tok)
        else:
            self.q.append(tok)

def provide_sample_code():
    return r"""# ----------------------------------------------------------------------------
#  Command Dialog::create
# ----------------------------------------------------------------------------
proc Dialog::create { path args } {
    global   tcl_platform
    variable _widget

    array set maps [list Dialog {} .bbox {}]
    array set maps [Widget::parseArgs Dialog $args]

    # Check to see if the -class flag was specified
    set dialogClass "Dialog"
    array set dialogArgs $maps(Dialog)
    if { [info exists dialogArgs(-class)] } {
	set dialogClass $dialogArgs(-class)
    }

    puts "Test a long string" ; # proper comment
    puts "bogus comment follows -- no ;" # proper comment
}

"""


if __name__ == "__main__":
    shared_lexer.main(sys.argv, provide_sample_code, TclLexer)
