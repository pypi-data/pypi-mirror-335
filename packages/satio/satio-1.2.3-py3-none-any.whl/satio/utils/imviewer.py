import numpy as np
import matplotlib.pyplot as plt

from IPython.display import display
import ipywidgets as widgets


class ImViewer:

    def __init__(self, *arrs, max_cols=3, titles=None, vmins=None, vmaxs=None):

        self.idx = 0
        self.n_ids = arrs[0].shape[0]
        self.arrs = arrs

        rows, cols = self._get_rows_cols(max_cols)
        self.fig, self.axs = plt.subplots(rows, cols, sharex=True, sharey=True)

        if len(arrs) == 1:
            self.axs = np.array([self.axs])

        self.vmins = vmins
        self.vmaxs = vmaxs

        self.titles = (titles if titles is not None
                       else [str(i) for i in range(self.n_ids)])

        button_prev = widgets.Button(description="Prev")  # type: ignore
        button_next = widgets.Button(description="Next")  # type: ignore

        display(button_prev, button_next)

        def click_prev(b):
            self.idx = max(0, self.idx - 1)
            self.show()

        def click_next(b):
            self.idx = min(self.idx + 1, self.n_ids - 1)
            self.show()

        button_prev.on_click(click_prev)
        button_next.on_click(click_next)

        @widgets.interact(index=(0, self.n_ids - 1, 1))
        def slider(index):
            self.idx = index
            self.show()

        @widgets.interact(title=self.titles)
        def drop_down_title(title):
            self.idx = self.titles.index(title)
            self.show()

        self.show()

    def _get_rows_cols(self, max_cols):
        n_arrs = len(self.arrs)
        if n_arrs <= max_cols:
            cols = n_arrs
            rows = 1
        else:
            cols = max_cols
            rows = (n_arrs // max_cols) + 1

        return rows, cols

    def show(self):
        ims = [arr[self.idx, ...] for arr in self.arrs]
        self.imshow(self.axs.flatten(),
                    *ims,
                    vmins=self.vmins,
                    vmaxs=self.vmaxs,
                    title=self.titles[self.idx])

    @staticmethod
    def imshow(axs, *ims, vmins, vmaxs, title):

        if vmins is None:
            vmins = [None for i in range(len(ims))]

        if vmaxs is None:
            vmaxs = [None for i in range(len(ims))]

        for im, ax, vmin, vmax in zip(ims,
                                      axs[:len(ims)],
                                      vmins,
                                      vmaxs):

            ax.imshow(im, vmin=vmin, vmax=vmax)

        ax.set_title(title)  # type: ignore
