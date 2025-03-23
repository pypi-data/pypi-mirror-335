##
# CnsMRReader.py
#
# Update:
##
""" A collection of classes for parsing CNS MR files.
"""
__docformat__ = "restructuredtext en"
__author__ = "Masashi Yokochi"
__email__ = "yokochi@protein.osaka-u.ac.jp"
__license__ = "Apache License 2.0"
__version__ = "1.0.0"

import sys
import os

from antlr4 import InputStream, CommonTokenStream, ParseTreeWalker, PredictionMode
from typing import IO, List, Tuple, Optional

try:
    from wwpdb.utils.nmr.mr.LexerErrorListener import LexerErrorListener
    from wwpdb.utils.nmr.mr.ParserErrorListener import ParserErrorListener
    from wwpdb.utils.nmr.mr.CnsMRLexer import CnsMRLexer
    from wwpdb.utils.nmr.mr.CnsMRParser import CnsMRParser
    from wwpdb.utils.nmr.mr.CnsMRParserListener import CnsMRParserListener
    from wwpdb.utils.nmr.mr.ParserListenerUtil import (coordAssemblyChecker,
                                                       MAX_ERROR_REPORT,
                                                       REPRESENTATIVE_MODEL_ID,
                                                       REPRESENTATIVE_ALT_ID)
    from wwpdb.utils.nmr.io.CifReader import CifReader
    from wwpdb.utils.nmr.ChemCompUtil import ChemCompUtil
    from wwpdb.utils.nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from wwpdb.utils.nmr.nef.NEFTranslator import NEFTranslator
except ImportError:
    from nmr.mr.LexerErrorListener import LexerErrorListener
    from nmr.mr.ParserErrorListener import ParserErrorListener
    from nmr.mr.CnsMRLexer import CnsMRLexer
    from nmr.mr.CnsMRParser import CnsMRParser
    from nmr.mr.CnsMRParserListener import CnsMRParserListener
    from nmr.mr.ParserListenerUtil import (coordAssemblyChecker,
                                           MAX_ERROR_REPORT,
                                           REPRESENTATIVE_MODEL_ID,
                                           REPRESENTATIVE_ALT_ID)
    from nmr.io.CifReader import CifReader
    from nmr.ChemCompUtil import ChemCompUtil
    from nmr.BMRBChemShiftStat import BMRBChemShiftStat
    from nmr.nef.NEFTranslator import NEFTranslator


