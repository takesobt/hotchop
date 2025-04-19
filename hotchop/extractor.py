# extractor.py
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import random as rd
import logging

class HOTchopper:
    # *-----------------------------------------------------------------------------------------------------------------*
    # * Constructor
    # *-----------------------------------------------------------------------------------------------------------------*
    def __init__(self, input_file: str, output_file: str, criteria_type: str, chop_criteria: dict):
        # set argument value
        self.input_file = input_file
        self.output_file = output_file
        self.criteria_type = criteria_type
        self.chop_criteria = chop_criteria
        #pdb.set_trace()
        # initial value set
        self.intCNT1 = 0  # input counter
        self.intCNT2 = 0  # output counter
        self.intCNT3 = 0  # TRNN renumber counter
        self.strInRec = ""  # input file record work
        self.strOutnRec = ""  # output file record work
        self.SMSG_STNQ = ""  # SMSG+STNQ like BFH01
        self.strBCH02 = ""  # work BCH02
        self.flgBCH02 = False  # flag BCH02
        self.strBOH03 = ""  # work BOH03
        self.flgBOH03 = False  # flag BOH03
        self.flgIFG = False  # IFG flag
        self.flgExtract = False  # choosen flag
        self.intTranRecs = 0  # transaction basis hot file record index
        self.strBSPI_BFT99 = ""  # BSPI for BFT99
        self.strNewBCH02Key = ""  # PDAI＋PCYC
        self.strOldBCH02Key = ""  # BCH02Key#s Old value
        self.strNewAGTN = ""  # AGTN in BOH03
        self.strOldAGTN = ""  # AGTN#s Old value
        self.strNewRMED = ""  # RMED in BOH03
        self.strOldRMED = ""  # RMED#s Old Value
        self.strNewBAGC = ""  # BAGC calculated from TRNC in BKS24
        self.strOldBAGC = ""  # BAGC#s Old value
        self.strTRNC = ""  # TRNC in BKS24
        self.strCUTP = ""  # CUTP in BKS30
        self.intTDAM = 0  # TDAM in BKS30
        self.intTMFA = 0  # TMFA in BKS30
        self.intLREP = 0  # LREP in BKS30
        self.intREMT = 0  # REMT in BKP84
        self.intEFCO = 0  # EFCO in BKS39
        self.intTOCA = 0  # TOCA in BKS42
        self.flg1stBAGC = True  # BAGC initial output flag
        self.flg1stBOT93 = True  # BOT93 initial output flag
        self.flg1stBOT94 = True  # BOT94 initial output flag
        self.flg1stBCT95 = True  # BCT95 initial output flag

        # numpy array definition and initial value set
        self.arrCUTP_BOH03 = np.array([""], dtype=object)  # CUTP array for BOH03
        self.arrTranRecs = np.array(
            [], dtype=object
        )  # transaction basis hot file record array

        # pandas detaframe definition and index setting
        self.df_BOT93 = pd.DataFrame(
            columns=["CUTP", "TRNC", "GROS", "TREM", "TCOM", "TTMF", "TLRP", "TTCA"]
        )
        self.df_BOT93.set_index(["CUTP", "TRNC"], inplace=True)
        self.df_BOT94 = pd.DataFrame(
            columns=["CUTP", "GROS", "TREM", "TCOM", "TTMF", "TLRP", "TTCA"]
        )
        self.df_BOT94.set_index("CUTP", inplace=True)
        self.df_BCT95 = pd.DataFrame(
            columns=["CUTP", "GROS", "TREM", "TCOM", "TTMF", "TLRP", "TTCA", "OFCC"]
        )
        self.df_BCT95.set_index("CUTP", inplace=True)
        self.df_BFT99 = pd.DataFrame(
            columns=["CUTP", "GROS", "TREM", "TCOM", "TTMF", "TLRP", "TTCA", "OFCC"]
        )
        self.df_BFT99.set_index("CUTP", inplace=True)

    # *-----------------------------------------------------------------------------------------------------------------*
    # * Method Name : HOT_chop
    # * Comments    : Select transactions which matches criteria sheets conditions
    # *-----------------------------------------------------------------------------------------------------------------*
    def HOT_chop(self):
        try:
            # ***********************
            # *** initial process ***
            # ***********************
            self._line_separator = self._detect_line_separator(
                self.input_file
            )  # Detect the line separator
            if self._line_separator is None:
                logging.error("Error:Line separator could not be detected in the HOT file.")
                raise

            with open(self.input_file, "r") as self.infile, open(
                self.output_file, "w", newline=""
            ) as self.outfile:  # Write newline='' to control line endings
                # ***********************
                # ***  main process   ***
                # ***********************
                while True:
                    # Read aline from the input file
                    self.strInRec = self.infile.readline()
                    # Break in case of EOF
                    if not self.strInRec:
                        break
                    self.intCNT1 += 1  # input counter count up
                    # Check if the record is subject to output
                    self._extract_HOTfile()
                    if self.flgExtract:
                        # Record output
                        self._edit_write()
                # ***********************
                # ***   end process   ***
                # ***********************
                # export text file
                if self.intCNT1 > 1:
                    # If no transaction is selected, BCH02 should be written
                    if self.intCNT3 == 0:
                        self.intCNT2 += 1
                        self.strBCH02 = self._replace_string(
                            self.strBCH02, 3, str(self.intCNT2).zfill(8)
                        )
                        # Out file write
                        self._outfileWrite(self.strBCH02)
                    # Summary Records write
                    self._BOT93_Write()
                    self._BOT94_Write()
                    # If no transaction is selected, BCT95 should be written
                    if self.intCNT3 == 0:
                        self.flg1stBCT95 = False
                        self.strOldBCH02Key = self.strNewBCH02Key
                        self.df_BCT95.loc["    "] = 0
                    self._BCT95_Write()
                    # If no transaction is selected, BFT99 should be written
                    if self.intCNT3 == 0:
                        self.df_BFT99.loc["    "] = 0
                    self._BFT99_Write()

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            raise

    # *-----------------------------------------------------------------------------------------------------------------*
    # * Method Name : _detect_line_separator
    # * Comments    : read first 1000 letters of given file path and return its line saparator
    # *-----------------------------------------------------------------------------------------------------------------*
    def _detect_line_separator(self, file_path: str) -> str:
        with open(file_path, "rb") as file:
            content = file.read(1000)  # Read the first 1000 bytes
        if b"IFG" in content:
            self.flgIFG = True
        if b"\r\n" in content:
            return "\r\n"
        elif b"\n" in content:
            return "\n"
        else:
            return None

    # *-----------------------------------------------------------------------------------------------------------------*
    # * Method Name : _outfileWrite
    # * Comments    : write outfile a record with detected line separator
    # *-----------------------------------------------------------------------------------------------------------------*
    def _outfileWrite(self, _str_outrec: str):
        # line saparator handling
        if _str_outrec.endswith("\n") and not _str_outrec.endswith(
            self._line_separator
        ):
            _str_outrec = _str_outrec.rstrip("\n") + self._line_separator
        elif not _str_outrec.endswith(self._line_separator):
            _str_outrec = _str_outrec + self._line_separator
        # output the file
        self.outfile.write(_str_outrec)

    # *-----------------------------------------------------------------------------------------------------------------*
    # * Method Name : _extract_HOTfile
    # * Comments    : Check if the HOTfile matches criteria
    # *-----------------------------------------------------------------------------------------------------------------*
    def _extract_HOTfile(self) -> bool:
        # SMSG+STNQ
        self.SMSG_STNQ = self.strInRec[0:3] + self.strInRec[11:13]
        # In case of BFH01 output anyway
        if self.SMSG_STNQ == "BFH01":
            # Set 'PROD' to TPST/BFH01
            self.strInRec = self._replace_string(self.strInRec, 22, "PROD")
            # Set random value(00-59) to processing second
            _intWRK = rd.randint(0, 59)
            self.strInRec = self._replace_string(
                self.strInRec, 34, str(_intWRK).zfill(2)
            )
            # Set random value(00-99) to the File Sequence
            _intWRK = rd.randint(0, 99)
            self.strInRec = self._replace_string(
                self.strInRec, 42, str(_intWRK).zfill(2)
            )
            # save BSPI for BFT99
            self.strBSPI_BFT99 = self.strInRec[13:16]
            self.flgExtract = True
            return self.flgExtract

        # in case BCH02, save to work
        if self.SMSG_STNQ == "BCH02":
            self.strBCH02 = self.strInRec
            self.flgBCH02 = False  # BCH02 write flag off
            self.flgExtract = False
            self.strBCH02 = self._replace_string(
                self.strBCH02.rstrip("\n"), 49, "CHOPPED BY THE HOTCHOP"
            )
            # Save PDAI,PCYC
            self.strNewBCH02Key = self.strInRec[13:17]  # PDAI＋PCYC
            return self.flgExtract

        # in case BOH03, save to work
        if self.SMSG_STNQ == "BOH03":
            self.strBOH03 = self.strInRec
            self.flgBOH03 = False  # BOH03 write flag off
            self.flgExtract = False
            # Save AGTN and RMED
            self.strNewAGTN = self.strInRec[13:21]
            self.strNewRMED = self.strInRec[21:27]
            return self.flgExtract

        # in case BKT06(transaction header), read all transaction data and save into a table
        if self.SMSG_STNQ == "BKT06":
            # Extract flag clear
            self.flgExtract = False

            # TRNN/BKT06 check
            if self.criteria_type == "TRNN":
                if self._criteria_check(self.strInRec[13:19]):
                    # extract flag on
                    self.flgExtract = True

            # redeline the table
            self.intTranRecs = 1
            self.arrTranRecs = np.array(self.strInRec, dtype=object)

            # work clear
            self.intTDAM = 0  # TDAM in BKS30
            self.intTMFA = 0  # TMFA in BKS30
            self.intLREP = 0  # LREP in BKS30
            self.intREMT = 0  # REMT in BKP84
            self.intEFCO = 0  # EFCO in BKS39
            self.intTOCA = 0  # TOCA in BKS42

            # read all transaction records into the table
            _intTREC_MAX = int(self.strInRec[21:24])  # save TREC
            for i in range(1, _intTREC_MAX):
                # input stream record
                self.strInRec = self.infile.readline()
                self.intCNT1 += 1  # input counter count up
                # Break in case of EOF
                if not self.strInRec:
                    break
                # SMSG+STNQ
                self.SMSG_STNQ = self.strInRec[0:3] + self.strInRec[11:13]
                # save to the table
                self.intTranRecs += 1
                self.arrTranRecs = np.append(self.arrTranRecs, self.strInRec)
                # Save necessary items to work
                if self.SMSG_STNQ == "BKS30":
                    self.intTDAM += self._BCD2DEC(self.strInRec[119:130])  # TDAM
                    self.intTMFA += (
                        self._BCD2DEC(self.strInRec[70:81])
                        + self._BCD2DEC(self.strInRec[89:100])
                        + self._BCD2DEC(self.strInRec[108:119])
                    )  # TMFA
                    self.strCUTP = self.strInRec[132:136]  # CUTP
                elif self.SMSG_STNQ == "BKP84":
                    self.intREMT += self._BCD2DEC(self.strInRec[97:108])  # REMT
                elif self.SMSG_STNQ == "BKS39":
                    self.intEFCO += self._BCD2DEC(self.strInRec[92:103])  # EFCO
                elif self.SMSG_STNQ == "BKS42":
                    self.intTOCA += self._BCD2DEC(self.strInRec[46:57])  # TOCA
                elif self.SMSG_STNQ == "BKS24":
                    # TDNR check
                    if self.criteria_type == "TDNR":
                        if self._criteria_check(self.strInRec[25:38]):
                            # extract flag on
                            self.flgExtract = True
                    self.strTRNC = self.strInRec[71:75]  # TRNC
                    self.strNewBAGC = self._BAGC(self.strTRNC)
                    if self.flg1stBAGC:
                        self.strOldBAGC = self.strNewBAGC
                        self.flg1stBAGC = False
                    # In case of IfG data, and BAGC = 'Issuing':  strTRNC should be changed to 'SALE'
                    if self.flgIFG and self.strNewBAGC == "Issue":
                        self.strTRNC = "SALE"

    # *-----------------------------------------------------------------------------------------------------------------*
    # * Method Name : _criteria_check
    # * Comments    : Check if the given value matchs against criteria dictionary
    # *-----------------------------------------------------------------------------------------------------------------*
    def _criteria_check(self, givenValue: str) -> bool:
        if givenValue in self.chop_criteria:
            self.chop_criteria[givenValue] = "OK"
            return True
        else:
            return False

    # *-----------------------------------------------------------------------------------------------------------------*
    # * Method Name : _edit_write
    # * Comments    : Edit and Write HOT file
    # *-----------------------------------------------------------------------------------------------------------------*
    def _edit_write(self):
        # In case of BFH01/BCH02 output anyway
        if self.SMSG_STNQ == "BFH01" or self.SMSG_STNQ == "BCH02":
            self.intCNT2 += 1
            self.strInRec = self._replace_string(
                self.strInRec, 3, str(self.intCNT2).zfill(8)
            )
            # Out file write
            self._outfileWrite(self.strInRec)
            return

        # if newkeys different from old keys, BOT93 write
        if not (
            self.strNewBCH02Key == self.strOldBCH02Key
            and self.strNewAGTN == self.strOldAGTN
            and self.strNewBAGC == self.strOldBAGC
        ):
            # BOT93 write
            self._BOT93_Write()
            # Clear BOT93 table
            self.df_BOT93 = pd.DataFrame(
                columns=["CUTP", "TRNC", "GROS", "TREM", "TCOM", "TTMF", "TLRP", "TTCA"]
            )
            self.df_BOT93.set_index(["CUTP", "TRNC"], inplace=True)
            # if newkeys different from old keys, BOT94 write
            if not (
                self.strNewBCH02Key == self.strOldBCH02Key
                and self.strNewAGTN == self.strOldAGTN
            ):
                # BOT94 write
                self._BOT94_Write()
                # Clear BOT94 table
                self.df_BOT94 = pd.DataFrame(
                    columns=["CUTP", "GROS", "TREM", "TCOM", "TTMF", "TLRP", "TTCA"]
                )
                self.df_BOT94.set_index("CUTP", inplace=True)
                # change keys
                self.strOldAGTN = self.strNewAGTN
                self.strOldRMED = self.strNewRMED
                # if newkeys different from old keys, BCT95 write
                if not (self.strNewBCH02Key == self.strOldBCH02Key):
                    # BCT95 write
                    self._BCT95_Write()
                    # Clear BCT95 table
                    self.df_BFT95 = pd.DataFrame(
                        columns=[
                            "CUTP",
                            "GROS",
                            "TREM",
                            "TCOM",
                            "TTMF",
                            "TLRP",
                            "TTCA",
                            "OFCC",
                        ]
                    )
                    self.df_BFT95.set_index("CUTP", inplace=True)
                    # change keys
                    self.strOldBCH02Key = self.strNewBCH02Key
        # change keys
        self.strOldBAGC = self.strNewBAGC

        # BCH02 write
        if not self.flgBCH02:
            self.intCNT2 += 1
            self.strBCH02 = self._replace_string(
                self.strBCH02, 3, str(self.intCNT2).zfill(8)
            )
            # Out file write
            self._outfileWrite(self.strBCH02)
            self.flgBCH02 = True

        # BOH03 write
        if not self.flgBOH03:
            self.intCNT2 += 1
            self.strBOH03 = self._replace_string(
                self.strBOH03, 3, str(self.intCNT2).zfill(8)
            )
            # Out file write
            self._outfileWrite(self.strBOH03)
            self.flgBOH03 = True
            # BOH03 table clear
            self.arrCUTP_BOH03 = np.array([""], dtype=object)  # CUTP table for BOH03

        # TRNN count up
        self.intCNT3 += 1
        # Output Selected Transaction Records
        for i in range(0, self.intTranRecs):
            # In case of TDNR criterion is selected, TRNN shoud be renumbered
            if self.criteria_type == "TDNR":
                # In case of BKT06
                if (
                    self.arrTranRecs[i][0:3] == "BKT"
                    and self.arrTranRecs[i][11:13] == "06"
                ):
                    self.arrTranRecs[i] = self._replace_string(
                        self.arrTranRecs[i], 13, str(self.intCNT3).zfill(6)
                    )
                else:
                    self.arrTranRecs[i] = self._replace_string(
                        self.arrTranRecs[i], 19, str(self.intCNT3).zfill(6)
                    )

            self.intCNT2 += 1
            self.arrTranRecs[i] = self._replace_string(
                self.arrTranRecs[i], 3, str(self.intCNT2).zfill(8)
            )
            # Out file write
            self._outfileWrite(self.arrTranRecs[i])

        # if there is no matched index(CUTP,TRNC) in BOT93, create a new index
        if not (self.strCUTP, self.strTRNC) in self.df_BOT93.index:
            self.df_BOT93.loc[(self.strCUTP, self.strTRNC), :] = 0

        # if there is no matched index(CUTP) in BOT94, create a new index
        if not self.strCUTP in self.df_BOT94.index:
            self.df_BOT94.loc[self.strCUTP] = 0

        # if there is no matched index(CUTP) in BCT95, create a new index
        if not self.strCUTP in self.df_BCT95.index:
            self.df_BCT95.loc[self.strCUTP] = 0

        # if there is no matched index(CUTP) in BFT99, create a new index
        if not self.strCUTP in self.df_BFT99.index:
            self.df_BFT99.loc[self.strCUTP] = 0

        # *** Add amount to BOT93 ***
        # GROS is an algebraic sum of TDAM fields from the BKS30
        self.df_BOT93.loc[(self.strCUTP, self.strTRNC), "GROS"] += self.intTDAM
        # TTMF is an algebraic sum of TMFA fields from the BKS30
        self.df_BOT93.loc[(self.strCUTP, self.strTRNC), "TTMF"] += self.intTMFA
        # TLRP is an algebraic sum of LREP fields from the BKS30
        self.df_BOT93.loc[(self.strCUTP, self.strTRNC), "TLRP"] += self.intLREP
        # TREM is an algebraic sum of REMT fields from the BKT84
        self.df_BOT93.loc[(self.strCUTP, self.strTRNC), "TREM"] += self.intREMT
        # TCOM is an algebraic sum of EFCO fields from the BKS39
        self.df_BOT93.loc[(self.strCUTP, self.strTRNC), "TCOM"] += self.intEFCO
        # TTCA is an algebraic sum of TOCA fields from the BKS42
        self.df_BOT93.loc[(self.strCUTP, self.strTRNC), "TTCA"] += self.intTOCA

        # *** Add amount to BOT94 ***
        # GROS is an algebraic sum of TDAM fields from the BKS30
        self.df_BOT94.loc[self.strCUTP, "GROS"] += self.intTDAM
        # TTMF is an algebraic sum of TMFA fields from the BKS30
        self.df_BOT94.loc[self.strCUTP, "TTMF"] += self.intTMFA
        # TLRP is an algebraic sum of LREP fields from the BKS30
        self.df_BOT94.loc[self.strCUTP, "TLRP"] += self.intLREP
        # TREM is an algebraic sum of REMT fields from the BKT84
        self.df_BOT94.loc[self.strCUTP, "TREM"] += self.intREMT
        # TCOM is an algebraic sum of EFCO fields from the BKS39
        self.df_BOT94.loc[self.strCUTP, "TCOM"] += self.intEFCO
        # TTCA is an algebraic sum of TOCA fields from the BKS42
        self.df_BOT94.loc[self.strCUTP, "TTCA"] += self.intTOCA

        # *** Add amount to BCT95 ***
        # GROS is an algebraic sum of TDAM fields from the BKS30
        self.df_BCT95.loc[self.strCUTP, "GROS"] += self.intTDAM
        # TTMF is an algebraic sum of TMFA fields from the BKS30
        self.df_BCT95.loc[self.strCUTP, "TTMF"] += self.intTMFA
        # TLRP is an algebraic sum of LREP fields from the BKS30
        self.df_BCT95.loc[self.strCUTP, "TLRP"] += self.intLREP
        # TREM is an algebraic sum of REMT fields from the BKT84
        self.df_BCT95.loc[self.strCUTP, "TREM"] += self.intREMT
        # TCOM is an algebraic sum of EFCO fields from the BKS39
        self.df_BCT95.loc[self.strCUTP, "TCOM"] += self.intEFCO
        # TTCA is an algebraic sum of TOCA fields from the BKS42
        self.df_BCT95.loc[self.strCUTP, "TTCA"] += self.intTOCA

        # *** Add amount to BFT99 ***
        # GROS is an algebraic sum of TDAM fields from the BKS30
        self.df_BFT99.loc[self.strCUTP, "GROS"] += self.intTDAM
        # TTMF is an algebraic sum of TMFA fields from the BKS30
        self.df_BFT99.loc[self.strCUTP, "TTMF"] += self.intTMFA
        # TLRP is an algebraic sum of LREP fields from the BKS30
        self.df_BFT99.loc[self.strCUTP, "TLRP"] += self.intLREP
        # TREM is an algebraic sum of REMT fields from the BKT84
        self.df_BFT99.loc[self.strCUTP, "TREM"] += self.intREMT
        # TCOM is an algebraic sum of EFCO fields from the BKS39
        self.df_BFT99.loc[self.strCUTP, "TCOM"] += self.intEFCO
        # TTCA is an algebraic sum of TOCA fields from the BKS42
        self.df_BFT99.loc[self.strCUTP, "TTCA"] += self.intTOCA

        # if there is no matched CUTP in the array arrCUTP_BOH03
        if not np.any(self.arrCUTP_BOH03 == self.strCUTP):
            # count up BCT95/BFT99# OFCC count
            self.df_BCT95.loc[self.strCUTP, "OFCC"] += +1
            self.df_BFT99.loc[self.strCUTP, "OFCC"] += +1
            # set the CUTP to the BOH03 table
            if self.arrCUTP_BOH03[0] != "":  # create new CUTP to BOH03 table
                self.arrCUTP_BOH03 = np.append(
                    self.arrCUTP_BOH03, self.strCUTP
                )  # CUTP table for BOH03
            else:  # set CUTP to the initial BOH03 table
                self.arrCUTP_BOH03[0] = self.strCUTP

        # Extract flag off
        self.flgExtract = False

    # *-----------------------------------------------------------------------------------------------------------------*
    # * Method Name : BOT93_Write
    # * Comments    : Edit and Write BOT93 Records
    # *-----------------------------------------------------------------------------------------------------------------*
    def _BOT93_Write(self):
        # First time BOT93 should be skipped
        if self.flg1stBOT93:
            self.flg1stBOT93 = False
            return
        # Sort BOT93 Table by CUTP,TRNC Assnding
        _df_BOT93_KEYS_asc = self.df_BOT93.sort_index(ascending=True)
        # Edit and write for each index(CUTP,TRNC) basis
        for index, row in _df_BOT93_KEYS_asc.iterrows():
            self.intCNT2 += 1
            self.strOutRec = (
                "BOT"
                + str(self.intCNT2).zfill(8)
                + "93"
                + self.strOldAGTN
                + self.strOldRMED
            )
            self.strOutRec += self._DEC2BCD(row["GROS"], 15)
            self.strOutRec += self._DEC2BCD(row["TREM"], 15)
            self.strOutRec += self._DEC2BCD(row["TCOM"], 15)
            self.strOutRec += self._DEC2BCD(row["TTMF"], 15)
            self.strOutRec += index[1]  # TRNC
            self.strOutRec += (
                self._DEC2BCD(row["TTCA"], 15) + "                          "
            )
            self.strOutRec += index[0]  # CUTP
            # Out file write
            self._outfileWrite(self.strOutRec)

    # *-----------------------------------------------------------------------------------------------------------------*
    # * Method Name : BOT94_Write
    # * Comments    : Edit and Write BOT94 Records
    # *-----------------------------------------------------------------------------------------------------------------*
    def _BOT94_Write(self):
        # First time BOT94 should be skipped
        if self.flg1stBOT94:
            self.flg1stBOT94 = False
            return
        # Sort BOT94 Table by CUTP Assnding
        _df_BOT94_CUTP_asc = self.df_BOT94.sort_index(ascending=True)
        # Edit and write for each index(CUTP) basis
        for index, row in _df_BOT94_CUTP_asc.iterrows():
            self.intCNT2 += 1
            self.strOutRec = (
                "BOT"
                + str(self.intCNT2).zfill(8)
                + "94"
                + self.strOldAGTN
                + self.strOldRMED
            )
            self.strOutRec += self._DEC2BCD(row["GROS"], 15)
            self.strOutRec += self._DEC2BCD(row["TREM"], 15)
            self.strOutRec += self._DEC2BCD(row["TCOM"], 15)
            self.strOutRec += self._DEC2BCD(row["TTMF"], 15)
            self.strOutRec += (
                self._DEC2BCD(row["TTCA"], 15) + "                              "
            )
            self.strOutRec += index
            # Out file write
            self._outfileWrite(self.strOutRec)

    # *-----------------------------------------------------------------------------------------------------------------*
    # * Method Name : BCT95_Write
    # * Comments    : Edit and Write BCT95 Records
    # *-----------------------------------------------------------------------------------------------------------------*
    def _BCT95_Write(self):
        # First time BCT95 should be skipped
        if self.flg1stBCT95:
            self.flg1stBCT95 = False
            return
        # Sort BCT95 Table by CUTP Assnding
        _df_BCT95_CUTP_asc = self.df_BCT95.sort_index(ascending=True)
        # Edit and write for each index(CUTP) basis
        for index, row in _df_BCT95_CUTP_asc.iterrows():
            self.intCNT2 += 1
            self.strOutRec = (
                "BCT"
                + str(self.intCNT2).zfill(8)
                + "95"
                + self.strOldBCH02Key
                + str(row["OFCC"]).zfill(5)
            )
            self.strOutRec += self._DEC2BCD(row["GROS"], 15)
            self.strOutRec += self._DEC2BCD(row["TREM"], 15)
            self.strOutRec += self._DEC2BCD(row["TCOM"], 15)
            self.strOutRec += self._DEC2BCD(row["TTMF"], 15)
            self.strOutRec += (
                self._DEC2BCD(row["TTCA"], 15) + "                                   "
            )
            self.strOutRec += index
            # Out file write
            self._outfileWrite(self.strOutRec)

    # *-----------------------------------------------------------------------------------------------------------------*
    # * Method Name : BFT99_Write
    # * Comments    : Edit and Write BFT99 Records
    # *-----------------------------------------------------------------------------------------------------------------*
    def _BFT99_Write(self):
        # Sort BFT99 Table by CUTP Assnding
        _df_BFT99_CUTP_asc = self.df_BFT99.sort_index(ascending=True)
        # Edit and write for each index(CUTP) basis
        # pdb.set_trace()
        for index, row in _df_BFT99_CUTP_asc.iterrows():
            self.intCNT2 += 1
            self.strOutRec = (
                "BFT"
                + str(self.intCNT2).zfill(8)
                + "99"
                + self.strBSPI_BFT99
                + str(row["OFCC"]).zfill(5)
            )
            self.strOutRec += self._DEC2BCD(row["GROS"], 15)
            self.strOutRec += self._DEC2BCD(row["TREM"], 15)
            self.strOutRec += self._DEC2BCD(row["TCOM"], 15)
            self.strOutRec += self._DEC2BCD(row["TTMF"], 15)
            self.strOutRec += (
                self._DEC2BCD(row["TTCA"], 15) + "                                    "
            )
            self.strOutRec += index
            # Out file write
            self._outfileWrite(self.strOutRec)

    # *-----------------------------------------------------------------------------------------------------------------*
    # * Method Name : _replace_string
    # * Comments    : replace the poart of string(whole string, replace column, replace letters)
    # *-----------------------------------------------------------------------------------------------------------------*
    def _replace_string(self, i_string: str, i: int, r_string: str) -> str:
        # in case whold string is shorter than the replace column
        if len(i_string) < i:
            i_string = i_string + " " * (i - len(i_string))
        # result back
        return i_string[:i] + r_string + i_string[i + len(r_string) :]

    # *-----------------------------------------------------------------------------------------------------------------*
    # * Method Name : _BAGC
    # * Comments    : Decide BAGC code by TRNC (wkBAGC=Billing Analysis Grouping Code)
    # *-----------------------------------------------------------------------------------------------------------------*
    def _BAGC(self, argTRNC: str) -> str:
        wkBAGC = ""
        if argTRNC == "ACMA":
            wkBAGC = "ACM"
        elif argTRNC == "ACMD":
            wkBAGC = "ACM"
        elif argTRNC == "ACMR":
            wkBAGC = "Refund"
        elif argTRNC == "ACNT":
            wkBAGC = "ACM"
        elif argTRNC == "ADMA":
            wkBAGC = "ADM"
        elif argTRNC == "ADMD":
            wkBAGC = "ADM"
        elif argTRNC == "ADNT":
            wkBAGC = "ADM"
        elif argTRNC == "CANN":
            wkBAGC = "n/a"
        elif argTRNC == "CANR":
            wkBAGC = "n/a"
        elif argTRNC == "CANX":
            wkBAGC = "Issue"
        elif argTRNC == "EMDA":
            wkBAGC = "Issue"
        elif argTRNC == "EMDS":
            wkBAGC = "Issue"
        elif argTRNC == "RCSM":
            wkBAGC = "ADM"
        elif argTRNC == "RFNC":
            wkBAGC = "Refund"
        elif argTRNC == "RFND":
            wkBAGC = "Refund"
        elif argTRNC == "RSCN":
            wkBAGC = "n/a"
        elif argTRNC == "SALE":
            wkBAGC = "n/a"
        elif argTRNC == "SPCR":
            wkBAGC = "ACM"
        elif argTRNC == "SPDR":
            wkBAGC = "ADM"
        elif argTRNC == "TASF":
            wkBAGC = "Issue"
        elif argTRNC == "TKTA":
            wkBAGC = "Issue"
        elif argTRNC == "TKTB":
            wkBAGC = "Issue"
        elif argTRNC == "TKTT":
            wkBAGC = "Issue"
        elif argTRNC == "VSCN":
            wkBAGC = "n/a"
        elif argTRNC == "WALL":
            wkBAGC = "n/a"
        elif argTRNC == "ACMS":
            wkBAGC = "ACM"
        elif argTRNC == "ADMS":
            wkBAGC = "ADM"
        elif argTRNC == "ARVM":
            wkBAGC = "Issue"
        elif argTRNC == "MCOM":
            wkBAGC = "Issue"
        elif argTRNC == "SSAC":
            wkBAGC = "ACM"
        elif argTRNC == "SSAD":
            wkBAGC = "ADM"
        elif argTRNC == "TKTM":
            wkBAGC = "Issue"
        elif argTRNC == "XSBM":
            wkBAGC = "Issue"
        elif argTRNC[0:2] == "MD":
            wkBAGC = "Issue"
        elif argTRNC[0:2] == "MP":
            wkBAGC = "Issue"
        elif argTRNC[0:2] == "MV":
            wkBAGC = "Issue"
        elif argTRNC[0:2] == "MM":
            wkBAGC = "Issue"
        return wkBAGC

    # *-----------------------------------------------------------------------------------------------------------------*
    # * Method Name : _BCD2DEC
    # * Comments    : converts BCD(Binary-coded decimal) to decimal with sign
    # * Arguments   : argInput BCD string
    # * Output      : decimal string with sign
    # *-----------------------------------------------------------------------------------------------------------------*
    def _BCD2DEC(self, argInput: str) -> int:
        _intSign = len(argInput)
        if argInput[-1] == "{":
            return int(argInput[0 : (_intSign - 1)] + "0")
        elif argInput[-1] == "A":
            return int(argInput[0 : (_intSign - 1)] + "1")
        elif argInput[-1] == "B":
            return int(argInput[0 : (_intSign - 1)] + "2")
        elif argInput[-1] == "C":
            return int(argInput[0 : (_intSign - 1)] + "3")
        elif argInput[-1] == "D":
            return int(argInput[0 : (_intSign - 1)] + "4")
        elif argInput[-1] == "E":
            return int(argInput[0 : (_intSign - 1)] + "5")
        elif argInput[-1] == "F":
            return int(argInput[0 : (_intSign - 1)] + "6")
        elif argInput[-1] == "G":
            return int(argInput[0 : (_intSign - 1)] + "7")
        elif argInput[-1] == "H":
            return int(argInput[0 : (_intSign - 1)] + "8")
        elif argInput[-1] == "I":
            return int(argInput[0 : (_intSign - 1)] + "9")
        elif argInput[-1] == "}":
            return int(argInput[0 : (_intSign - 1)] + "0") * -1
        elif argInput[-1] == "J":
            return int(argInput[0 : (_intSign - 1)] + "1") * -1
        elif argInput[-1] == "K":
            return int(argInput[0 : (_intSign - 1)] + "2") * -1
        elif argInput[-1] == "L":
            return int(argInput[0 : (_intSign - 1)] + "3") * -1
        elif argInput[-1] == "M":
            return int(argInput[0 : (_intSign - 1)] + "4") * -1
        elif argInput[-1] == "N":
            return int(argInput[0 : (_intSign - 1)] + "5") * -1
        elif argInput[-1] == "O":
            return int(argInput[0 : (_intSign - 1)] + "6") * -1
        elif argInput[-1] == "P":
            return int(argInput[0 : (_intSign - 1)] + "7") * -1
        elif argInput[-1] == "Q":
            return int(argInput[0 : (_intSign - 1)] + "8") * -1
        elif argInput[-1] == "R":
            return int(argInput[0 : (_intSign - 1)] + "9") * -1

    # *-----------------------------------------------------------------------------------------------------------------*
    # * Method Name : _DEC2BCD
    # * Comments    : converts decimal with sign to BCD(Binary-coded decimal)
    # * Arguments   : arg1 decimal with sign integer, arg2 length integer
    # * Output      : string of BCD leading zero of length of arg2
    # *-----------------------------------------------------------------------------------------------------------------*
    def _DEC2BCD(self, argInput: int, argLen: int) -> str:
        wrkBCD = str(abs(argInput)).zfill(argLen)
        if argInput >= 0:
            wrkBCD = wrkBCD + "+"
        else:
            wrkBCD = wrkBCD + "-"
        _sliceLen = argLen - 1
        if wrkBCD[-2:] == "0+":
            return wrkBCD[0:_sliceLen] + "{"
        elif wrkBCD[-2:] == "1+":
            return wrkBCD[0:_sliceLen] + "A"
        elif wrkBCD[-2:] == "2+":
            return wrkBCD[0:_sliceLen] + "B"
        elif wrkBCD[-2:] == "3+":
            return wrkBCD[0:_sliceLen] + "C"
        elif wrkBCD[-2:] == "4+":
            return wrkBCD[0:_sliceLen] + "D"
        elif wrkBCD[-2:] == "5+":
            return wrkBCD[0:_sliceLen] + "E"
        elif wrkBCD[-2:] == "6+":
            return wrkBCD[0:_sliceLen] + "F"
        elif wrkBCD[-2:] == "7+":
            return wrkBCD[0:_sliceLen] + "G"
        elif wrkBCD[-2:] == "8+":
            return wrkBCD[0:_sliceLen] + "H"
        elif wrkBCD[-2:] == "9+":
            return wrkBCD[0:_sliceLen] + "I"
        elif wrkBCD[-2:] == "0-":
            return wrkBCD[0:_sliceLen] + "}"
        elif wrkBCD[-2:] == "1-":
            return wrkBCD[0:_sliceLen] + "J"
        elif wrkBCD[-2:] == "2-":
            return wrkBCD[0:_sliceLen] + "K"
        elif wrkBCD[-2:] == "3-":
            return wrkBCD[0:_sliceLen] + "L"
        elif wrkBCD[-2:] == "4-":
            return wrkBCD[0:_sliceLen] + "M"
        elif wrkBCD[-2:] == "5-":
            return wrkBCD[0:_sliceLen] + "N"
        elif wrkBCD[-2:] == "6-":
            return wrkBCD[0:_sliceLen] + "O"
        elif wrkBCD[-2:] == "7-":
            return wrkBCD[0:_sliceLen] + "P"
        elif wrkBCD[-2:] == "8-":
            return wrkBCD[0:_sliceLen] + "Q"
        elif wrkBCD[-2:] == "9-":
            return wrkBCD[0:_sliceLen] + "R"

    # *-----------------------------------------------------------------------------------------------------------------*
    # * Method Name : getresult_number
    # * Comments    : Return the process result of HOT chop
    # *-----------------------------------------------------------------------------------------------------------------*
    def getresult_number(self):
        return (
            "Input  CNT => "
            + str(self.intCNT1)
            + "\n"
            + "Output CNT => "
            + str(self.intCNT2)
            + "\n"
            + "  TRNN CNT => "
            + str(self.intCNT3)
        )

    # *-----------------------------------------------------------------------------------------------------------------*
    # * Method Name : getresult_criteria
    # * Comments    : Return the criteria basis result of HOT chop
    # *-----------------------------------------------------------------------------------------------------------------*
    def getresult_criteria(self) -> dict:
        return self.chop_criteria
