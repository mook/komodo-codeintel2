#!/usr/bin/env python

# ***** BEGIN LICENSE BLOCK *****
# Version: MPL 1.1/GPL 2.0/LGPL 2.1
# 
# The contents of this file are subject to the Mozilla Public License
# Version 1.1 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
# 
# Software distributed under the License is distributed on an "AS IS"
# basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
# License for the specific language governing rights and limitations
# under the License.
# 
# The Original Code is Komodo code.
# 
# The Initial Developer of the Original Code is ActiveState Software Inc.
# Portions created by ActiveState Software Inc are Copyright (C) 2000-2007
# ActiveState Software Inc. All Rights Reserved.
# 
# Contributor(s):
#   ActiveState Software Inc
# 
# Alternatively, the contents of this file may be used under the terms of
# either the GNU General Public License Version 2 or later (the "GPL"), or
# the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
# in which case the provisions of the GPL or the LGPL are applicable instead
# of those above. If you wish to allow use of your version of this file only
# under the terms of either the GPL or the LGPL, and not to allow others to
# use your version of this file under the terms of the MPL, indicate your
# decision by deleting the provisions above and replace them with the notice
# and other provisions required by the GPL or the LGPL. If you do not delete
# the provisions above, a recipient may use your version of this file under
# the terms of any one of the MPL, the GPL or the LGPL.
# 
# ***** END LICENSE BLOCK *****

""" Utility class used for the parsing of Javascript comments.

This uses the JavaSciptDoc style (JSDoc) "http://jsdoc.sourceforge.net/" for
allowing comments to specify specific information about the file structure.

The TAGS we use for JavaScript is based upon what JSDoc
supplies and what YAHOO has done. A YAHOO example is:

/**
 * Method for creating a slider
 *
 * @private
 * @param s {String} the name of the slider.
 * @param id {String} element id to place the silder within
 * @param {int} leftPadding is the size of the padding field on the left
 * @param rightPadding {int} optional field for setting the size of the padding
 * field on the right.
 * @return {Slider} a horizontal slider control
 */

Notes:
* comments and type information "{...}" are optional
* {} type field can be either the first or second position after the field.
* field comments can span multiple lines.
"""

# JSDoc tags and the help (calltip) for the tag.
# Note: Not all of these have a meaning for the javascript ciler.
jsdoc_tags = {
    "addon":        "This is an addon to an external JS class or component.\n"
                    "Example: /** @addon */",

    "argument":     "Provide information about a function parameter.\n"
                    "Note: Same as @param.\n"
                    "Example: /** @argument arg1 {string}  The first argument */",

    "author":       "The author of this component.\n"
                    "Example: /** @author John Smith jsmith@jsmith.com.mars */",

    "base":         "The base class this class extends.\n"
                    "Note: Same as @extends.\n"
                    "Example: /** @base MyParentClass */",

    "class":        "This tag is used in a constructor's documentation block\n"
                    "to provide information about the actual class.\n"
                    "Example: /** @class MyClass */",

    "constructor":  "The constructor for the class.\n"
                    "Example: /** @constructor MyClass */",

    "deprecated":   "Mark as not being supported anymore.\n"
                    "Deprecated components should not be used, as they\n"
                    "will usually be removed in some future version.\n"
                    "Example: /** @deprecated */",

    "exception":    "Method call may throw this type of exception.\n"
                    "Note: Same as @throws.\n"
                    "Example: /** @exception MyException  Text of when thrown */",

    "extends":      "The base class this class extends.\n"
                    "Note: Same as @base.\n"
                    "Example: /** @extends ParentClass */",

    "fileoverview": "This documentation block will be used to provide\n"
                    "an overview for the current file.\n"
                    "Example: /** @fileoverview */",

    "final":        "Constant variable.\n"
                    "Example: /** @final */",

    "ignore":       "Item will be ignored by JSDoc.\n"
                    "Example: /** @ignore */",

    "member":       "This is a member of the named class.\n"
                    "Example: /** @member MyClass */",

    "namespace":    "Namespace where the element resides.\n"
                    "Example: /** @namespace code.util */",

    "param":        "Provide information about a function parameter.\n"
                    "Note: Same as @argument.\n"
                    "Example: /** @param arg1 {string}  The first argument */",

    "private":      "Member is private.\n"
                    "This means it will not be shown in any documentation.\n"
                    "Komodo's Code Browser shows this with a locked image.\n"
                    "Example: /** @private */",

    "requires":     "Define a dependency upon another class.\n"
                    "Example: /** @requires OtherClass  Because it does! */",

    "returns":      "Provide information about the return value of a function.\n"
                    "Example: /** @returns {array} An array of items. */",

    "static":       "Static member, only one instance ever defined.\n"
                    "Example: /** @static */",

    "see":          "Link to another class or function.\n"
                    "Example: /** @see ClassName#methodName */",

    "tags":         "User defined tag names.\n"
                    "Example: /** @tags testcase,knownfailure */",

    "throws":       "Method call may throw this type of exception.\n"
                    "Note: Same as @exception.\n"
                    "Example: /** @throws MyException  Text of when thrown */",

    "type":         "Variable type.\n"
                    "Example: /** @type String */",

    "version":      "Version number of the current file or class.\n"
                    "Example: /** @version 1.0.8 */",

}