class CnsMRReader:
    """ Accessor methods for parsing CNS MR files.
    """

    def __init__(self, verbose: bool = True, log: IO = sys.stdout,
                 representativeModelId: int = REPRESENTATIVE_MODEL_ID,
                 representativeAltId: str = REPRESENTATIVE_ALT_ID,
                 mrAtomNameMapping: Optional[List[dict]] = None,
                 cR: Optional[CifReader] = None, caC: Optional[dict] = None, ccU: Optional[ChemCompUtil] = None,
                 csStat: Optional[BMRBChemShiftStat] = None, nefT: Optional[NEFTranslator] = None,
                 reasons: Optional[dict] = None):
        self.__class_name__ = self.__class__.__name__
        self.__version__ = __version__

        self.__verbose = verbose
        self.__lfh = log
        self.__debug = False
        self.__sll_pred = False

        self.__maxLexerErrorReport = MAX_ERROR_REPORT
        self.__maxParserErrorReport = MAX_ERROR_REPORT

        self.__representativeModelId = representativeModelId
        self.__representativeAltId = representativeAltId
        self.__mrAtomNameMapping = mrAtomNameMapping

        # CCD accessing utility
        self.__ccU = ChemCompUtil(verbose, log) if ccU is None else ccU

        if cR is not None and caC is None:
            caC = coordAssemblyChecker(verbose, log, representativeModelId, representativeAltId,
                                       cR, self.__ccU, None, None, fullCheck=False)

        self.__cR = cR
        self.__caC = caC

        # BMRB chemical shift statistics
        self.__csStat = BMRBChemShiftStat(verbose, log, self.__ccU) if csStat is None else csStat

        # NEFTranslator
        self.__nefT = NEFTranslator(verbose, log, self.__ccU, self.__csStat) if nefT is None else nefT
        if nefT is None:
            self.__nefT.set_remediation_mode(True)

        # reasons for re-parsing request from the previous trial
        self.__reasons = reasons

    def setDebugMode(self, debug: bool):
        self.__debug = debug

    def setLexerMaxErrorReport(self, maxErrReport: int):
        self.__maxLexerErrorReport = maxErrReport

    def setParserMaxErrorReport(self, maxErrReport: int):
        self.__maxParserErrorReport = maxErrReport

    def setSllPredMode(self, sll_pred: bool):
        self.__sll_pred = sll_pred

    def parse(self, mrFilePath: str, cifFilePath: Optional[str] = None, isFilePath: bool = True,
              createSfDict: bool = False, originalFileName: Optional[str] = None, listIdCounter: Optional[dict] = None, entryId: Optional[str] = None
              ) -> Tuple[Optional[CnsMRParserListener], Optional[ParserErrorListener], Optional[LexerErrorListener]]:
        """ Parse CNS MR file.
            @return: CnsMRParserListener for success or None otherwise, ParserErrorListener, LexerErrorListener.
        """

        ifh = None

        try:

            if isFilePath:
                mrString = None

                if not os.access(mrFilePath, os.R_OK):
                    if self.__verbose:
                        self.__lfh.write(f"+{self.__class_name__}.parse() {mrFilePath} is not accessible.\n")
                    return None, None, None

                ifh = open(mrFilePath, 'r')  # pylint: disable=consider-using-with
                input = InputStream(ifh.read())

            else:
                mrFilePath, mrString = None, mrFilePath

                if mrString is None or len(mrString) == 0:
                    if self.__verbose:
                        self.__lfh.write(f"+{self.__class_name__}.parse() Empty string.\n")
                    return None, None, None

                input = InputStream(mrString)

            if cifFilePath is not None:
                if not os.access(cifFilePath, os.R_OK):
                    if self.__verbose:
                        self.__lfh.write(f"+{self.__class_name__}.parse() {cifFilePath} is not accessible.\n")
                    return None, None, None

                if self.__cR is None:
                    self.__cR = CifReader(self.__verbose, self.__lfh)
                    if not self.__cR.parse(cifFilePath):
                        return None, None, None

            lexer = CnsMRLexer(input)
            lexer.removeErrorListeners()

            lexer_error_listener = LexerErrorListener(mrFilePath, maxErrorReport=self.__maxLexerErrorReport)
            lexer.addErrorListener(lexer_error_listener)

            messageList = lexer_error_listener.getMessageList()

            if messageList is not None and self.__verbose:
                for description in messageList:
                    self.__lfh.write(f"[Syntax error] line {description['line_number']}:{description['column_position']} {description['message']}\n")
                    if 'input' in description:
                        self.__lfh.write(f"{description['input']}\n")
                        self.__lfh.write(f"{description['marker']}\n")

            stream = CommonTokenStream(lexer)
            parser = CnsMRParser(stream)
            if not isFilePath or self.__sll_pred:
                parser._interp.predictionMode = PredictionMode.SLL  # pylint: disable=protected-access
            parser.removeErrorListeners()
            parser_error_listener = ParserErrorListener(mrFilePath, maxErrorReport=self.__maxParserErrorReport)
            parser.addErrorListener(parser_error_listener)
            tree = parser.cns_mr()

            walker = ParseTreeWalker()
            listener = CnsMRParserListener(self.__verbose, self.__lfh,
                                           self.__representativeModelId,
                                           self.__representativeAltId,
                                           self.__mrAtomNameMapping,
                                           self.__cR, self.__caC,
                                           self.__ccU, self.__csStat, self.__nefT,
                                           self.__reasons)
            listener.setDebugMode(self.__debug)
            listener.createSfDict(createSfDict)
            if createSfDict:
                if originalFileName is not None:
                    listener.setOriginaFileName(originalFileName)
                if listIdCounter is not None:
                    listener.setListIdCounter(listIdCounter)
                if entryId is not None:
                    listener.setEntryId(entryId)
            walker.walk(listener, tree)

            messageList = parser_error_listener.getMessageList()

            if messageList is not None and self.__verbose:
                for description in messageList:
                    self.__lfh.write(f"[Syntax error] line {description['line_number']}:{description['column_position']} {description['message']}\n")
                    if 'input' in description:
                        self.__lfh.write(f"{description['input']}\n")
                        self.__lfh.write(f"{description['marker']}\n")

            if self.__verbose and self.__debug:
                if listener.warningMessage is not None and len(listener.warningMessage) > 0:
                    self.__lfh.write(f"+{self.__class_name__}.parse() ++ Info  -\n" + '\n'.join(listener.warningMessage) + '\n')
                if isFilePath:
                    self.__lfh.write(f"+{self.__class_name__}.parse() ++ Info  - {listener.getContentSubtype()}\n")

            return listener, parser_error_listener, lexer_error_listener

        except IOError as e:
            if self.__verbose:
                self.__lfh.write(f"+{self.__class_name__}.parse() ++ Error  - {str(e)}\n")
            return None, None, None
        finally:
            if isFilePath and ifh is not None:
                ifh.close()


