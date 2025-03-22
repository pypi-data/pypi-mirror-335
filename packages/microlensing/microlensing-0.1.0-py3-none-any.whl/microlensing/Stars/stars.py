import numpy as np


class Stars():

    def __init__(self, rectangular: bool, corner, theta_star, stars):
        '''
        :param rectangular: whether star field is rectangualr or circular
        :param corner: corner of the star field, assuming it is centered at (0,0)
        :param theta_star: Einstein radius of a unit mass point lens
        :param stars: array of star positions and masses (x1, x2, m)
        '''

        self.rectangular = rectangular

        self.corner = tuple(corner)

        self.theta_star = theta_star

        if not isinstance(stars, np.ndarray):
            self.stars = np.array(stars)
        else:
            self.stars = stars

    @property
    def num_stars(self):
        return self.stars.shape[0]

    @property
    def mean_mass_actual(self):
        return np.mean(self.stars[:, 2])

    @property
    def mean_mass2_actual(self):
        return np.mean(self.stars[:, 2]**2)

    @property
    def mean_mass2_ln_mass_actual(self):
        return np.mean(self.stars[:, 2]**2 * np.log(self.stars[:, 2]))

    def plot(self, ax, **kwargs):
        if 's' not in kwargs.keys() and 'sizes' not in kwargs.keys():
            kwargs['s'] = 10 * self.stars[:, 2]
        else:
            kwargs['s'] = kwargs['s'] * self.stars[:, 2]
        if 'c' not in kwargs.keys() and 'color' not in kwargs.keys():
            kwargs['c'] = 'black'
        if 'marker' not in kwargs.keys():
            kwargs['marker'] = '*'


        ax.scatter(self.stars[:, 0] / self.theta_star,
                   self.stars[:, 1] / self.theta_star,
                   **kwargs)

        ax.set_xlabel('$x_1 / \\theta_★$')
        ax.set_ylabel('$x_2 / \\theta_★$')

        ax.set_aspect(self.corner[0] / self.corner[1])
