import numpy as np


class UniformDisk():

    def __init__(self, radius: int, max_radius: int = None):
        '''
        :param radius: radius of the disk in pixels
        :param max_radius: maximum radius of the 2D profile.
                           by construction, providing a maximum radius r
                           means the profile always has a shape (2 * r + 1)^2.
                           default value is the radius
        '''
        self.radius = radius

        if max_radius is None:
            max_radius = self.radius

        # use np.int8 to minimize memory, since it is just 0s and 1s
        kernel = np.zeros((2 * max_radius + 1, 2 * max_radius + 1),
                          dtype=np.int8)

        y, x = np.ogrid[-max_radius: max_radius + 1,
                        -max_radius: max_radius + 1]
        mask = x**2 + y**2 <= self.radius**2
        kernel[mask] = 1

        self.profile = kernel
        self.weight = np.sum(kernel)

    @property
    def half_light_radius(self):
        return self.radius / np.sqrt(2)


class UniformDisks():

    def __init__(self, max_radius: int, min_radius: int = None):
        '''
        :param max_radius: maximum radius of the 2D profiles in pixels
        :param radius: minimum radius of the 2D profiles in pixels
        '''
        if min_radius is None:
            min_radius = 0

        # use np.int8 to minimize memory, since it is just 0s and 1s
        kernel = np.zeros((max_radius - min_radius + 1,
                           2 * max_radius + 1, 2 * max_radius + 1),
                          dtype=np.int8)

        self.radii, y, x = np.ogrid[min_radius: max_radius + 1,
                                    -max_radius: max_radius + 1,
                                    -max_radius: max_radius + 1]
        mask = x**2 + y**2 <= self.radii**2
        kernel[mask] = 1

        self.profiles = kernel
        self.weights = np.sum(kernel, axis=0)

    @property
    def half_light_radii(self):
        return self.radii / np.sqrt(2)
