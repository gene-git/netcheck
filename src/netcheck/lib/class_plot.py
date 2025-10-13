'''
Plot tool
'''
import os
import matplotlib.pyplot as plt

from .class_conf import parse_args_init
from .class_plotdata import PlotData


class Plot:
    '''
    Generate Plot from netcheck csv output file
    '''
    def __init__(self):
        self.file: str = ''
        self.pdf: str = ''
        self.start: str = 'all'
        self.end: str = 'all'
        self.dir: str = './'
        self.show: bool = False

        self.initialize()
        self.data = PlotData(self.file)

    def initialize(self):
        '''
        Command line options
        '''
        opts = get_avail_options()
        par = parse_args_init('netcheck-plot', opts)
        parsed = par.parse_args()
        if parsed:
            for (opt, val) in vars(parsed).items():
                setattr(self, opt, val)

        if self.file:
            if self.pdf:
                if self.pdf.endswith('.pdf'):
                    self.pdf = self.pdf
                else:
                    self.pdf = f'{self.pdf}.pdf'
            else:
                fname = os.path.basename(self.file)
                self.pdf = os.path.join(self.dir, f'{fname}.pdf')
            pdf_dir = os.path.dirname(self.pdf)
            os.makedirs(pdf_dir, exist_ok=True)

    def do_plot(self):
        '''
        Make plot
        '''
        # set date range
        self.data.date_range(self.start, self.end)

        # make plot
        ts = self.data.loss_series()

        date_range = str(ts.index[0]) + ' to ' + str(ts.index[-1])

        plt.plot(ts.index, ts.values)
        plt.xlabel(f'Date Time\n{date_range}')
        plt.ylabel('Loss Rate %')
        plt.title('Network Loss Rates')

        options = {'linestyle': '--',
                   'linewidth': 0.5,
                   'color': 'gray'
                   }
        plt.grid(visible=True,
                 which='both',
                 axis='both',
                 **options)

        plt.gcf().autofmt_xdate()

        # Display the plot
        plt.savefig(self.pdf)
        if self.show:
            plt.show()


def get_avail_options():
    '''
    Command line
    '''
    opts = []
    val: str | bool | None

    val = './pdf'
    ohelp = f'Directory to write plot pdf file ({val})'
    opt = [('-d', '--dir'), {'default': val, 'help': ohelp}]
    opts.append(opt)

    val = 'all'
    ohelp = f'End time : absolute or relative days ({val})'
    opt = [('-e', '--end'), {'default': val, 'help': ohelp}]
    opts.append(opt)

    val = 'data'
    ohelp = f'Input csv file ({val})'
    opt = [('-f', '--file'), {'default': val, 'help': ohelp}]
    opts.append(opt)

    val = ''
    ohelp = 'Output PDF : if not specified will be based on input filename'
    opt = [('-o', '--out'), {'default': val, 'help': ohelp}]
    opts.append(opt)

    val = 'all'
    ohelp = f'Start time : absolute or relative days ({val})'
    opt = [('-s', '--start'), {'default': val, 'help': ohelp}]
    opts.append(opt)

    val = False
    ohelp = f'Show plot in terminal ({val})'
    opt = [('-sh', '--show'), {'action': 'store_true', 'help': ohelp}]
    opts.append(opt)

    return opts
