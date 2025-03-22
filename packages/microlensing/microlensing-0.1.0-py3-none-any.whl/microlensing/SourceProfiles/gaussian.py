import numpy as np


class Gaussian():

    def __init__(self, radius: int, max_radius: int = None):
        '''
        :param radius: radius of the disk in pixels that contains 0.999 of the
                       flux
        :param max_radius: maximum radius of the 2D profile.
                           by construction, providing a maximum radius r
                           means the profile always has a shape (2 * r + 1)^2.
                           default value is the radius
        '''
        self.radius = radius

        if max_radius is None:
            max_radius = self.radius

        y, x = np.ogrid[-max_radius: max_radius + 1,
                        -max_radius: max_radius + 1]
        mask = x**2 + y**2 <= self.radius**2

        # for a 2D Gaussian, 0.999 of the PDF lies within r = 3.7169222 * sigma
        self.sigma = self.radius / 3.7169222

        if self.sigma == 0:
            kernel = np.ones(mask.shape)
        else:
            kernel = np.exp(-(x**2 + y**2)/(2 * self.sigma**2))
        kernel[np.logical_not(mask)] = 0

        self.profile = kernel
        self.weight = np.sum(kernel)

    @property
    def half_light_radius(self):

        # for a 2D gaussian, 0.5 of the PDF (i.e. the half-light radius) is
        # at r_0.5 = 1.1774100 * sigma, or equivalently
        # at r_0.5 = r_0.999 / 3.1568630
        return self.radius / 3.1568630


class Gaussians():

    def __init__(self, max_radius: int, min_radius: int = None):
        '''
        :param max_radius: maximum radius of the 2D profiles in pixels that
                           contains 0.999 of the flux
        :param radius: minimum radius of the 2D profiles in pixels
        '''
        if min_radius is None:
            self.min_radius = 0

        self.radii, y, x = np.ogrid[min_radius: max_radius + 1,
                                    -max_radius: max_radius + 1,
                                    -max_radius: max_radius + 1]
        mask = x**2 + y**2 <= self.radii**2

        # for a 2D Gaussian, 0.999 of the PDF lies within r = 3.7169222 * sigma
        self.sigma = self.radii / 3.7169222

        self.sigma[self.sigma == 0] = 1  # to avoid division by zero below
        kernel = np.exp(-(x**2 + y**2)/(2 * self.sigma**2))
        kernel[np.logical_not(mask)] = 0

        self.profiles = kernel
        self.weights = np.sum(kernel, axis=0)

    @property
    def half_light_radii(self):

        # for a 2D gaussian, 0.5 of the PDF (i.e. the half-light radius) is
        # at r_0.5 = 1.1774100 * sigma, or equivalently
        # at r_0.5 = r_0.999 / 3.1568630
        return self.radii / 3.1568630
