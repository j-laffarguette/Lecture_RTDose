import pymedphys
import numpy as np

class CalculGamma():
    def __init__(self, abscisseMCC, ordonneesMCC, abscisseRTDose, ordonneesRTDose):
        self.abscisseMCC = abscisseMCC
        self.ordonneesMCC = ordonneesMCC

        self.abscisseRTDose = abscisseRTDose
        self.ordonneesRTDose = ordonneesRTDose

        self.valid_gamma = None

        self.gamma_options = {
            'dose_percent_threshold'   : 2,
            'distance_mm_threshold'    : 2,
            'lower_percent_dose_cutoff': 40,
            'interp_fraction'          : 100,  # Should be 10 or more for more accurate results
            'max_gamma'                : 2,
            'random_subset'            : None,
            'local_gamma'              : True,  # False indicates global gamma is calculated
            'ram_available'            : 2 ** 29  # 1/2 GB
                        }

        self.gamma = pymedphys.gamma(
            self.abscisseRTDose,self.ordonneesRTDose,
            self.abscisseMCC, self.ordonneesMCC,
            **self.gamma_options)

        # self.gamma = pymedphys.gamma(
        #     self.abscisseMCC,self.ordonneesMCC,
        #     self.abscisseRTDose, self.ordonneesRTDose,
        #     **self.gamma_options)

        self.valid_gamma = self.gamma[~np.isnan(self.gamma)]
        print('# of reference points with a valid gamma {0}'.format(len(self.valid_gamma)))
        # num_bins = (
        #         self.gamma_options['interp_fraction'] * self.gamma_options['max_gamma'])
        # self.bins = np.linspace(0, self.gamma_options['max_gamma'], num_bins + 1)
    
        if self.gamma_options['local_gamma']:
            gamma_norm_condition = 'Local gamma'
        else:
            gamma_norm_condition = 'Global gamma'
    
        pass_ratio = np.sum(self.valid_gamma <= 1) / len(self.valid_gamma)
        print('pass ratio : ', pass_ratio)
        print('le taux de passe est de : ', np.sum(self.valid_gamma <= 1) / len(self.valid_gamma))