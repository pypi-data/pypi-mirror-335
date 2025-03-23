# Generated from BarePKParser.g4 by ANTLR 4.13.0
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,11,207,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        1,0,3,0,30,8,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,5,0,39,8,0,10,0,12,0,
        42,9,0,1,0,1,0,1,1,4,1,47,8,1,11,1,12,1,48,1,2,1,2,1,2,1,2,1,2,1,
        2,1,2,1,2,1,2,1,2,1,2,5,2,62,8,2,10,2,12,2,65,9,2,1,2,1,2,1,3,4,
        3,70,8,3,11,3,12,3,71,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,
        4,1,4,1,4,1,4,1,4,1,4,5,4,90,8,4,10,4,12,4,93,9,4,1,4,1,4,1,5,4,
        5,98,8,5,11,5,12,5,99,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,
        6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,5,6,123,8,6,10,6,12,6,
        126,9,6,1,6,1,6,1,7,4,7,131,8,7,11,7,12,7,132,1,8,1,8,1,8,1,8,1,
        8,1,8,1,8,1,8,1,8,5,8,144,8,8,10,8,12,8,147,9,8,1,8,1,8,1,9,4,9,
        152,8,9,11,9,12,9,153,1,10,1,10,1,10,1,10,1,10,1,10,1,10,1,10,1,
        10,1,10,1,10,1,10,1,10,5,10,169,8,10,10,10,12,10,172,9,10,1,10,1,
        10,1,11,4,11,177,8,11,11,11,12,11,178,1,12,1,12,1,12,1,12,1,12,1,
        12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,5,12,198,
        8,12,10,12,12,12,201,9,12,1,12,1,12,1,13,1,13,1,13,0,0,14,0,2,4,
        6,8,10,12,14,16,18,20,22,24,26,0,2,1,1,9,9,1,0,1,3,212,0,29,1,0,
        0,0,2,46,1,0,0,0,4,50,1,0,0,0,6,69,1,0,0,0,8,73,1,0,0,0,10,97,1,
        0,0,0,12,101,1,0,0,0,14,130,1,0,0,0,16,134,1,0,0,0,18,151,1,0,0,
        0,20,155,1,0,0,0,22,176,1,0,0,0,24,180,1,0,0,0,26,204,1,0,0,0,28,
        30,5,9,0,0,29,28,1,0,0,0,29,30,1,0,0,0,30,40,1,0,0,0,31,39,3,2,1,
        0,32,39,3,6,3,0,33,39,3,10,5,0,34,39,3,14,7,0,35,39,3,18,9,0,36,
        39,3,22,11,0,37,39,5,9,0,0,38,31,1,0,0,0,38,32,1,0,0,0,38,33,1,0,
        0,0,38,34,1,0,0,0,38,35,1,0,0,0,38,36,1,0,0,0,38,37,1,0,0,0,39,42,
        1,0,0,0,40,38,1,0,0,0,40,41,1,0,0,0,41,43,1,0,0,0,42,40,1,0,0,0,
        43,44,5,0,0,1,44,1,1,0,0,0,45,47,3,4,2,0,46,45,1,0,0,0,47,48,1,0,
        0,0,48,46,1,0,0,0,48,49,1,0,0,0,49,3,1,0,0,0,50,51,5,7,0,0,51,52,
        5,1,0,0,52,53,5,7,0,0,53,54,5,7,0,0,54,55,5,2,0,0,55,56,5,7,0,0,
        56,57,5,1,0,0,57,58,5,7,0,0,58,59,5,7,0,0,59,63,5,2,0,0,60,62,3,
        26,13,0,61,60,1,0,0,0,62,65,1,0,0,0,63,61,1,0,0,0,63,64,1,0,0,0,
        64,66,1,0,0,0,65,63,1,0,0,0,66,67,7,0,0,0,67,5,1,0,0,0,68,70,3,8,
        4,0,69,68,1,0,0,0,70,71,1,0,0,0,71,69,1,0,0,0,71,72,1,0,0,0,72,7,
        1,0,0,0,73,74,5,7,0,0,74,75,5,1,0,0,75,76,5,7,0,0,76,77,5,7,0,0,
        77,78,5,2,0,0,78,79,5,7,0,0,79,80,5,1,0,0,80,81,5,7,0,0,81,82,5,
        7,0,0,82,83,5,2,0,0,83,84,5,7,0,0,84,85,5,1,0,0,85,86,5,7,0,0,86,
        87,5,7,0,0,87,91,5,2,0,0,88,90,3,26,13,0,89,88,1,0,0,0,90,93,1,0,
        0,0,91,89,1,0,0,0,91,92,1,0,0,0,92,94,1,0,0,0,93,91,1,0,0,0,94,95,
        7,0,0,0,95,9,1,0,0,0,96,98,3,12,6,0,97,96,1,0,0,0,98,99,1,0,0,0,
        99,97,1,0,0,0,99,100,1,0,0,0,100,11,1,0,0,0,101,102,5,7,0,0,102,
        103,5,1,0,0,103,104,5,7,0,0,104,105,5,7,0,0,105,106,5,2,0,0,106,
        107,5,7,0,0,107,108,5,1,0,0,108,109,5,7,0,0,109,110,5,7,0,0,110,
        111,5,2,0,0,111,112,5,7,0,0,112,113,5,1,0,0,113,114,5,7,0,0,114,
        115,5,7,0,0,115,116,5,2,0,0,116,117,5,7,0,0,117,118,5,1,0,0,118,
        119,5,7,0,0,119,120,5,7,0,0,120,124,5,2,0,0,121,123,3,26,13,0,122,
        121,1,0,0,0,123,126,1,0,0,0,124,122,1,0,0,0,124,125,1,0,0,0,125,
        127,1,0,0,0,126,124,1,0,0,0,127,128,7,0,0,0,128,13,1,0,0,0,129,131,
        3,16,8,0,130,129,1,0,0,0,131,132,1,0,0,0,132,130,1,0,0,0,132,133,
        1,0,0,0,133,15,1,0,0,0,134,135,5,1,0,0,135,136,5,7,0,0,136,137,5,
        7,0,0,137,138,5,2,0,0,138,139,5,1,0,0,139,140,5,7,0,0,140,141,5,
        7,0,0,141,145,5,2,0,0,142,144,3,26,13,0,143,142,1,0,0,0,144,147,
        1,0,0,0,145,143,1,0,0,0,145,146,1,0,0,0,146,148,1,0,0,0,147,145,
        1,0,0,0,148,149,7,0,0,0,149,17,1,0,0,0,150,152,3,20,10,0,151,150,
        1,0,0,0,152,153,1,0,0,0,153,151,1,0,0,0,153,154,1,0,0,0,154,19,1,
        0,0,0,155,156,5,1,0,0,156,157,5,7,0,0,157,158,5,7,0,0,158,159,5,
        2,0,0,159,160,5,1,0,0,160,161,5,7,0,0,161,162,5,7,0,0,162,163,5,
        2,0,0,163,164,5,1,0,0,164,165,5,7,0,0,165,166,5,7,0,0,166,170,5,
        2,0,0,167,169,3,26,13,0,168,167,1,0,0,0,169,172,1,0,0,0,170,168,
        1,0,0,0,170,171,1,0,0,0,171,173,1,0,0,0,172,170,1,0,0,0,173,174,
        7,0,0,0,174,21,1,0,0,0,175,177,3,24,12,0,176,175,1,0,0,0,177,178,
        1,0,0,0,178,176,1,0,0,0,178,179,1,0,0,0,179,23,1,0,0,0,180,181,5,
        1,0,0,181,182,5,7,0,0,182,183,5,7,0,0,183,184,5,2,0,0,184,185,5,
        1,0,0,185,186,5,7,0,0,186,187,5,7,0,0,187,188,5,2,0,0,188,189,5,
        1,0,0,189,190,5,7,0,0,190,191,5,7,0,0,191,192,5,2,0,0,192,193,5,
        1,0,0,193,194,5,7,0,0,194,195,5,7,0,0,195,199,5,2,0,0,196,198,3,
        26,13,0,197,196,1,0,0,0,198,201,1,0,0,0,199,197,1,0,0,0,199,200,
        1,0,0,0,200,202,1,0,0,0,201,199,1,0,0,0,202,203,7,0,0,0,203,25,1,
        0,0,0,204,205,7,1,0,0,205,27,1,0,0,0,15,29,38,40,48,63,71,91,99,
        124,132,145,153,170,178,199
    ]

