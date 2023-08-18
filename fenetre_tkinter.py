# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 10:42:20 2020

@author: M11344
"""
import tkinter as tk
from tkinter import ttk
from tkinter import *
import tkinter.font as font
from tkinter import filedialog as fd
from textwrap import wrap
from lectureMCC_Pandas import LectureMccCuve
from lecture_Dicom import Lecture_Dicom
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,NavigationToolbar2Tk)
import re
import numpy as np
from echantillonnage_DoseMesure import EchantillonnageDoseMesure
from calculGamma import CalculGamma
from matplotlib.widgets import Cursor


class SnappingCursor:
    """
    A cross hair cursor that snaps to the data point of a line, which is
    closest to the *x* position of the cursor.

    For simplicity, this assumes that *x* values of the data are sorted.
    """

    def __init__(self, ax, line):
        self.ax = ax
        self.horizontal_line = ax.axhline(color='k', lw=0.8, ls='--')
        self.vertical_line = ax.axvline(color='k', lw=0.8, ls='--')
        self.x, self.y = line.get_data()
        self._last_index = None
        # text location in axes coords
        self.text = ax.text(0.3, 0.9, '', transform=ax.transAxes)

    def set_cross_hair_visible(self, visible):
        need_redraw = self.horizontal_line.get_visible() != visible
        self.horizontal_line.set_visible(visible)
        self.vertical_line.set_visible(visible)
        self.text.set_visible(visible)
        return need_redraw

    def on_mouse_move(self, event):
        if not event.inaxes:
            self._last_index = None
            need_redraw = self.set_cross_hair_visible(False)
            if need_redraw:
                self.ax.figure.canvas.draw()
        else:
            self.set_cross_hair_visible(True)
            x, y = event.xdata, event.ydata
            index = min(np.searchsorted(self.x, x), len(self.x) - 1)
            if index == self._last_index:
                return  # still on the same data point. Nothing to do.
            self._last_index = index
            x = self.x[index]
            y = self.y[index]
            # update the line positions
            self.horizontal_line.set_ydata(y)
            self.vertical_line.set_xdata(x)
            self.text.set_text('x=%1.2f, y=%1.2f' % (x, y))
            self.ax.figure.canvas.draw()


class SelectFiles(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.offAxisInPlane = 0
        self.field_size_x = None
        self.field_size_y = None
        self.depth = None
        self.curve_type = None
        self.energie_mcc = None
        self.mppg = None
        self.dsp = None
        self.ssd = None
        self.energie = None


        self.rtdose_a_garder = None
        self.mcc_a_garder = None
        self.mccDejaTrace = False
        self.RTDoseDejaTrace = False

        self.mccSelected = None
        self.dicomSelected = None






        self.ax_1 = None
        self.echantillonnageMCC = None
        self.objPlan = None
        self.listePDD = None
        self.filenameRTDose = None
        self.clear = False
        self.mcc_item = ' '


        ### définition des frames
        self.frameDicomGeneral = Frame(self, highlightbackground="gray", highlightthickness=1)
        self.frameDicomGeneral.grid(row=0, column=0)

        self.frameMCCGeneral = Frame(self, highlightbackground="gray", highlightthickness=1)
        self.frameMCCGeneral.grid(row=0, column=1, sticky='n', padx=100)

        self.frameTraceMatplotlib = Frame(self, highlightbackground="gray", highlightthickness=1)
        self.frameTraceMatplotlib.grid(row=1, column=0, columnspan=2, sticky='n', pady=10)

        self.frameTraceGamma = Frame(self, highlightbackground="gray", highlightthickness=1)
        self.frameTraceGamma.grid(row=2, column=0, columnspan=2, sticky='n')

        ################################################################################################################################################################
        ### définition du sous frame d'ouverture des fichiers dicom
        ################################################################################################################################################################
        self.sousFrameOuvertureDicom = Frame(self.frameDicomGeneral)
        self.sousFrameOuvertureDicom.grid(row=0, column=0, sticky='w', pady=10)
        ### Définition des boutons de sélection
        self.boutonLoad_RTDose = ttk.Button(self.sousFrameOuvertureDicom, text='Open Dicom dose',
                                            command=self.selectDoseFile)
        self.boutonLoad_RTDose.grid(row=0, column=0, padx=20)

        self.boutonLoad_RTPlan = ttk.Button(self.sousFrameOuvertureDicom, text='Open Dicom plan',
                                            command=self.selectPlanFile)
        self.boutonLoad_RTPlan.grid(row=0, column=1)
        ################################################################################################################################################################

        ################################################################################################################################################################
        ### Définition du sous frame pour afficher les fichiers dicom ouverts
        ################################################################################################################################################################
        self.sousFrameAffichageFichierOuvert = Frame(
            self.frameDicomGeneral)  # , highlightbackground="red", highlightthickness=2)
        self.sousFrameAffichageFichierOuvert.grid(row=1, column=0, sticky='w', pady=10)

        ### Définition des labels pour afficher quels fichiers ont été ouverts
        self.lblRTPlan_Ouvert = ttk.Label(self.sousFrameAffichageFichierOuvert, text='RTPLAN ouvert : ')
        self.lblRTDose_Ouvert = ttk.Label(self.sousFrameAffichageFichierOuvert, text='RTDose ouvert : ')

        self.lblRTPlan_Ouvert.grid(row=1, column=0)
        self.lblRTDose_Ouvert.grid(row=2, column=0)
        ################################################################################################################################################################

        ################################################################################################################################################################
        ### définition du sous frame dicom offset
        ########################################################################################################################
        self.sousFrameDicomOffset = Frame(self.frameDicomGeneral)  # , highlightbackground="red", highlightthickness=2)
        self.sousFrameDicomOffset.grid(row=3, column=0, pady=10)

        ### définition du label pour expliquer l'offset
        self.labelExplicationOffset = ttk.Label(self.sousFrameDicomOffset,
                                                text='Sélectionner une valeur Off-Axis en mm')
        self.labelExplicationOffset['font'] = font.Font(weight='bold')
        self.labelExplicationOffset.grid(row=0, column=0, columnspan=3)

        ### définition des labels pour expliquer quel axe correspond à quel offset
        self.labelOffsetGaucheDroite = ttk.Label(self.sousFrameDicomOffset, text='Gauche-Droite')
        self.labelOffsetGaucheDroite.grid(row=1, column=0)

        self.labelOffsetTetePied = ttk.Label(self.sousFrameDicomOffset, text='Tete-Pied')
        self.labelOffsetTetePied.grid(row=1, column=1)

        self.labelOffsetAntPost = ttk.Label(self.sousFrameDicomOffset, text='Ant-Post')
        self.labelOffsetAntPost.grid(row=1, column=2)

        ### Définition des entry d'offset
        self.valeurOffsetGaucheDroite = tk.IntVar()
        self.valeurOffsetGaucheDroite.set(0)
        self.entryGaucheDroite = tk.Entry(self.sousFrameDicomOffset, textvariable=self.valeurOffsetGaucheDroite,
                                          width=10)
        self.entryGaucheDroite.grid(row=2, column=0)

        self.valeurOffsetTetePied = tk.IntVar()
        self.valeurOffsetTetePied.set(0)
        self.entryTetePied = tk.Entry(self.sousFrameDicomOffset, textvariable=self.valeurOffsetTetePied, width=10)
        self.entryTetePied.grid(row=2, column=1)

        self.valeurOffsetAntPost = tk.IntVar()


        self.valeurOffsetAntPost.set(0)
        self.entryAntPost = tk.Entry(self.sousFrameDicomOffset, textvariable=self.valeurOffsetAntPost, width=10)
        self.entryAntPost.grid(row=2, column=2)
        ################################################################################################################################################################

        ################################################################################################################################################################
        ### définition du sous frame de choix de l'axe du RTDose
        ################################################################################################################################################################
        self.sousFrameAxeRTDose = Frame(self.frameDicomGeneral)  # , highlightbackground="gray", highlightthickness=1)
        self.sousFrameAxeRTDose.grid(row=4, column=0, sticky='w')
        ### Définition des checkbox pour afficher soit PDD ou profile du RTDose
        self.valeurRadioButtonPDD_Profil = tk.IntVar()
        self.radioButtonPDD = tk.Radiobutton(self.sousFrameAxeRTDose, text='PDD',
                                             variable=self.valeurRadioButtonPDD_Profil,
                                             value=1)  # , command=self.drawPDD_RTDose)
        self.radioButtonCrossPlane = tk.Radiobutton(self.sousFrameAxeRTDose, text='CrossPlane',
                                                    variable=self.valeurRadioButtonPDD_Profil,
                                                    value=2)  # , command = self.drawCrossPlane_RTDose)
        self.radioButtonInPlane = tk.Radiobutton(self.sousFrameAxeRTDose, text='InPlane',
                                                 variable=self.valeurRadioButtonPDD_Profil,
                                                 value=3)  # , command=self.drawInPlane_RTDose)
        self.radioButtonPDD.grid(row=0, column=0, ipadx=20)
        self.radioButtonCrossPlane.grid(row=0, column=1, padx=20)
        self.radioButtonInPlane.grid(row=0, column=2)
        ################################################################################################################################################################

        self.boutonLoad_MCC = ttk.Button(self.frameMCCGeneral, text='Open MCC file', command=self.selectMccFile)
        self.boutonLoad_MCC.grid(row=0, column=0, sticky='n')

        self.lblMCC_Ouvert = ttk.Label(self.frameMCCGeneral, text='MCC ouvert : ')
        self.lblMCC_Ouvert.grid(row=1, column=0, sticky='w')

        ### Combobox pour affichage des mesure du MCC
        self.combobox = ttk.Combobox(self.frameMCCGeneral, width=50)
        self.combobox.grid(row=2, column=0)

        ################################################################################################################################################################
        ### définition de la configuration du canvas de Matplotlib et des boutons d'affichage de la dose et du reset du graphique
        ################################################################################################################################################################
        ### Définition du canvas qui contiendra le tracé Matplotlib
        self.fig = Figure(figsize=(6, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frameTraceMatplotlib)
        #

        ### placing the canvas on the Tkinter window
        self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=3)
        self.canvas.draw()
        ################################################################################################################################################################
        ### Définition du bouton d'affichage du RTDose
        self.boutonDisplayRTDose = ttk.Button(self.frameTraceMatplotlib, text='Afficher la dose',
                                              command=self.getValueOffset)
        self.boutonDisplayRTDose.grid(row=1, column=0, padx=50)

        ### Bouton pour effacer les graphs
        self.boutonClear = ttk.Button(self.frameTraceMatplotlib, text='Clear all plots', command=self.clearPlots)
        self.boutonClear.grid(row=1, column=1)
        self.clear = False

        ### définition du bouton d'affichage du gamma
        self.boutonCalculGamma = ttk.Button(self.frameTraceMatplotlib, text='Calcul Gamma', command=self.calculGamma)
        self.boutonCalculGamma.grid(row=1, column=2)

        ### définition du bouton d'enregistrement de la figure
        self.boutonCalculGamma = ttk.Button(self.frameTraceMatplotlib, text='save fig', command=self.enregistrementPlot)
        self.boutonCalculGamma.grid(row=1, column=3)
        ################################################################################################################################################################

    def calculGamma(self):
        if self.objPlan == None or self.objMCC == None:
            tk.messagebox.showerror(title=None,
                                    message="Sélectionnez d'abord un RTDose et une mesure MCC avant de calculer le gamma")
            return
        else:
            # self.figGamma.clear()
            if self.valeurRadioButtonPDD_Profil.get() == 1:
                calculGamma = CalculGamma(self.abscisseDuDataFrame,
                                          self.ordonneesDuDataFrame,
                                          self.listePDD[:, 0],
                                          self.listePDD[:, 1]
                                          )
                self.traceMatplotlibGamma(self.listePDD[:, 0], calculGamma.gamma)
                # self.traceMatplotlibGamma(self.abscisseDuDataFrame, calculGamma.valid_gamma)

            elif self.valeurRadioButtonPDD_Profil.get() == 2:
                calculGamma = CalculGamma(self.abscisseDuDataFrame,
                                          self.ordonneesDuDataFrame,
                                          self.listeCrossPlaneDose[:, 0],
                                          self.listeCrossPlaneDose[:, 1]
                                          )
                self.traceMatplotlibGamma(self.listeCrossPlaneDose[:, 0], calculGamma.gamma)
                # self.traceMatplotlibGamma(self.abscisseDuDataFrame, calculGamma.gamma)

            else:
                calculGamma = CalculGamma(self.abscisseDuDataFrame,
                                          self.ordonneesDuDataFrame,
                                          self.listeInPlaneDose[:, 0],
                                          self.listeInPlaneDose[:, 1]
                                          )
                self.traceMatplotlibGamma(self.listeInPlaneDose[:, 0], calculGamma.gamma)
                # self.traceMatplotlibGamma(self.abscisseDuDataFrame, calculGamma.valid_gamma)

    def updateEntryValue(self):
        x = self.valeurOffsetGaucheDroite.get()
        y = self.valeurOffsetTetePied.get()
        z = self.valeurOffsetAntPost.get()
        self.valeurOffsetGaucheDroite.set(x)
        self.valeurOffsetTetePied.set(y)
        self.valeurOffsetAntPost.set(z)

    def selectDoseFile(self):
        """Fonction reliée au pushbutton de sélection du dicom dose. Quand le dicom est sélectionné,
        il est lu avec pydicom dans la classe LectureDicom avec la fonction dicomread_Dose. Elle prend
        en paramètre le fichier dicom ainsi que les coordonnées d'un éventuel offset dans l'ordre
        suivant : GD-TP-AP. Le RTPLAN aura été ouvert et lu avant, de là conversion de la position de l'iso
        du repère CT dans le repère de dose avec la méthode passageRepereCTVersDose. Puis on extrait le PDD
        """

        if self.objPlan == None:
            tk.messagebox.showerror(title=None, message="Sélectionnez d'abord un RTPLAN avant  d'ouvrir un RTDose")
            return

        filetypes = [('dicom files', '.dcm')]

        if self.mppg is not None and self.energie is not None :
            initial_dir = r'C:\Users\M11142\OneDrive - Centre Oscar Lambret\Truebeam\01 Acceptance - Commissioning - ' \
                          r'Mesures\02 Relatif - Model TPS\04 TPS\02 RT PLANS\MPPG %s\%s_%s' % (self.mppg,self.mppg,
                                                                                                self.energie)

        else:
            initial_dir = r'C:\Users\M11142\OneDrive - Centre Oscar Lambret\Truebeam\01 Acceptance - Commissioning - ' \
                          r'Mesures\02 Relatif - Model TPS\04 TPS\02 RT PLANS'

        print(initial_dir)
        self.filenameRTDose = fd.askopenfilename(title='Selectionner RTDose',
                                                 initialdir=initial_dir,
                                                 filetypes=filetypes)




        ### Définition du champs qui affiche le chemin du rtplan
        self.afficherCheminRTDOSE_Ouvert = tk.Label(self.sousFrameAffichageFichierOuvert, text=self.filenameRTDose)
        self.afficherCheminRTDOSE_Ouvert.grid(row=2, column=1)

    def getValueOffset(self):

        if self.valeurRadioButtonPDD_Profil.get() != 1 and self.valeurRadioButtonPDD_Profil.get() != 2 and self.valeurRadioButtonPDD_Profil.get() != 3:
            tk.messagebox.showerror(title=None, message="Sélectionnez si c'est un PDD ou un profil")

        elif self.filenameRTDose == None:
            tk.messagebox.showerror(title=None, message="Sélectionnez d abord un RTDose")


        elif self.listePDD is not None:
            self.executeLectureDicom(float(self.entryGaucheDroite.get()),
                                     float(self.entryTetePied.get()),
                                     float(self.entryAntPost.get())
                                     )

            if self.valeurRadioButtonPDD_Profil.get() == 1:
                self.preparationTraceRTDose(self.listePDD)
            elif self.valeurRadioButtonPDD_Profil.get() == 2:
                self.preparationTraceRTDose(self.listeCrossPlaneDose)
            else:
                self.preparationTraceRTDose(self.listeInPlaneDose)


        else:

            self.executeLectureDicom(float(self.entryGaucheDroite.get()),
                                     float(self.entryTetePied.get()),
                                     float(self.entryAntPost.get())
                                     )

    def executeLectureDicom(self, offsetGD, offsetTP, offsetAP):
        self.objPlan.dicomread_Dose(self.filenameRTDose, offsetGD, offsetTP, offsetAP)
        self.objPlan.passageRepereCTVersDose()
        self.listePDD = self.objPlan.pdd()
        self.listeCrossPlaneDose = self.objPlan.profilCrossPlane()
        self.listeInPlaneDose = self.objPlan.profilInPlane()

        if self.valeurRadioButtonPDD_Profil.get() == 1:
            self.preparationTraceRTDose(self.listePDD)
        elif self.valeurRadioButtonPDD_Profil.get() == 2:
            self.preparationTraceRTDose(self.listeCrossPlaneDose)
        else:
            self.preparationTraceRTDose(self.listeInPlaneDose)

    def preparationTraceRTDose(self, arrayDose):
        if self.valeurRadioButtonPDD_Profil.get() == 1:
            arrayDose[:, 1] = np.divide(arrayDose[:, 1], max(arrayDose[:, 1]))
            self.traceMatplotlibGeneral(arrayDose, 'RTDose')
        else:
            if self.echantillonnageMCC:
                x = 0
                diffArray = np.absolute(arrayDose[:, 0] - x)
                idx = diffArray.argmin()
                print('idx : ', idx, ' ', arrayDose[:, 0][idx])
                # arrayDose[:,1] = np.multiply(arrayDose[:,1], self.ordonneesDuDataFrame[np.where((self.abscisseDuDataFrame == 0))]/arrayDose[:,1][idx])
                arrayDose[:, 1] = np.divide(arrayDose[:, 1], max(arrayDose[:, 1]))

                ### j'ai mis un true pour afficher des mesures off-axis si problème d'abscissecar problème sens de lecture du RTDose
                ### Pour mesures centrées, enlever le True
                self.traceMatplotlibGeneral(arrayDose, 'RTDose')
            else:
                self.traceMatplotlibGeneral(arrayDose, 'RTDose')

    def selectPlanFile(self):
        """Fonction reliée au pushbutton de sélection du dicom plan. Quand le dicom est sélectionné,
        il est lu avec pydicom dans la classe LectureDicom avec la fonction dicomread_Plan. Elle prend
        en paramètre le fichier dicom.
        """
        filetypes = [('dicom files', '.dcm')]
        
        if self.mppg is not None and self.energie is not None :
            initial_dir = r'C:\Users\M11142\OneDrive - Centre Oscar Lambret\Truebeam\01 Acceptance - Commissioning - Mesures\02 Relatif - Model TPS\04 TPS\02 RT PLANS\MPPG %s\%s_%s' % (self.mppg,self.mppg, self.energie)

        else:
            initial_dir = r'C:\Users\M11142\OneDrive - Centre Oscar Lambret\Truebeam\01 Acceptance - Commissioning - Mesures\02 Relatif - Model TPS\04 TPS\02 RT PLANS'


        print(initial_dir)
        filename = fd.askopenfilename(title='Selectionner RTPlan',
                                      initialdir=initial_dir,
                                      filetypes=filetypes)





        ### Définition du champs qui affiche le chemin du rtplan
        # self.afficherCheminRTPLAN_Ouvert = tk.Label(self.sousFrameAffichageFichierOuvert, text =filename)
        # self.afficherCheminRTPLAN_Ouvert.grid(row=1, column=1)

        self.objPlan = Lecture_Dicom()
        self.objPlan.dicomread_Plan(filename)

    def selectMccFile(self):
        """Fonction reliée au pushbutton de sélection du MCC. Quand il est sélectionné,
        il est lu avec Pandas afin d'extraire toutes les mesures enregistrées (PDD ou profil)
        et tout est stocké dans un dictionnaire. On met ensuite toutes les clés du dictionnaire
        dans une combobox
        """
        filetypes = [('mcc files', '.mcc')]

        if self.mppg is not None and self.energie is not None :
            initialdir = r'C:\Users\M11142\OneDrive - Centre Oscar Lambret\Truebeam\01 Acceptance - Commissioning - ' \
                         r'Mesures\02 Relatif - Model TPS\04 TPS\01 Mesures cuve\MPPG %s' % (self.mppg)
        else:
            initialdir = r'C:\Users\M11142\OneDrive - Centre Oscar Lambret\Truebeam\01 Acceptance - Commissioning - Mesures\02 Relatif - Model TPS\04 TPS\01 Mesures cuve'

        self.filenameMCC = fd.askopenfilename(title='Selectionner MCC',
                                              initialdir=initialdir,
                                              filetypes=filetypes)


        # Utilisation d'expressions régulières pour extraire les valeurs recherchées
        mppg_match = re.search(r"/MPPG (\d+\.\d+)", self.filenameMCC)
        dsp_match = re.search(r"/DSP (\d+)", self.filenameMCC)
        energie_match = re.search(r"/(X\d+(?: FFF)?)\.mcc", self.filenameMCC)
        if energie_match is None:
            energie_match = re.search(r"/(X\d+(?: FFF)?)",  self.filenameMCC)

        if mppg_match:
            self.mppg = mppg_match.group(1)
            print("mppg =", self.mppg)
        if dsp_match:
            self.dsp = dsp_match.group(1)
            print("dsp =", self.dsp)
        if energie_match:
            self.energie_mcc = energie_match.group(1)
            self.energie = self.energie_mcc.replace("X06", "X6").replace("X6 FFF","X6FFF").replace("X06 FFF", "X6FFF").replace("X6 FFF", "X6FFF").replace("X10 FFF", "X10FFF")

            print("energie =", self.energie)


        ### Définition du champs qui affiche le chemin du mcc
        # self.afficherCheminMCC_Ouvert = tk.Label(self.frameMCCGeneral, text = self.filenameMCC)
        # self.afficherCheminMCC_Ouvert.grid(row=1, column=0, padx=80)

        ### instanciation de la classe EchantillonnageDoseMesure afin de savoir si le MCC a été ouvert
        ### cela permet de savoir comment afficher le RTDose dans la fonction selectDoseFile.
        ### Si le MCC n'a pas été ouvert, self.echantillonnageMCC vaudra None
        self.echantillonnageMCC = EchantillonnageDoseMesure()

        ### On instancie la classe LectureMccCuve afin de lire le MCC et de tout stocker dans un dictionnaire
        ### avec Pandas. La clé sera le setup de la mesure, la valeur sera les valeurs mesurées à la chambre
        self.objMCC = LectureMccCuve(self.filenameMCC)

        ### Ici on met à jour la combobox, c'est à dire qu'on affiche toutes les clés du dictionnaire
        ### donc tous les setup de mesure. Si on change de MCC, tout sera effacé et mis à jour
        self.updateCombobox(self.objMCC.listeCle)

    def updateCombobox(self, cleDictMCC):
        """Remplissage des lignes de la combobox avec les clés du dictionnaire du MCC.
        Appel de la fonction choixItemCombobox quand on sélectionne un item de la combobox
        """
        # n = tk.StringVar()
        # self.combobox = ttk.Combobox(self, width=50, textvariable=n)
        self.combobox['values'] = cleDictMCC
        # self.combobox.grid(row=1, column=0)
        self.combobox.bind('<<ComboboxSelected>>', self.choixItemCombobox)



    def choixItemCombobox(self, event):
        ### la variable self.itemSelected contient l'item de la combobox sélectionné
        self.itemSelected = self.combobox.get()

        print('a : ', self.itemSelected)


        # On récupères les proprioétés de la mesure sélectionnée
        # Utilisation d'expressions régulières pour extraire les valeurs recherchées
        curve_type_match = re.search(r'(INPLANE_PROFILE|CROSSPLANE_PROFILE|PDD)', self.itemSelected)
        field_size_match = re.search(r'Field Size = (\d+\.\d+) (\d+\.\d+)', self.itemSelected)
        depth_match = re.search(r'depth = (\d+\.\d+)', self.itemSelected)
        ssd_match = re.search(r'SSD = (\d+\.\d+)', self.itemSelected)
        offAxisInPlane_match = re.search(r'offAxisInPlane = (\d+\.\d+)', self.itemSelected)

        if curve_type_match :
            self.curve_type = curve_type_match.group(1)

        if field_size_match :
            self.field_size_x = float(field_size_match.group(1))
            self.field_size_y = float(field_size_match.group(2))
        if depth_match :
            self.depth = float(depth_match.group(1))

        if ssd_match :
            self.ssd = float(ssd_match.group(1))

        if offAxisInPlane_match :
            self.offAxisInPlane = float(offAxisInPlane_match.group(1))

        print("curve_type =", self.curve_type)
        print("Field size [Y,X] =", [self.field_size_y, self.field_size_x])
        print("depth =", self.depth)
        print("ssd =", self.ssd)

        # Initialisation des valeurs des champs de texte
        self.valeurOffsetAntPost.set(1)  # Change la valeur de la case à cocher à "cochée"
        self.entryAntPost.delete(0, tk.END)  # Efface le contenu actuel de la zone de texte

        nouvelle_valeur = round( (self.depth+self.ssd)-1000,1)
        self.entryAntPost.insert(0,nouvelle_valeur)

        self.entryTetePied.delete(0, tk.END)
        self.entryTetePied.insert(0, 0)

        if self.curve_type == 'PDD':
            self.valeurRadioButtonPDD_Profil.set(1)
        elif self.curve_type == 'INPLANE_PROFILE':
            self.valeurRadioButtonPDD_Profil.set(3)


        elif self.curve_type == 'CROSSPLANE_PROFILE':
            self.valeurRadioButtonPDD_Profil.set(2)

            # On ajoute l'offset inplane qui si la courbe mesurée est en crossplane
            self.entryTetePied.delete(0, tk.END)
            self.entryTetePied.insert(0, self.offAxisInPlane)




        ### on exécute la fonction miseEnFormeDesDonneesDuMCC afin de mettre en forme le PDD
        ### en normalisant par le max ou pour les profils selon méthode fogliata
        self.miseEnFormeDesDonneesDuMCC()

        ### ajout de cette condition pour savoir si le dicom a déjà été ouvert
        ### Si c'est le cas, comme self.echantillonnageMCC a été créé dans la fonction
        ### selectMccFile, on exécute la fonction echantillonnage PDD afin de garder
        ### dans le PDD les mêmes abscisses que ceux du MCC, pour faire une comparaison point par point
        ### puis on trace les graps du MCC et de la dose
        ### Si dicom n'a pas été ouvert avant, on trace uniquement le MCC
        # if self.objPlan:
        #     print('le plan a deja ete ouvert')
        #     # self.fig.clear()
        #     # # pdd = self.echantillonnageMCC.echantillonnagePDD(self.listePDD, self.donneesDuDataFrame)
        #     self.traceMatplotlibMCCDansFenetre(self.abscisseDuDataFrame, self.ordonneesDuDataFrame)
        #     # self.traceMatplotlibRtdoseDansFenetre(pdd)
        # else:
        #     self.traceMatplotlibMCCDansFenetre(self.abscisseDuDataFrame, self.ordonneesDuDataFrame)

        # self.traceMatplotlibMCCDansFenetre(self.abscisseDuDataFrame, self.ordonneesDuDataFrame)
        # print(self.arrayMCC)
        self.traceMatplotlibGeneral(self.arrayMCC, 'MCC')

    def miseEnFormeDesDonneesDuMCC(self):
        """Permet de normaliser au max les PDD et les profils sur l'axe selon Fogliata"""

        ### Conversion des valeurs de la clé du dictionnaire correspondant à
        ### l'item sélectionné dans le combobox en numpy array

        self.donneesDuDataFrame = []
        self.arrayMCC = []

        self.donneesDuDataFrame = self.objMCC.dictMCC[self.itemSelected].to_numpy()

        ### On définit les valeurs en abscisse
        self.abscisseDuDataFrame = self.donneesDuDataFrame[:, 0]

        # convertir toutes les données de self.abscisseDuDataFrame en float sans utiliser la fonction np.float
        for i in range(len(self.abscisseDuDataFrame)):
            self.abscisseDuDataFrame[i] = float(self.abscisseDuDataFrame[i])

        ### On définit les ordonnées selon que ce soit un PDD ou un profil
        if 'PDD' in self.itemSelected:
            self.ordonneesDuDataFrame = self.donneesDuDataFrame[:, 1]
            for i in range(len(self.ordonneesDuDataFrame)):
                self.ordonneesDuDataFrame[i] = float(self.ordonneesDuDataFrame[i])
            self.ordonneesDuDataFrame = np.divide(self.ordonneesDuDataFrame, max(self.ordonneesDuDataFrame))
        else:
            aNorm = 95.44
            bNorm = 0.0084
            cNorm = 0.1125
            dNorm = -0.0118
            eNorm = 0.00113
            self.renormalization_Value = (aNorm + bNorm * float(self.itemSelected.split()[4]) / 10 + cNorm * float(
                self.itemSelected.split()[-1]) / 10 / (1 + dNorm * float(
                self.itemSelected.split()[4]) / 10 + eNorm * float(
                self.itemSelected.split()[-1]) / 10))

            self.ordonneesDuDataFrame = self.donneesDuDataFrame[:, 1]
            for i in range(len(self.ordonneesDuDataFrame)):
                self.ordonneesDuDataFrame[i] = float(self.ordonneesDuDataFrame[i])

            # self.ordonneesDuDataFrame = np.multiply(self.ordonneesDuDataFrame, self.renormalization_Value / self.ordonneesDuDataFrame[np.where((self.abscisseDuDataFrame == 0))])

            ### décommenter cette ligne là pour analyser les profils off axis
            self.ordonneesDuDataFrame = np.divide(self.ordonneesDuDataFrame, max(self.ordonneesDuDataFrame))

        ### On regroupe les abscisses et les ordonnées dans une numpy array à 2D
        self.donneesDuDataFrame = np.c_[self.abscisseDuDataFrame, self.ordonneesDuDataFrame]

        self.arrayMCC = np.c_[self.abscisseDuDataFrame, self.ordonneesDuDataFrame]

    def update_plot(self):

        self.fig.clear()
        self.ax_1 = self.fig.add_subplot(111)


    def clearPlots(self):
        self.fig.clear()
        self.ax_1 = self.fig.add_subplot(111)



    def draw_plot(self,arrayMCC_Ou_Dose, label, xflip=False):
        self.ax_1.set_xlabel('mm')
        self.ax_1.set_ylabel('Dose mesurée (%)')

        self.ax_1.set_ylim([0, max(arrayMCC_Ou_Dose[:, 1]) * 1.1])
        self.ax_1.grid(True)


        if self.echantillonnageMCC:
            self.ax_1.set_title('mcc path : ' + self.filenameMCC.split('/')[-1] + '\n' +
                                'mesure analysee : ' + self.itemSelected,
                                loc='center',
                                wrap=True)
            self.ax_1.set_xlim([min(self.donneesDuDataFrame[:, 0]), max(self.donneesDuDataFrame[:, 0])])
        else:
            self.ax_1.set_xlim([min(arrayMCC_Ou_Dose[:, 0]), max(arrayMCC_Ou_Dose[:, 0])])

        ### Condition ajoutée dans le cas ces profils off-axis pour faire un flip des abscisses

        if 'RTDose' in label:
            color = 'red'
        else:
            color = 'blue'

        self.ax_1.plot(arrayMCC_Ou_Dose[:, 0], arrayMCC_Ou_Dose[:, 1], label=label, color=color)
        self.ax_1.legend(loc='best')
        self.canvas.draw()


    def traceMatplotlibGeneral(self, arrayMCC_Ou_Dose, label, xflip=False):



        if self.mccSelected == self.itemSelected:
            print("Le mcc n'a pas été modifié")

        # Si le dicom n'a pas déjà été tracé, on trace le mcc. On update le plot à chaque fois
        if label == 'MCC' and not self.RTDoseDejaTrace:
            print('Mcc sélectionné, RTDose pas encore tracé')
            self.update_plot()
            self.mcc_a_garder = arrayMCC_Ou_Dose
            self.draw_plot(arrayMCC_Ou_Dose, label, xflip)
            self.mccDejaTrace = True

        elif label == 'RTDose' and not self.mccDejaTrace:
            print('RTDose sélectionné, MCC pas encore tracé')
            self.update_plot()
            self.rtdose_a_garder = arrayMCC_Ou_Dose
            self.draw_plot(arrayMCC_Ou_Dose, label, xflip)
            self.RTDoseDejaTrace = True

        elif label == 'RTDose' and self.mccDejaTrace:
            print('RTDose sélectionné, MCC déjà tracé')
            self.update_plot()
            self.rtdose_a_garder = arrayMCC_Ou_Dose
            self.draw_plot(arrayMCC_Ou_Dose, label, xflip)
            self.draw_plot(self.mcc_a_garder, label= 'MCC',)
            self.RTDoseDejaTrace = True

        elif label == 'MCC' and self.RTDoseDejaTrace:
            print('MCC sélectionné, RTDose déjà tracé')
            self.update_plot()
            self.mcc_a_garder = arrayMCC_Ou_Dose
            self.draw_plot(arrayMCC_Ou_Dose, label, xflip)
            self.draw_plot(self.rtdose_a_garder, label= 'RTDose')
            self.mccDejaTrace = True

        elif label == 'RTDose' and self.RTDoseDejaTrace:
            print('RTDose sélectionné, RTDose déjà tracé')
            self.update_plot()
            self.rtdose_a_garder = arrayMCC_Ou_Dose
            self.draw_plot(arrayMCC_Ou_Dose, label, xflip)
            self.draw_plot(self.mcc_a_garder, label= 'MCC')
            self.RTDoseDejaTrace = True



    # def traceMatplotlibGamma(self, arrayMCC_Ou_Dose, gamma):
    #
    #     # ax_1 = self.fig.add_subplot(111)
    #     ax_2 = self.ax_1.twinx()
    #     ax_2.plot(arrayMCC_Ou_Dose, gamma, label='Gamma')
    #     ax_2.set_ylabel('Gamma mesurée (%)')
    #     # ax_2.set_xlim([min(arrayMCC_Ou_Dose), max(arrayMCC_Ou_Dose)])
    #     # ax_2.set_ylim([0, max(gamma) * 1.1])
    #     ax_2.grid(True)
    #
    #     line, = ax_2.plot(arrayMCC_Ou_Dose, gamma, 'o')
    #     snap_cursor = SnappingCursor(ax_2, line)
    #     self.fig.canvas.mpl_connect('motion_notify_event', snap_cursor.on_mouse_move)
    #     ax_2.legend()
    #     ax_2.show()
    #
    #     ### creating the Tkinter canvas containing the Matplotlib figure
    #     self.canvas.draw()
    #
    #     ### placing the canvas on the Tkinter window
    #     self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=3)

    def enregistrementPlot(self):
        folder = r'C:\Users\M11142\OneDrive - Centre Oscar Lambret\Truebeam\01 Acceptance - Commissioning - Mesures\02 Relatif - Model TPS\04 TPS\02 RT PLANS\MPPG %s\%s_%s' % (self.mppg,self.mppg,self.energie)
        # folder = r'G:\CAYEZ\temp\dose'
        self.fig.savefig(folder + '\\' + self.filenameMCC.split('/')[-1] + '  ' + self.itemSelected + '.png', dpi=600)