class JSDocParameter:
    def __init__(self, paramname, paramtype=None, doc=None):
        self.paramname = paramname
        self.paramtype = paramtype
        self.doc = doc
    def __repr__(self):
        return "JSDocParameter: %r (%r) - %r" % (self.paramname, self.paramtype,
                                                 self.doc)

class JSDoc:
    A_CLASS = 0x01
    A_CONSTRUCTOR = 0x02
    A_PRIVATE = 0x04
    A_STATIC = 0x08
    A_CONSTANT = 0x10
    A_DEPRECATED = 0x20

    def __init__(self, comment=None):
        self._reset()
        if comment:
            # Full comment initially given
            #print "JSDoc comment: %r" % (comment)
            self.parse(comment)

    def __repr__(self):
        result = []
        if self.attributes:
            attrs = []
            if self.attributes & self.A_CLASS:
                if self.classname:
                    result.append("Classname:  %s" % (self.classname))
                else:
                    attrs.append("class")
            elif self.attributes & self.A_CONSTRUCTOR:
                attrs.append("constructor")
            elif self.attributes & self.A_PRIVATE:
                attrs.append("private")
            elif self.attributes & self.A_STATIC:
                attrs.append("static")
            elif self.attributes & self.A_CONSTANT:
                attrs.append("constant")
            elif self.attributes & self.A_DEPRECATED:
                attrs.append("deprecated")
            if len(attrs) > 0:
                result.append(" ".join(attrs))
        if self.namespace:
            result.append("Namespace:  %s" % (self.namespace))
        if self.baseclasses:
            result.append("baseclasses:  %s" % (self.baseclasses))
        for cp in self.params:
            result.append(str(cp))
        if self.type:
            result.append("Type:  %s" % (self.type))
        if self.tags:
            result.append("Tags:  %s" % (self.tags))
        if self.returns:
            result.append("Returns:  %s" % (str(self.returns)))
        if self.doc:
            result.append("Doc:\n" + self.doc)
        return "JSDoc:\n  %s" % ("\n  ".join(result))

    def _reset(self):
        self.comment = None
        self.baseclasses = []
        self.doc = None
        self.classname = None
        self.namespace = None
        self.type = None
        self.tags = None
        self.attributes = 0
        # params is a list of JSDocParameter's
        self.params = []
        # returns is a JSDocParameter (does not have a paramname though)
        self.returns = None

    def _getTypeField(self, value):
        # Examples:
        #  'int'
        #  '{String}'
        #  'boolean|Object'
        #  'Array[](Number[])'
        # YUI Example:
        #   * @param {<a href="http://www.w3.org/TR/2000/WD-DOM-Level-1-20000929/level-one-
        #   * html.html#ID-22445964">HTMLDivElement</a>} p_oElement Object specifying the 
        #   * <code>&#60;div&#62;</code> element of the context menu.
        if not value:
            return value

        # Only take first field if multiples are given
        pipePos = value.find('|')
        if pipePos > 0:
            value = value[:pipePos]

        value = value.strip()
        if value[-1] == "}":
            value = value[:-1]
            sp = value.split("{", 1)
            if len(sp) > 1:
                value = sp[1]
                sp = value.split(":", 1)
                if len(sp) > 1:
                    value = sp[1]
        # Added to remove YUI's href docs from the citdl type
        href_pos = value.find('<a href="')
        if href_pos >= 0:
            # We only want the href link text
            end_a_tag_pos = value.find('</a>')
            if end_a_tag_pos:
                value = value[:end_a_tag_pos]
                # Find matching close tag >
                href_pos = value.rfind('>')
                if href_pos >= 0:
                    value = value[href_pos+1:]

        # If a brace is in the value, it's an array
        bracePos = value.find("[")
        if bracePos >= 0:
            value = "Array"
        return value.strip()

    # Examples:
    #  "{Boolean}       true if the date is OOM"
    #  "el {HTMLElement} the element to animate"
    #  "{string}  sCategory  The log category for the message."
    def _getTypeFieldFromString(self, value):
        """Return tuple (type, rest of string)"""

        sp = value.split("{", 1)
        if len(sp) > 1:
            before = sp[0]
            value = sp[1]
            sp = value.split("}", 1)
            value = sp[0]
            if len(sp) > 1:
                after = sp[1]
                return (self._getTypeField(value), before + after)
        return (None, value)

    def _handle_base(self, value):
        self.baseclasses.append(value)

    # Same as base
    def _handle_extends(self, value):
        self._handle_base(value)

    def _handle_class(self, value):
        self.attributes |= self.A_CLASS
        self.classname = value

    def _handle_constructor(self, value):
        self.attributes |= self.A_CONSTRUCTOR

    def _handle_namespace(self, value):
        self.namespace = value

    def _handle_private(self, value):
        self.attributes |= self.A_PRIVATE

    def _handle_static(self, value):
        self.attributes |= self.A_STATIC

    def _handle_final(self, value):
        self.attributes |= self.A_CONSTANT

    def _handle_deprecated(self, value):
        self.attributes |= self.A_DEPRECATED

    def _handle_param(self, value):
        paramname = None
        paramtype = None
        doc = None
        sp = value.split(None, 2)
        for s in sp[:2]:
            if paramtype is None and s and s[0] == '{':
                # type information
                paramtype = self._getTypeField(s)
            elif paramname is None:
                paramname = s
        # Should have at least the paramname by now
        if paramname and paramtype:
            if len(sp) > 2:
                doc = sp[2]
            else:
                doc = None
        else:
            doc = " ".join(sp[1:3])
        cp = JSDocParameter(paramname, paramtype, doc)
        self.params.append(cp)

    def _handle_tags(self, value):
        self.tags = value

    def _handle_type(self, value):
        self.type = self._getTypeField(value)

    def _handle_return(self, value):
        returntype, doc = self._getTypeFieldFromString(value)
        if returntype:
            self.returns = JSDocParameter(None, returntype, doc)
    # Same as return
    def _handle_returns(self, value):
        return self._handle_return(value)

    def parse(self, comment):
        self._reset()
        self.comment = comment
        if not comment:
            return False
        in_doc = True
        doc = []
        lines = self.comment.splitlines(0)
        # Check to see if it's an actual javadoc
        isJSDoc = False
        # Once we reach the tags we don't add to the doc anymore, only
        # to the tags
        tagElements = []
        for line in lines:
            line = line.strip()
            #print "line: %r" % (line)
            if not isJSDoc:
                # Note: "*//**" style comes from the ciler using two comments
                # See bug: http://bugs.activestate.com/show_bug.cgi?id=68727
                if line == "/**" or line.endswith("*//**"):
                    # It looks like a javadoc from here
                    isJSDoc = True
            else:
                # It's a javadoc, so parse up the fields
                if line == "*/":
                    isJSDoc = False
                elif line.endswith("*//**"):
                    self._reset()
                    self.comment = comment
                elif line == "*":
                    doc.append("")
                elif len(line) > 2 and line[:2] == "* ":
                    sp = line.split(None, 1)
                    #print sp
                    if len(sp) > 1:
                        if sp[1][0] == '@':
                            # It's a javadoc field
                            #print sp
                            docfield = sp[1][1:]
                            sp = docfield.split(None, 1)
                            #print sp
                            #print "Tag: %r" % (sp[0])
                            if sp[0] == "description":
                                if len(sp) > 1:
                                    doc.append(sp[1])
                                in_doc = True
                            else:
                                tagElements.append(sp)
                                in_doc = False
                        elif tagElements and doc and not in_doc: # This is a continued param field
                            tagData = tagElements[-1]
                            if len(tagData) == 1:
                                tagData.append(sp[1])
                            else:
                                tagData[1] += "\n%s" % (sp[1])
                        else: # This is still the main doc string
                            doc.append(sp[1])
                            in_doc = True
        self.doc = "\n".join(doc).rstrip()
        # Parse the tags now
        for tagData in tagElements:
            handle_call = getattr(self, "_handle_%s" % (tagData[0]), None)
            if handle_call is not None:
                if len(tagData) == 1:
                    value = ""
                else:
                    value = tagData[1].strip()
                handle_call(value)
            # else: # We don't handle this param

    def isClass(self):
        return self.attributes & self.A_CLASS

    def isConstructor(self):
        return self.attributes & self.A_CONSTRUCTOR

    def isPrivate(self):
        return self.attributes & self.A_PRIVATE

    def isStatic(self):
        return self.attributes & self.A_STATIC

    def isConstant(self):
        return self.attributes & self.A_CONSTANT

    def isDeprecated(self):
        return self.attributes & self.A_DEPRECATED