if __name__ == "__main__":
    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/5kp0/cterm_ab_noe.tbl-corrected',
                     '../../tests-nmr/mock-data-remediation/5kp0/5kp0.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6xmn/6xmn-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/6xmn/6xmn.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6xmn/6xmn-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/6xmn/6xmn.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2k3c/2k3c-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2k3c/2k3c.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2k3c/2k3c-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2k3c/2k3c.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2rvb/2rvb-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2rvb/2rvb.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7qlf/noes.tbl',
                     '../../tests-nmr/mock-data-remediation/7qlf/7qlf.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2l8i/2l8i-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2l8i/2l8i.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7t1p/7t1p-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/7t1p/7t1p.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2nbl/2nbl-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2nbl/2nbl.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mlx/2mlx-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2mlx/2mlx.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6ggz/unambig.tbl',
                     '../../tests-nmr/mock-data-remediation/6ggz/6ggz.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-daother-8751/2nd_case/D_1292132188_mr-upload_P1.cns.V1',
                     '../../tests-nmr/mock-data-daother-8751/2nd_case/D_800600_model_P1.cif.V3')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2kid/2kid-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2kid/2kid.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2kid/2kid-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2kid/2kid.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2n1o/2n1o-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2n1o/2n1o.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2n2w/2n2w-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2n2w/2n2w.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2n2w/2n2w-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2n2w/2n2w.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7cwh/Rack_noe_all.tbl',
                     '../../tests-nmr/mock-data-remediation/7cwh/7cwh.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2l11/2l11-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2l11/2l11.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2n3r/2n3r-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2n3r/2n3r.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2n3r/2n3r-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2n3r/2n3r.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lfr/2lfr-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2lfr/2lfr.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lfr/2lfr-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2lfr/2lfr.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2n30/2n30-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2n30/2n30.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/5xv8/170307_UVSSA-TFIIHp62.tbl-corrected',
                     '../../tests-nmr/mock-data-remediation/5xv8/5xv8.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lwn/2lwn-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2lwn/2lwn.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lwn/2lwn-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2lwn/2lwn.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6cc9/NOE_cmpd2_run30_ambig.tbl',
                     '../../tests-nmr/mock-data-remediation/6cc9/6cc9.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lp4/2lp4-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2lp4/2lp4.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lp4/2lp4-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2lp4/2lp4.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2k7v/2k7v-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2k7v/2k7v.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2k7v/2k7v-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2k7v/2k7v.cif')
    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2ms7/2ms7-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2ms7/2ms7.cif')
    print(reader_listener.getReasonsForReparsing())

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lpe/2lpe-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2lpe/2lpe.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lpe/2lpe-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2lpe/2lpe.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mrp/2mrp-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2mrp/2mrp.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mrp/2mrp-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2mrp/2mrp.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6zbi/allNOEs.tbl',
                     '../../tests-nmr/mock-data-remediation/6zbi/6zbi.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6zbi/allNOEs.tbl',
                 '../../tests-nmr/mock-data-remediation/6zbi/6zbi.cif')

    reader = CnsMRReader(True, reasons={'global_auth_sequence_offset': {'B': 35}})
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7f7x/f1f_cnoe.tab-corrected',
                     '../../tests-nmr/mock-data-remediation/7f7x/7f7x.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7f7x/pUbrl-UBA-NOE.tab-corrected',
                     '../../tests-nmr/mock-data-remediation/7f7x/7f7x.cif')
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/7f7x/pUbrl-UBA-NOE.tab-corrected',
                 '../../tests-nmr/mock-data-remediation/7f7x/7f7x.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lbu/2lbu-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2lbu/2lbu.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2n4n/2n4n-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2n4n/2n4n.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mnz/2mnz-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2mnz/2mnz.cif')
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mnz/2mnz-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2mnz/2mnz.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2lwe/2lwe-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2lwe/2lwe.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6ttc/ambig.tbl',
                     '../../tests-nmr/mock-data-remediation/6ttc/6ttc.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/4cyk/4cyk-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/4cyk/4cyk.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6vl2/restraint_file-corrected',
                     '../../tests-nmr/mock-data-remediation/6vl2/6vl2.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2ljc/2ljc-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2ljc/2ljc.cif')
    print(reader_listener.getReasonsForReparsing())
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2ljc/2ljc-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2ljc/2ljc.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/5y95/5y95-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/5y95/5y95.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/7mqu/ambig.tbl',
                     '../../tests-nmr/mock-data-remediation/7mqu/7mqu.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2l5y/test.mr',
                     '../../tests-nmr/mock-data-remediation/2l5y/2l5y.cif')
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2l5y/test.mr',
                 '../../tests-nmr/mock-data-remediation/2l5y/2l5y.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lsz/2lsz-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2lsz/2lsz.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/7dvm/7dvm-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/7dvm/7dvm.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2k9e/2k9e-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2k9e/2k9e.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/8ht7/dihe_f.tbl-corrected',
                 '../../tests-nmr/mock-data-remediation/8ht7/8ht7.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mgt/2mgt-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2mgt/2mgt.cif')
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mgt/2mgt-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2mgt/2mgt.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/5kmz/5kmz-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/5kmz/5kmz.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/7yhh/all.tbl',
                 '../../tests-nmr/mock-data-remediation/7yhh/7yhh.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2mhm/2mhm-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/2mhm/2mhm.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6pts/run6_unambig.tbl-corrected',
                 '../../tests-nmr/mock-data-remediation/6pts/6pts.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6feg/03_NOEs_ambig.tbl',
                     '../../tests-nmr/mock-data-remediation/6feg/6feg.cif')
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6feg/03_NOEs_ambig.tbl',
                 '../../tests-nmr/mock-data-remediation/6feg/6feg.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/6gpi/distance_res.tbl-corrected',
                     '../../tests-nmr/mock-data-remediation/6gpi/6gpi.cif')
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6gpi/distance_res.tbl-corrected',
                 '../../tests-nmr/mock-data-remediation/6gpi/6gpi.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-daother-9063/4_mercaptophenol_a3c_NOE_restaints.txt',
                     '../../tests-nmr/mock-data-daother-9063/D_800642_model_P1.cif.V15')
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-daother-9063/4_mercaptophenol_a3c_NOE_restaints.txt',
                 '../../tests-nmr/mock-data-daother-9063/D_800642_model_P1.cif.V15')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2ju4/2ju4-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2ju4/2ju4.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2k4l/2k4l-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2k4l/2k4l.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mlb/test.mr',
                 '../../tests-nmr/mock-data-remediation/2mlb/2mlb.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2ltq/2ltq-corrected-div_src.mr',
                 '../../tests-nmr/mock-data-remediation/2ltq/2ltq.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-combine-at-upload/bmr36473/data/D_1300028046_mr-upload_P2.cns.V1',
                 '../../tests-nmr/mock-data-combine-at-upload/bmr36473/data/D_1300028046_model-annotate_P1.cif.V2')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2mf8/2mf8-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2mf8/2mf8.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-daother-7969/dna2_used.tbl',
                 '../../tests-nmr/mock-data-daother-7969/D_800478_model_P1.cif.V3')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6ijw/D_1300008256_mr_P1.cyana.V1-corrected',
                 '../../tests-nmr/mock-data-remediation/6ijw/6ijw.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6uck/noe.tbl-corrected',
                 '../../tests-nmr/mock-data-remediation/6uck/6uck.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2m10/2m10-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/2m10/2m10.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/1iio/1iio-trimmed.mr',
                     '../../tests-nmr/mock-data-remediation/1iio/1iio.cif')
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/1iio/1iio-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/1iio/1iio.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2jrl/2jrl-corrected-div_dst-div_src.mr',
                 '../../tests-nmr/mock-data-remediation/2jrl/2jrl.cif')

    reader = CnsMRReader(False)
    reader.setDebugMode(False)
    reader_listener, _, _ =\
        reader.parse('../../tests-nmr/mock-data-remediation/2b87/2b87-corrected.mr',
                     '../../tests-nmr/mock-data-remediation/2b87/2b87.cif')
    reader = CnsMRReader(True, reasons=reader_listener.getReasonsForReparsing())
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2b87/2b87-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2b87/2b87.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/2lhz/2lhz-corrected.mr',
                 '../../tests-nmr/mock-data-remediation/2lhz/2lhz.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/6th8/hbond_patches.tbl',
                 '../../tests-nmr/mock-data-remediation/6th8/6th8.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-remediation/4by9/4by9-trimmed.mr',
                 '../../tests-nmr/mock-data-remediation/4by9/4by9.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-daother-7690/D_1300022442_mr-upload_P1.cns.V1',
                 '../../tests-nmr/mock-data-daother-7690/D_1300022442_model-annotate_P1.cif.V1')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-daother-7690/D_1300019843_mr-upload_P1.cns.V1',
                 '../../tests-nmr/mock-data-daother-7690/D_1300019843_model-annotate_P1.cif.V1')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-pdbstat/D_1000243168_mr-upload_P8.xplor-nih.V1',
                 '../../tests-nmr/mock-data-pdbstat/6pvr.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-pdbstat/D_1000243168_mr-upload_P2.xplor-nih.V1',
                 '../../tests-nmr/mock-data-pdbstat/6pvr.cif')

    reader = CnsMRReader(True)
    reader.setDebugMode(True)
    reader.parse('../../tests-nmr/mock-data-pdbstat/atom_sel_expr_example.txt',
                 '../../tests-nmr/mock-data-pdbstat/6pvr.cif')