class BarePKParser ( Parser ):

    grammarFileName = "BarePKParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [  ]

    symbolicNames = [ "<INVALID>", "Integer", "Float", "Real", "SHARP_COMMENT", 
                      "EXCLM_COMMENT", "SMCLN_COMMENT", "Simple_name", "SPACE", 
                      "RETURN", "SECTION_COMMENT", "LINE_COMMENT" ]

    RULE_bare_pk = 0
    RULE_peak_list_2d = 1
    RULE_peak_2d = 2
    RULE_peak_list_3d = 3
    RULE_peak_3d = 4
    RULE_peak_list_4d = 5
    RULE_peak_4d = 6
    RULE_peak_list_wo_chain_2d = 7
    RULE_peak_wo_chain_2d = 8
    RULE_peak_list_wo_chain_3d = 9
    RULE_peak_wo_chain_3d = 10
    RULE_peak_list_wo_chain_4d = 11
    RULE_peak_wo_chain_4d = 12
    RULE_number = 13

    ruleNames =  [ "bare_pk", "peak_list_2d", "peak_2d", "peak_list_3d", 
                   "peak_3d", "peak_list_4d", "peak_4d", "peak_list_wo_chain_2d", 
                   "peak_wo_chain_2d", "peak_list_wo_chain_3d", "peak_wo_chain_3d", 
                   "peak_list_wo_chain_4d", "peak_wo_chain_4d", "number" ]

    EOF = Token.EOF
    Integer=1
    Float=2
    Real=3
    SHARP_COMMENT=4
    EXCLM_COMMENT=5
    SMCLN_COMMENT=6
    Simple_name=7
    SPACE=8
    RETURN=9
    SECTION_COMMENT=10
    LINE_COMMENT=11

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.0")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class Bare_pkContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(BarePKParser.EOF, 0)

        def RETURN(self, i:int=None):
            if i is None:
                return self.getTokens(BarePKParser.RETURN)
            else:
                return self.getToken(BarePKParser.RETURN, i)

        def peak_list_2d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BarePKParser.Peak_list_2dContext)
            else:
                return self.getTypedRuleContext(BarePKParser.Peak_list_2dContext,i)


        def peak_list_3d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BarePKParser.Peak_list_3dContext)
            else:
                return self.getTypedRuleContext(BarePKParser.Peak_list_3dContext,i)


        def peak_list_4d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BarePKParser.Peak_list_4dContext)
            else:
                return self.getTypedRuleContext(BarePKParser.Peak_list_4dContext,i)


        def peak_list_wo_chain_2d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BarePKParser.Peak_list_wo_chain_2dContext)
            else:
                return self.getTypedRuleContext(BarePKParser.Peak_list_wo_chain_2dContext,i)


        def peak_list_wo_chain_3d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BarePKParser.Peak_list_wo_chain_3dContext)
            else:
                return self.getTypedRuleContext(BarePKParser.Peak_list_wo_chain_3dContext,i)


        def peak_list_wo_chain_4d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BarePKParser.Peak_list_wo_chain_4dContext)
            else:
                return self.getTypedRuleContext(BarePKParser.Peak_list_wo_chain_4dContext,i)


        def getRuleIndex(self):
            return BarePKParser.RULE_bare_pk

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBare_pk" ):
                listener.enterBare_pk(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBare_pk" ):
                listener.exitBare_pk(self)




    def bare_pk(self):

        localctx = BarePKParser.Bare_pkContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_bare_pk)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 29
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,0,self._ctx)
            if la_ == 1:
                self.state = 28
                self.match(BarePKParser.RETURN)


            self.state = 40
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 642) != 0):
                self.state = 38
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
                if la_ == 1:
                    self.state = 31
                    self.peak_list_2d()
                    pass

                elif la_ == 2:
                    self.state = 32
                    self.peak_list_3d()
                    pass

                elif la_ == 3:
                    self.state = 33
                    self.peak_list_4d()
                    pass

                elif la_ == 4:
                    self.state = 34
                    self.peak_list_wo_chain_2d()
                    pass

                elif la_ == 5:
                    self.state = 35
                    self.peak_list_wo_chain_3d()
                    pass

                elif la_ == 6:
                    self.state = 36
                    self.peak_list_wo_chain_4d()
                    pass

                elif la_ == 7:
                    self.state = 37
                    self.match(BarePKParser.RETURN)
                    pass


                self.state = 42
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 43
            self.match(BarePKParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Peak_list_2dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def peak_2d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BarePKParser.Peak_2dContext)
            else:
                return self.getTypedRuleContext(BarePKParser.Peak_2dContext,i)


        def getRuleIndex(self):
            return BarePKParser.RULE_peak_list_2d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPeak_list_2d" ):
                listener.enterPeak_list_2d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPeak_list_2d" ):
                listener.exitPeak_list_2d(self)




    def peak_list_2d(self):

        localctx = BarePKParser.Peak_list_2dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_peak_list_2d)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 46 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 45
                    self.peak_2d()

                else:
                    raise NoViableAltException(self)
                self.state = 48 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,3,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Peak_2dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Simple_name(self, i:int=None):
            if i is None:
                return self.getTokens(BarePKParser.Simple_name)
            else:
                return self.getToken(BarePKParser.Simple_name, i)

        def Integer(self, i:int=None):
            if i is None:
                return self.getTokens(BarePKParser.Integer)
            else:
                return self.getToken(BarePKParser.Integer, i)

        def Float(self, i:int=None):
            if i is None:
                return self.getTokens(BarePKParser.Float)
            else:
                return self.getToken(BarePKParser.Float, i)

        def RETURN(self):
            return self.getToken(BarePKParser.RETURN, 0)

        def EOF(self):
            return self.getToken(BarePKParser.EOF, 0)

        def number(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BarePKParser.NumberContext)
            else:
                return self.getTypedRuleContext(BarePKParser.NumberContext,i)


        def getRuleIndex(self):
            return BarePKParser.RULE_peak_2d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPeak_2d" ):
                listener.enterPeak_2d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPeak_2d" ):
                listener.exitPeak_2d(self)




    def peak_2d(self):

        localctx = BarePKParser.Peak_2dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_peak_2d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 50
            self.match(BarePKParser.Simple_name)
            self.state = 51
            self.match(BarePKParser.Integer)
            self.state = 52
            self.match(BarePKParser.Simple_name)
            self.state = 53
            self.match(BarePKParser.Simple_name)
            self.state = 54
            self.match(BarePKParser.Float)
            self.state = 55
            self.match(BarePKParser.Simple_name)
            self.state = 56
            self.match(BarePKParser.Integer)
            self.state = 57
            self.match(BarePKParser.Simple_name)
            self.state = 58
            self.match(BarePKParser.Simple_name)
            self.state = 59
            self.match(BarePKParser.Float)
            self.state = 63
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 14) != 0):
                self.state = 60
                self.number()
                self.state = 65
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 66
            _la = self._input.LA(1)
            if not(_la==-1 or _la==9):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Peak_list_3dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def peak_3d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BarePKParser.Peak_3dContext)
            else:
                return self.getTypedRuleContext(BarePKParser.Peak_3dContext,i)


        def getRuleIndex(self):
            return BarePKParser.RULE_peak_list_3d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPeak_list_3d" ):
                listener.enterPeak_list_3d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPeak_list_3d" ):
                listener.exitPeak_list_3d(self)




    def peak_list_3d(self):

        localctx = BarePKParser.Peak_list_3dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_peak_list_3d)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 69 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 68
                    self.peak_3d()

                else:
                    raise NoViableAltException(self)
                self.state = 71 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,5,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Peak_3dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Simple_name(self, i:int=None):
            if i is None:
                return self.getTokens(BarePKParser.Simple_name)
            else:
                return self.getToken(BarePKParser.Simple_name, i)

        def Integer(self, i:int=None):
            if i is None:
                return self.getTokens(BarePKParser.Integer)
            else:
                return self.getToken(BarePKParser.Integer, i)

        def Float(self, i:int=None):
            if i is None:
                return self.getTokens(BarePKParser.Float)
            else:
                return self.getToken(BarePKParser.Float, i)

        def RETURN(self):
            return self.getToken(BarePKParser.RETURN, 0)

        def EOF(self):
            return self.getToken(BarePKParser.EOF, 0)

        def number(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BarePKParser.NumberContext)
            else:
                return self.getTypedRuleContext(BarePKParser.NumberContext,i)


        def getRuleIndex(self):
            return BarePKParser.RULE_peak_3d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPeak_3d" ):
                listener.enterPeak_3d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPeak_3d" ):
                listener.exitPeak_3d(self)




    def peak_3d(self):

        localctx = BarePKParser.Peak_3dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_peak_3d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 73
            self.match(BarePKParser.Simple_name)
            self.state = 74
            self.match(BarePKParser.Integer)
            self.state = 75
            self.match(BarePKParser.Simple_name)
            self.state = 76
            self.match(BarePKParser.Simple_name)
            self.state = 77
            self.match(BarePKParser.Float)
            self.state = 78
            self.match(BarePKParser.Simple_name)
            self.state = 79
            self.match(BarePKParser.Integer)
            self.state = 80
            self.match(BarePKParser.Simple_name)
            self.state = 81
            self.match(BarePKParser.Simple_name)
            self.state = 82
            self.match(BarePKParser.Float)
            self.state = 83
            self.match(BarePKParser.Simple_name)
            self.state = 84
            self.match(BarePKParser.Integer)
            self.state = 85
            self.match(BarePKParser.Simple_name)
            self.state = 86
            self.match(BarePKParser.Simple_name)
            self.state = 87
            self.match(BarePKParser.Float)
            self.state = 91
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 14) != 0):
                self.state = 88
                self.number()
                self.state = 93
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 94
            _la = self._input.LA(1)
            if not(_la==-1 or _la==9):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Peak_list_4dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def peak_4d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BarePKParser.Peak_4dContext)
            else:
                return self.getTypedRuleContext(BarePKParser.Peak_4dContext,i)


        def getRuleIndex(self):
            return BarePKParser.RULE_peak_list_4d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPeak_list_4d" ):
                listener.enterPeak_list_4d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPeak_list_4d" ):
                listener.exitPeak_list_4d(self)




    def peak_list_4d(self):

        localctx = BarePKParser.Peak_list_4dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_peak_list_4d)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 97 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 96
                    self.peak_4d()

                else:
                    raise NoViableAltException(self)
                self.state = 99 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,7,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Peak_4dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Simple_name(self, i:int=None):
            if i is None:
                return self.getTokens(BarePKParser.Simple_name)
            else:
                return self.getToken(BarePKParser.Simple_name, i)

        def Integer(self, i:int=None):
            if i is None:
                return self.getTokens(BarePKParser.Integer)
            else:
                return self.getToken(BarePKParser.Integer, i)

        def Float(self, i:int=None):
            if i is None:
                return self.getTokens(BarePKParser.Float)
            else:
                return self.getToken(BarePKParser.Float, i)

        def RETURN(self):
            return self.getToken(BarePKParser.RETURN, 0)

        def EOF(self):
            return self.getToken(BarePKParser.EOF, 0)

        def number(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BarePKParser.NumberContext)
            else:
                return self.getTypedRuleContext(BarePKParser.NumberContext,i)


        def getRuleIndex(self):
            return BarePKParser.RULE_peak_4d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPeak_4d" ):
                listener.enterPeak_4d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPeak_4d" ):
                listener.exitPeak_4d(self)




    def peak_4d(self):

        localctx = BarePKParser.Peak_4dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_peak_4d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 101
            self.match(BarePKParser.Simple_name)
            self.state = 102
            self.match(BarePKParser.Integer)
            self.state = 103
            self.match(BarePKParser.Simple_name)
            self.state = 104
            self.match(BarePKParser.Simple_name)
            self.state = 105
            self.match(BarePKParser.Float)
            self.state = 106
            self.match(BarePKParser.Simple_name)
            self.state = 107
            self.match(BarePKParser.Integer)
            self.state = 108
            self.match(BarePKParser.Simple_name)
            self.state = 109
            self.match(BarePKParser.Simple_name)
            self.state = 110
            self.match(BarePKParser.Float)
            self.state = 111
            self.match(BarePKParser.Simple_name)
            self.state = 112
            self.match(BarePKParser.Integer)
            self.state = 113
            self.match(BarePKParser.Simple_name)
            self.state = 114
            self.match(BarePKParser.Simple_name)
            self.state = 115
            self.match(BarePKParser.Float)
            self.state = 116
            self.match(BarePKParser.Simple_name)
            self.state = 117
            self.match(BarePKParser.Integer)
            self.state = 118
            self.match(BarePKParser.Simple_name)
            self.state = 119
            self.match(BarePKParser.Simple_name)
            self.state = 120
            self.match(BarePKParser.Float)
            self.state = 124
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 14) != 0):
                self.state = 121
                self.number()
                self.state = 126
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 127
            _la = self._input.LA(1)
            if not(_la==-1 or _la==9):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Peak_list_wo_chain_2dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def peak_wo_chain_2d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BarePKParser.Peak_wo_chain_2dContext)
            else:
                return self.getTypedRuleContext(BarePKParser.Peak_wo_chain_2dContext,i)


        def getRuleIndex(self):
            return BarePKParser.RULE_peak_list_wo_chain_2d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPeak_list_wo_chain_2d" ):
                listener.enterPeak_list_wo_chain_2d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPeak_list_wo_chain_2d" ):
                listener.exitPeak_list_wo_chain_2d(self)




    def peak_list_wo_chain_2d(self):

        localctx = BarePKParser.Peak_list_wo_chain_2dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_peak_list_wo_chain_2d)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 130 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 129
                    self.peak_wo_chain_2d()

                else:
                    raise NoViableAltException(self)
                self.state = 132 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,9,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Peak_wo_chain_2dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self, i:int=None):
            if i is None:
                return self.getTokens(BarePKParser.Integer)
            else:
                return self.getToken(BarePKParser.Integer, i)

        def Simple_name(self, i:int=None):
            if i is None:
                return self.getTokens(BarePKParser.Simple_name)
            else:
                return self.getToken(BarePKParser.Simple_name, i)

        def Float(self, i:int=None):
            if i is None:
                return self.getTokens(BarePKParser.Float)
            else:
                return self.getToken(BarePKParser.Float, i)

        def RETURN(self):
            return self.getToken(BarePKParser.RETURN, 0)

        def EOF(self):
            return self.getToken(BarePKParser.EOF, 0)

        def number(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BarePKParser.NumberContext)
            else:
                return self.getTypedRuleContext(BarePKParser.NumberContext,i)


        def getRuleIndex(self):
            return BarePKParser.RULE_peak_wo_chain_2d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPeak_wo_chain_2d" ):
                listener.enterPeak_wo_chain_2d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPeak_wo_chain_2d" ):
                listener.exitPeak_wo_chain_2d(self)




    def peak_wo_chain_2d(self):

        localctx = BarePKParser.Peak_wo_chain_2dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_peak_wo_chain_2d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 134
            self.match(BarePKParser.Integer)
            self.state = 135
            self.match(BarePKParser.Simple_name)
            self.state = 136
            self.match(BarePKParser.Simple_name)
            self.state = 137
            self.match(BarePKParser.Float)
            self.state = 138
            self.match(BarePKParser.Integer)
            self.state = 139
            self.match(BarePKParser.Simple_name)
            self.state = 140
            self.match(BarePKParser.Simple_name)
            self.state = 141
            self.match(BarePKParser.Float)
            self.state = 145
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 14) != 0):
                self.state = 142
                self.number()
                self.state = 147
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 148
            _la = self._input.LA(1)
            if not(_la==-1 or _la==9):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Peak_list_wo_chain_3dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def peak_wo_chain_3d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BarePKParser.Peak_wo_chain_3dContext)
            else:
                return self.getTypedRuleContext(BarePKParser.Peak_wo_chain_3dContext,i)


        def getRuleIndex(self):
            return BarePKParser.RULE_peak_list_wo_chain_3d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPeak_list_wo_chain_3d" ):
                listener.enterPeak_list_wo_chain_3d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPeak_list_wo_chain_3d" ):
                listener.exitPeak_list_wo_chain_3d(self)




    def peak_list_wo_chain_3d(self):

        localctx = BarePKParser.Peak_list_wo_chain_3dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_peak_list_wo_chain_3d)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 151 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 150
                    self.peak_wo_chain_3d()

                else:
                    raise NoViableAltException(self)
                self.state = 153 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,11,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Peak_wo_chain_3dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self, i:int=None):
            if i is None:
                return self.getTokens(BarePKParser.Integer)
            else:
                return self.getToken(BarePKParser.Integer, i)

        def Simple_name(self, i:int=None):
            if i is None:
                return self.getTokens(BarePKParser.Simple_name)
            else:
                return self.getToken(BarePKParser.Simple_name, i)

        def Float(self, i:int=None):
            if i is None:
                return self.getTokens(BarePKParser.Float)
            else:
                return self.getToken(BarePKParser.Float, i)

        def RETURN(self):
            return self.getToken(BarePKParser.RETURN, 0)

        def EOF(self):
            return self.getToken(BarePKParser.EOF, 0)

        def number(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BarePKParser.NumberContext)
            else:
                return self.getTypedRuleContext(BarePKParser.NumberContext,i)


        def getRuleIndex(self):
            return BarePKParser.RULE_peak_wo_chain_3d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPeak_wo_chain_3d" ):
                listener.enterPeak_wo_chain_3d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPeak_wo_chain_3d" ):
                listener.exitPeak_wo_chain_3d(self)




    def peak_wo_chain_3d(self):

        localctx = BarePKParser.Peak_wo_chain_3dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_peak_wo_chain_3d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 155
            self.match(BarePKParser.Integer)
            self.state = 156
            self.match(BarePKParser.Simple_name)
            self.state = 157
            self.match(BarePKParser.Simple_name)
            self.state = 158
            self.match(BarePKParser.Float)
            self.state = 159
            self.match(BarePKParser.Integer)
            self.state = 160
            self.match(BarePKParser.Simple_name)
            self.state = 161
            self.match(BarePKParser.Simple_name)
            self.state = 162
            self.match(BarePKParser.Float)
            self.state = 163
            self.match(BarePKParser.Integer)
            self.state = 164
            self.match(BarePKParser.Simple_name)
            self.state = 165
            self.match(BarePKParser.Simple_name)
            self.state = 166
            self.match(BarePKParser.Float)
            self.state = 170
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 14) != 0):
                self.state = 167
                self.number()
                self.state = 172
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 173
            _la = self._input.LA(1)
            if not(_la==-1 or _la==9):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Peak_list_wo_chain_4dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def peak_wo_chain_4d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BarePKParser.Peak_wo_chain_4dContext)
            else:
                return self.getTypedRuleContext(BarePKParser.Peak_wo_chain_4dContext,i)


        def getRuleIndex(self):
            return BarePKParser.RULE_peak_list_wo_chain_4d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPeak_list_wo_chain_4d" ):
                listener.enterPeak_list_wo_chain_4d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPeak_list_wo_chain_4d" ):
                listener.exitPeak_list_wo_chain_4d(self)




    def peak_list_wo_chain_4d(self):

        localctx = BarePKParser.Peak_list_wo_chain_4dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_peak_list_wo_chain_4d)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 176 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 175
                    self.peak_wo_chain_4d()

                else:
                    raise NoViableAltException(self)
                self.state = 178 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,13,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Peak_wo_chain_4dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self, i:int=None):
            if i is None:
                return self.getTokens(BarePKParser.Integer)
            else:
                return self.getToken(BarePKParser.Integer, i)

        def Simple_name(self, i:int=None):
            if i is None:
                return self.getTokens(BarePKParser.Simple_name)
            else:
                return self.getToken(BarePKParser.Simple_name, i)

        def Float(self, i:int=None):
            if i is None:
                return self.getTokens(BarePKParser.Float)
            else:
                return self.getToken(BarePKParser.Float, i)

        def RETURN(self):
            return self.getToken(BarePKParser.RETURN, 0)

        def EOF(self):
            return self.getToken(BarePKParser.EOF, 0)

        def number(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BarePKParser.NumberContext)
            else:
                return self.getTypedRuleContext(BarePKParser.NumberContext,i)


        def getRuleIndex(self):
            return BarePKParser.RULE_peak_wo_chain_4d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPeak_wo_chain_4d" ):
                listener.enterPeak_wo_chain_4d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPeak_wo_chain_4d" ):
                listener.exitPeak_wo_chain_4d(self)




    def peak_wo_chain_4d(self):

        localctx = BarePKParser.Peak_wo_chain_4dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_peak_wo_chain_4d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 180
            self.match(BarePKParser.Integer)
            self.state = 181
            self.match(BarePKParser.Simple_name)
            self.state = 182
            self.match(BarePKParser.Simple_name)
            self.state = 183
            self.match(BarePKParser.Float)
            self.state = 184
            self.match(BarePKParser.Integer)
            self.state = 185
            self.match(BarePKParser.Simple_name)
            self.state = 186
            self.match(BarePKParser.Simple_name)
            self.state = 187
            self.match(BarePKParser.Float)
            self.state = 188
            self.match(BarePKParser.Integer)
            self.state = 189
            self.match(BarePKParser.Simple_name)
            self.state = 190
            self.match(BarePKParser.Simple_name)
            self.state = 191
            self.match(BarePKParser.Float)
            self.state = 192
            self.match(BarePKParser.Integer)
            self.state = 193
            self.match(BarePKParser.Simple_name)
            self.state = 194
            self.match(BarePKParser.Simple_name)
            self.state = 195
            self.match(BarePKParser.Float)
            self.state = 199
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 14) != 0):
                self.state = 196
                self.number()
                self.state = 201
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 202
            _la = self._input.LA(1)
            if not(_la==-1 or _la==9):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NumberContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Float(self):
            return self.getToken(BarePKParser.Float, 0)

        def Real(self):
            return self.getToken(BarePKParser.Real, 0)

        def Integer(self):
            return self.getToken(BarePKParser.Integer, 0)

        def getRuleIndex(self):
            return BarePKParser.RULE_number

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNumber" ):
                listener.enterNumber(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNumber" ):
                listener.exitNumber(self)




    def number(self):

        localctx = BarePKParser.NumberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_number)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 204
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 14) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





