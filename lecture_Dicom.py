import pydicom as dicom
import numpy as np
import matplotlib.pyplot as plt


class Lecture_Dicom():
    def __init__(self):
        pass

    def dicomread_Dose(self, rtdose, offAxisValueLeftRight, offAxisValueSupInf, offAxisValueAntPost):
        self.dsRD = dicom.read_file(rtdose)

        ### Origine de la grille de dose
        coordOriginRD = self.dsRD.ImagePositionPatient
        self.coordOriginDoseGrid_X = coordOriginRD[0]
        self.coordOriginDoseGrid_Y = coordOriginRD[1]
        self.coordOriginDoseGrid_Z = coordOriginRD[2]
        print("OrigineGrille Dose: x --> ",
              self.coordOriginDoseGrid_X, "  y --> ",
              self.coordOriginDoseGrid_Y, " z --> ",
              self.coordOriginDoseGrid_Z
              )

        ### Taille de la grille de dose
        self.Imax_DoseGrid = self.dsRD.Columns
        self.Jmax_DoseGrid = self.dsRD.Rows
        self.Kmax_DoseGrid = self.dsRD.NumberOfFrames

        ### Resolution de la grille de dose
        PixelSpacingRD = self.dsRD.PixelSpacing
        self.pixelSpacingDoseGrid_X = PixelSpacingRD[0]
        self.pixelSpacingDoseGrid_Y = PixelSpacingRD[1]
        self.pixelSpacingDoseGrid_Z = self.dsRD.SliceThickness
        print("Resolution", self.pixelSpacingDoseGrid_X, self.pixelSpacingDoseGrid_Y, self.pixelSpacingDoseGrid_Z)

        ### Valeurs de l'offset qui seront appliquées à l'iso pour des analyses off axis
        self.offAxisValueLeftRight = offAxisValueLeftRight
        self.offAxisValueSupInf = offAxisValueSupInf
        self.offAxisValueAntPost = offAxisValueAntPost

    def dicomread_Plan(self, rtplan):
        self.dsRP = dicom.read_file(rtplan)

        ### Isocentre de traitement
        Isocenter = self.dsRP.BeamSequence[0].ControlPointSequence[0].IsocenterPosition
        self.x_Iso = Isocenter[0]
        self.y_Iso = Isocenter[1]
        self.z_Iso = Isocenter[2]
        print("Coordonnees isocentre dans repere CT : x --> ",
              self.x_Iso, " y --> ",
              self.y_Iso, " z --> ",
              self.z_Iso
              )

        ### calcul de la profondeur de l'iso
        DSP = self.dsRP.BeamSequence[0].ControlPointSequence[0].SourceToSurfaceDistance
        DSA = self.dsRP.BeamSequence[0].SourceAxisDistance
        self.profIso = DSA - DSP

    def passageRepereCTVersDose(self):
        ### Conversion des coordonnees du point iso en (i,j,k) dans le RT dose ###
        self.i_isoDoseGrid = ((self.x_Iso + self.offAxisValueLeftRight) - self.coordOriginDoseGrid_X) / self.pixelSpacingDoseGrid_X
        self.j_isoDoseGrid = ((self.y_Iso + self.offAxisValueAntPost) - self.coordOriginDoseGrid_Y) / self.pixelSpacingDoseGrid_Y
        self.k_isoDoseGrid = ((self.z_Iso + self.offAxisValueSupInf) - self.coordOriginDoseGrid_Z) / self.pixelSpacingDoseGrid_Z
        print("Coordonnees isocentre dans repere RT Dose : x --> ",
              self.i_isoDoseGrid, " y --> ",
              self.j_isoDoseGrid, " z --> ",
              self.k_isoDoseGrid
              )

        ### Infos concernant le code  ###
        # Dans le référentiel du RTDose : X--> Droite-Gauche ; Z--> Ant-Post ; Y--> Tête-Pied
        # Dans le référentiel du SCANNE : X--> Droite-Gauche ; Y--> Ant-Post ; Z--> Tête-Pied
        # X = i*DeltaX + X0  i:dimension array en X ; DeltaX:pixelSpacing ; X0:origine grille ; X:coordonnee dernier voxel en X
        # Y = j*DeltaY + Y0
        # Z = k*DeltaZ + Z0
        # i ; j ; k correspondent aux dimensions de la pixel array du RTDose. Le but étant de les déterminer

    def pdd(self):
        self.listePDD = np.array([])

        ### Détermination du 1er voxel de la grille de dose en ANT-POST qui est dans l'external ###
        ### Sinon on obtient plein de zéros si la grille de dose commence loin de l'external ###
        ### La version initiale du code c'était ça :
        ### J_Surface = abs((self.coordOriginDoseGrid_Y - (self.y_Iso - self.profIso)) / self.pixelSpacingDoseGrid_Y)
        ### je l'ai écrit comme ça pour être raccord avec la ligne où on calcule self.i_isoDoseGrid
        J_Surface = ((self.y_Iso - self.profIso) - self.coordOriginDoseGrid_Y) / self.pixelSpacingDoseGrid_Y
        Y = 0
        for l in np.arange(int(np.around(J_Surface)), self.Jmax_DoseGrid - 1):
        # for l in np.arange(int(J_Surface), self.Jmax_DoseGrid - 1):
            ### print(Y, dsRD.pixel_array[int(k_iso),l,int(i_iso)]) #(k,j,i) pour être sûr afficher dsRD.pixel_array et regarder la taille
            self.listePDD = np.append(self.listePDD, Y)

            ### ici la pixel array se lit dans le sens (k,j,i) car quand on regarde la shape, elle est de la forme
            ### (DimTêtePied,DimAntPost,DimGaucheDroite) et dans le référentiel du scanner
            ### le têtePied c'est en Z et ici on l'a associé à l'indice k
            ### le AntPost c'est en Y et ici on l'a associé à l'indice j
            ### le GaucheDroite c'est en X et ici on l'a associé à l'indice i
            self.listePDD = np.append(self.listePDD,
                                      self.dsRD.pixel_array[int(np.around(self.k_isoDoseGrid)),
                                                            l,
                                                            int(np.around(self.i_isoDoseGrid))]
                                      )
            Y = Y + self.pixelSpacingDoseGrid_Y


        self.listePDD = self.listePDD.reshape(self.listePDD.shape[0] // 2, 2)
        self.listePDD[:, 1] = self.listePDD[:, 1] * self.dsRD.DoseGridScaling

        return self.listePDD

    def profilCrossPlane(self):
        self.listeCrossPlane = np.array([])
        #  Crossplane (Gauche-Droite)
        X = 0
        for l in range(0, self.Imax_DoseGrid, int(self.pixelSpacingDoseGrid_X)):
            # print(X, dsRD.pixel_array[int(k_iso),int(j_iso),l])
            self.listeCrossPlane = np.append(self.listeCrossPlane, X)
            self.listeCrossPlane = np.append(self.listeCrossPlane, self.dsRD.pixel_array[int(self.k_isoDoseGrid),
                                                                                         int(self.j_isoDoseGrid),
                                                                                         l]
                                             )
            X = X + self.pixelSpacingDoseGrid_X

        self.listeCrossPlane = self.listeCrossPlane.reshape(len(self.listeCrossPlane) // 2, 2)
        self.listeCrossPlane[:,1] = self.listeCrossPlane[:,1]*self.dsRD.DoseGridScaling

        ### Cette array permet de shifter l'abscisse car le RTDose commence a zero alors que la cuve c'est symetrique par rapport à l'iso
        self.listeCrossPlane[:, 0] = np.subtract(self.listeCrossPlane[:, 0], self.i_isoDoseGrid)
        
        return self.listeCrossPlane

    
    def profilInPlane(self):
        self.listeInPlane = np.array([])

        #  Inplane (Tete-Pied)
        Z = 0
        for l in range(0, self.Kmax_DoseGrid, int(self.pixelSpacingDoseGrid_Z)):
            # print(X, dsRD.pixel_array[int(k_iso),int(j_iso),l])
            self.listeInPlane = np.append(self.listeInPlane, Z)
            self.listeInPlane = np.append(self.listeInPlane, self.dsRD.pixel_array[l,
                                                                                   int(self.j_isoDoseGrid),
                                                                                   int(self.i_isoDoseGrid)]
                                          )
            Z = Z + self.pixelSpacingDoseGrid_Z

        self.listeInPlane = self.listeInPlane.reshape(len(self.listeInPlane) // 2, 2)
        self.listeInPlane[:, 1] = self.listeInPlane[:, 1] * self.dsRD.DoseGridScaling

        ### Cette array permet de shifter l'abscisse car le RTDose commence a zero alors que la cuve c'est symetrique par rapport à l'iso
        self.listeInPlane[:, 0] = -np.subtract(self.listeInPlane[:, 0], self.k_isoDoseGrid)

        return self.listeInPlane