from microlensing.Stars.stars import Stars

import numpy as np
import matplotlib.axes


class MagMap():

    def __init__(self, magnifications: np.ndarray, center: tuple, half_length: tuple, 
                 kappa_tot: float, shear: float, kappa_star: float, stars: Stars):
        '''
        :param magnifications: array of magnifications
        :param center: center of the magnification map
        :param half_length: half_length of the magnification map (distances from center to corner)
        :param kappa_tot: total convergence
        :param shear: shear
        :param kappa_star: convergence in point mass lenses
        :param stars: stars used to create the magnification map
        '''
        if not isinstance(magnifications, np.ndarray):
            self.magnifications = np.array(magnifications)
        else:
            self.magnifications = magnifications

        self.center = tuple(center)
        self.half_length = tuple(half_length)

        self.kappa_tot = kappa_tot
        self.shear = shear
        self.kappa_star = kappa_star
        self.stars = stars

    @property
    def mu_ave(self):
        return 1 / ((1 - self.kappa_tot)**2 - self.shear**2)

    @property
    def stellar_fraction(self):
        return self.kappa_star / self.kappa_tot

    @property
    def smooth_fraction(self):
        return 1 - self.kappa_star / self.kappa_tot

    @property
    def num_pixels(self):
        return (self.magnifications.shape[1], # axis 1 of array is y1 axis
                self.magnifications.shape[0]) # axis 0 of array is y2 axis

    @property
    def pixel_scales(self):
        return (2 * self.half_length[0] / self.num_pixels[0],
                2 * self.half_length[1] / self.num_pixels[1])

    @property
    def magnitudes(self):
        return -2.5 * np.log10(self.magnifications / np.abs(self.mu_ave))

    def plot(self, ax: matplotlib.axes.Axes, **kwargs):
        if 'vmin' not in kwargs.keys():
            kwargs['vmin'] = np.percentile(self.magnitudes.ravel(), 2.5)
        if 'vmax' not in kwargs.keys():
            kwargs['vmax'] = np.percentile(self.magnitudes.ravel(), 97.5)
        if 'cmap' not in kwargs.keys():
            kwargs['cmap'] = 'viridis_r'

        extent = [(self.center[0] - self.half_length[0]) / self.stars.theta_star,
                  (self.center[0] + self.half_length[0]) / self.stars.theta_star,
                  (self.center[1] - self.half_length[1]) / self.stars.theta_star,
                  (self.center[1] + self.half_length[1]) / self.stars.theta_star]

        img = ax.imshow(self.magnitudes, extent=extent, **kwargs)
        cbar = ax.get_figure().colorbar(img, label='microlensing $\\Delta m$ (magnitudes)')
        cbar.ax.invert_yaxis()

        ax.set_xlabel('$y_1 / \\theta_★$')
        ax.set_ylabel('$y_2 / \\theta_★$')

        ax.set_aspect(self.half_length[0] / self.half_length[1])

    def plot_hist(self, ax: matplotlib.axes.Axes, bins=None, **kwargs):
        if bins is None:
            vmin, vmax = (np.min(self.magnitudes), np.max(self.magnitudes))
            bins = np.arange(vmin - 0.01, vmax + 0.01, 0.01)

        ax.hist(self.magnitudes.ravel(), bins=bins, density=True, **kwargs)

        ax.set_xlabel('microlensing $\\Delta m$ (magnitudes)')
        ax.set_ylabel('p($\\Delta m$)')
        ax.invert_xaxis()
