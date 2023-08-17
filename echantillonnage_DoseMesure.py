import numpy as np

class EchantillonnageDoseMesure():
    def __init__(self):
        pass


    def echantillonnagePDD(self, listePDD, mcc):
        ### Création d'une array vide pour stocker les valeurs de position du PDD interpolées
        liste_Y_RTDose_Interpole = np.array([])

        ### Création de la 1ère dimension de l'array dans le sens Z tous les 0.1.
        ### Ajout de +0.1 au max liste car la dernière valeur est exclue sinon
        for i in np.arange(0, max(listePDD[:, 0]) + 0.1, 0.1):
            liste_Y_RTDose_Interpole = np.append(liste_Y_RTDose_Interpole, np.around(i, decimals=3))

        ### Création de la 2è dimension de l'array qui contient les valeurs de dose interpolées dans le sens Z tous les 0.1
        Dose_Z_interpole = np.interp(liste_Y_RTDose_Interpole,
                                     [listePDD[i][0] for i in range(len(listePDD))],
                                     [listePDD[j][1] for j in range(len(listePDD))]
                                     )

        ### Regroupement des 2 array précédemment crées
        newRTDose_Interpole = np.c_[liste_Y_RTDose_Interpole, Dose_Z_interpole]
        np.round(newRTDose_Interpole[:, 0], 2)

        ### Création d'un numpy array pour sauvegarder les valeurs de dose pour chaque position du détecteur
        # self.dose_Analyse = np.array([])
        dose_Analyse = np.array([])


        ### Boucle pour sauvegarder dans la numpy array créée juste avant les valeurs de dose de la numpy array
        ### interpolée qui correspondent aux positions du détecteur
        for i in range(len(mcc)):
            for j in range(len(newRTDose_Interpole)):
                if mcc[i][0] == newRTDose_Interpole[j][0]:
                    dose_Analyse = np.append(dose_Analyse, newRTDose_Interpole[j][0])
                    dose_Analyse = np.append(dose_Analyse, newRTDose_Interpole[j][1])

        dose_Analyse = dose_Analyse.reshape((len(dose_Analyse) // 2, 2))

        ### Sert à normaliser directement la dose au max
        dose_Analyse[:, 1] = np.divide(dose_Analyse[:, 1], max(dose_Analyse[:, 1]))

        return dose_Analyse

    def echantillonnageCrossPlane(self, listeCrossPlaneDose, mcc, normalizationValue):
        ### Création d'une array vide pour stocker les valeurs de position du CROSS PLANE interpolées  ###
        # Liste_X_RTDose_Interpole = np.array([])
        Liste_X_RTDose_Interpole_Modif = np.array([])

        ### Création de la 1ère dimension de l'array dans le sens X tous les 0.1. Ajout de +0.1 car la dernière valeur est exclue sinon ###
        ### J'ai pris comme borne de la boucle les positions extrêmes du fichier MCC afin que le profil du TPS ne dépasse pas celui du MCC.
        ### Ajout d'un np.around sur l'indice i sinon pour certaines valeurs il mettait x.00000000000000003
        for i in np.arange(mcc[0][0], mcc[-1][0] + 0.1, 0.01):
            Liste_X_RTDose_Interpole_Modif = np.append(Liste_X_RTDose_Interpole_Modif, np.around(i, decimals=3))

        ### Création de la 2è dimension de l'array qui contient les valeurs de dose interpolées dans le sens Z tous les 0.5 ###
        Dose_X_interpole = np.interp(Liste_X_RTDose_Interpole_Modif, [listeCrossPlaneDose[i][0] for i in range(len(listeCrossPlaneDose))],
                                     [listeCrossPlaneDose[j][1] for j in range(len(listeCrossPlaneDose))])

        ### Regroupement des 2 array précédemment crées ###
        newRTDose_X_Interpole = np.c_[Liste_X_RTDose_Interpole_Modif, Dose_X_interpole]
        np.round(newRTDose_X_Interpole[:, 0], 2)

        ### Création d'un numpy array pour sauvegarder les valeurs de dose pour chaque position du détecteur ###
        dose_CrossPlane_Analyse = np.array([])

        ### Boucle pour sauvegarder dans la numpy array créée juste avant les valeurs de dose de la numpy array interpolée qui correspondent aux positions du détecteur
        for i in range(len(mcc)):
            for j in range(len(newRTDose_X_Interpole)):
                if mcc[i][0] == newRTDose_X_Interpole[j][0]:
                    dose_CrossPlane_Analyse = np.append(dose_CrossPlane_Analyse, newRTDose_X_Interpole[j][0])
                    dose_CrossPlane_Analyse = np.append(dose_CrossPlane_Analyse, newRTDose_X_Interpole[j][1])

        dose_CrossPlane_Analyse = dose_CrossPlane_Analyse.reshape(len(dose_CrossPlane_Analyse) // 2, 2)
        

        ### Renormalisation du RTDose
        dose_CrossPlane_Analyse[:, 1] = np.multiply(dose_CrossPlane_Analyse[:, 1], normalizationValue / dose_CrossPlane_Analyse[np.where(dose_CrossPlane_Analyse[:, 0] == 0)[0][0]][1])

        return dose_CrossPlane_Analyse

    def echantillonnageInPlane(self, listeInPlane_rtdose, mcc, normalizationValue):
        ### Création d'une array vide pour stocker les valeurs de position du CROSS PLANE interpolées  ###
        # Liste_X_RTDose_Interpole = np.array([])
        Liste_Z_RTDose_Interpole_Modif = np.array([])

        ### Création de la 1ère dimension de l'array dans le sens X tous les 0.1. Ajout de +0.1 car la dernière valeur est exclue sinon ###
        ### J'ai pris comme borne de la boucle les positions extrêmes du fichier MCC afin que le profil du TPS ne dépasse pas celui du MCC.
        ### Ajout d'un np.around sur l'indice i sinon pour certaines valeurs il mettait x.00000000000000003
        for i in np.arange(mcc[0][0], mcc[-1][0] + 0.1, 0.01):
            Liste_Z_RTDose_Interpole_Modif = np.append(Liste_Z_RTDose_Interpole_Modif, np.around(i, decimals=3))

        ### Création de la 2è dimension de l'array qui contient les valeurs de dose interpolées dans le sens Z tous les 0.5 ###
        Dose_Z_interpole = np.interp(Liste_Z_RTDose_Interpole_Modif, [listeInPlane_rtdose[i][0] for i in range(len(listeInPlane_rtdose))],
                                     [listeInPlane_rtdose[j][1] for j in range(len(listeInPlane_rtdose))])

        ### Regroupement des 2 array précédemment crées ###
        newRTDose_Z_Interpole = np.c_[Liste_Z_RTDose_Interpole_Modif, Dose_Z_interpole]
        np.round(newRTDose_Z_Interpole[:, 0], 2)

        ### Création d'un numpy array pour sauvegarder les valeurs de dose pour chaque position du détecteur ###
        dose_InPlane_Analyse = np.array([])

        ### Boucle pour sauvegarder dans la numpy array créée juste avant les valeurs de dose de la numpy array interpolée qui correspondent aux positions du détecteur
        for i in range(len(mcc)):
            for j in range(len(newRTDose_Z_Interpole)):
                if mcc[i][0] == newRTDose_Z_Interpole[j][0]:
                    dose_InPlane_Analyse = np.append(dose_InPlane_Analyse, newRTDose_Z_Interpole[j][0])
                    dose_InPlane_Analyse = np.append(dose_InPlane_Analyse, newRTDose_Z_Interpole[j][1])

        dose_InPlane_Analyse = dose_InPlane_Analyse.reshape(len(dose_InPlane_Analyse) // 2, 2)

        ### Renormalisation du RTDose
        dose_InPlane_Analyse[:, 1] = np.multiply(dose_InPlane_Analyse[:, 1],
                                                         normalizationValue / dose_InPlane_Analyse[np.where(dose_InPlane_Analyse[:, 0] == 0)[0][0]][1])

        return dose_InPlane_Analyse