############################################################
#                       Test code                          #
############################################################

def _test():
    sample_comment = """/**
 * Utility to set up the prototype, constructor and superclass properties to
 * support an inheritance strategy that can chain constructors and methods.
 *
 * @param {function} subclass   the object to modify
 * @param {function} superclass the object to inherit.
 *  Second line of param superclass doc.
 * @tags these,are,my,tags
 */
"""

    # Test the general usage of the class
    jd = JSDoc(sample_comment)
    assert(len(jd.params) == 2)
    assert(jd.params[0].paramname == "subclass")
    assert(jd.params[0].paramtype == "function")
    assert(jd.params[0].doc == "the object to modify")
    assert(jd.params[1].paramname == "superclass")
    assert(jd.params[1].paramtype == "function")
    assert(jd.params[1].doc == "the object to inherit.\nSecond line of param superclass doc.")
    assert(jd.tags == "these,are,my,tags")
    #print jd

    # Test specific internal functions of the class
    paramtype, doc = jd._getTypeFieldFromString("el {HTMLElement} the element to animate")
    assert(paramtype == "HTMLElement")
    assert(doc == "el  the element to animate")
    paramtype = jd._getTypeField("Array[](Number[])")
    assert(paramtype == "Array")
    paramtype = jd._getTypeField("Number|Array[])")
    assert(paramtype == "Number")

    jd._reset()
    jd._handle_param("{string}  sSource    The source of the the message (opt)")
    assert(len(jd.params) == 1 and \
           jd.params[0].paramname == "sSource" and \
           jd.params[0].paramtype == "string")

    jd._reset()
    jd._handle_param("oParent {Node} this node's parent node")
    assert(len(jd.params) == 1 and \
           jd.params[0].paramname == "oParent" and \
           jd.params[0].paramtype == "Node")

    jd._reset()
    jd._handle_returns("{array} Array of result objects")
    assert(jd.returns and \
           not jd.returns.paramname and \
           jd.returns.paramtype == "array")

    jd._reset()
    jd._handle_class("The superclass of all menu containers.")
    assert(jd.attributes & jd.A_CLASS)
    assert(jd.isClass())

    jd._reset()
    jd._handle_private("")
    assert(jd.attributes & jd.A_PRIVATE)
    assert(jd.isPrivate())

    jd._reset()
    jd._handle_static("")
    assert(jd.attributes & jd.A_STATIC)
    assert(jd.isStatic())

    jd._reset()
    jd._handle_constructor("")
    assert(jd.attributes & jd.A_CONSTRUCTOR)
    assert(jd.isConstructor())

    jd._reset()
    jd._handle_deprecated("")
    assert(jd.attributes & jd.A_DEPRECATED)
    assert(jd.isDeprecated())

    jd._reset()
    jd._handle_base("YAHOO.widget.Menu")
    assert("YAHOO.widget.Menu" in jd.baseclasses)
    jd._reset()
    jd._handle_extends("YAHOO.util.DragDrop")
    assert("YAHOO.util.DragDrop" in jd.baseclasses)

    jd._reset()
    jd._handle_type("YAHOO.widget.MenuModuleItem")
    assert(jd.type == "YAHOO.widget.MenuModuleItem")
    jd._reset()
    jd._handle_type("{HTMLImageElement}")
    assert(jd.type == "HTMLImageElement")

# Main function
def main():
    _test()

# When run from command line
if __name__ == '__main__':
    main()
