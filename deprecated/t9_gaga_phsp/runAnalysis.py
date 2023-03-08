#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import click
import gatetools as gt
import itk
import matplotlib.pyplot as plt
import numpy as np

logger = logging.getLogger(__name__)


def read_images(folder, scale):
    print(folder)
    f = os.path.join(folder, 'dose-Edep.mhd')
    img = itk.imread(f)
    data = itk.array_from_image(img)
    data = data * scale

    f = os.path.join(folder, 'dose-Edep-Uncertainty.mhd')
    img_s = itk.imread(f)
    data_s = itk.array_from_image(img_s)

    return img, data, data_s


def plot_images_profiles(ax, img, label, scale, axe_sum1=2, axe_sum2=1):
    data = itk.GetArrayViewFromImage(img) * scale
    y = np.sum(data, axe_sum1)
    y = np.sum(y, axe_sum2)
    x = np.arange(len(y)) * img.GetSpacing()[2]
    ax.plot(x, y, label=label)
    ax.legend()


def relative_uncertainty(folders, scale, factor):
    img1, data1, uncert1 = read_images(folders[0], float(scale[0]))
    img2, data2, uncert2 = read_images(folders[1], float(scale[1]))

    myfontsize = 18
    myfontsize_tic = 15
    myfontsize_title = 15

    # plot
    fig, ax = plt.subplots(ncols=1, nrows=2, figsize=(25, 10))
    a = ax[0]
    plot_images_profiles(a, img1, folders[0], float(scale[0]))
    plot_images_profiles(a, img2, folders[1], float(scale[1]))
    a = ax[1]
    plot_images_profiles(a, img1, folders[0], float(scale[0]), axe_sum1=0, axe_sum2=1)
    plot_images_profiles(a, img2, folders[1], float(scale[1]), axe_sum1=0, axe_sum2=1)
    n = f'{folders[1]}_test.png'
    print('Save image test figure :', n)
    plt.savefig(n)

    # param
    f = float(factor)  # 0.05

    # detect the max with quantile to be a bit more robust
    mask = np.ones_like(data2)
    mi = np.amin(data2[mask == 1])
    ma = np.amax(data2[mask == 1])
    mean = np.mean(data2[mask == 1])
    med = np.median(data2[mask == 1])
    print('Data (no mask): min max mean med', mi, ma, mean, med)
    q = np.amax(data2)
    print('Data max = ', q)
    q = np.quantile(data2, 0.99999)
    print('Data maxQ = ', q)
    print('Data maxQ*f = ', q * f,
          ' <-- only pixels with value larger than this value are considered (below is "noise")')
    mask = np.where(data2 < q * f, 0, mask)

    # compute uncert
    uncert2_d = uncert2 * data2

    # compute sigma
    sigma1 = np.sqrt(uncert1 * uncert1 + uncert2_d * uncert2_d)
    sigma1 = sigma1[mask == 1]

    print('Nb pixels before mask: ', data1.size)
    print('Nb pixels after mask :', len(sigma1))

    # compute relative difference
    def compute_diff(data1, data2):
        diff = (data1 - data2)  # /data1
        print('Min and max relative difference: ', np.amin(diff), np.amax(diff))
        return diff

    d1 = data1[mask == 1]
    d2 = data2[mask == 1]
    amax = np.quantile(d1, 0.999)
    print('For normalisation use max value', amax)
    amean = np.mean(d1)
    amean = amax
    diff1 = compute_diff(d1, d2) / amean

    u1 = uncert1[mask == 1]
    u2 = uncert2[mask == 1]
    print(f'Mean uncert {np.mean(u1) * 100}% {np.mean(u2) * 100}%')
    print('Mean sigma  {}%'.format(np.mean(sigma1) / np.mean(d1)))

    # plot histo
    fig, ax = plt.subplots(1, 2, figsize=(15, 8))
    fs = myfontsize
    a = ax[0]
    q1 = np.quantile(diff1, 0.01)
    q2 = np.quantile(diff1, 0.99)
    print('Quantile for H', q1, q2)
    l1 = f'PHSP1 vs GAN $\mu=${np.mean(diff1) * 100.0:.2f}% '
    a.hist(diff1, 200, range=(q1, q2),
           density=False, facecolor='g', alpha=0.3,
           label=l1)
    a.legend(loc='center left', prop={'size': myfontsize_title})
    x1 = np.mean(diff1)
    a.axvline(x=x1, color='k')
    a.set_xlabel('Difference %', fontsize=fs)
    a.set_ylabel('Counts', fontsize=fs)
    a.tick_params(labelsize=myfontsize_tic)
    print('----> PHSP1 vs GAN mean diff1 = ', x1 * 100.0)

    a = ax[1]
    x = (d1 - d2) / sigma1
    l1 = '{:} $\mu=${:.2f} $\sigma=${:.2f}'.format('PHSP1 vs GAN', np.mean(x), np.std(x))
    l1 = f'PHSP1 vs GAN $\mu=${np.mean(x):.2f} $\sigma=${np.std(x):.2f}'
    a.hist(x, 200, range=(-3, 3),
           density=False, facecolor='g', alpha=0.3,
           label=l1)
    print('PHSP1 vs GAN mu et sigma = ', np.mean(x), np.std(x))
    vals = a.get_xticks()
    a.set_xlabel('Nb of sigma', fontsize=fs)
    a.set_ylabel('Counts', fontsize=fs)
    a.tick_params(labelsize=myfontsize_tic)
    # a.legend(prop={'family':'monospace', 'size': 10})
    a.legend(loc='center left', prop={'size': myfontsize_title})

    img = itk.image_from_array((data1 - data2) / np.mean(d1))
    img.CopyInformation(img1)
    itk.imwrite(img, 'temp/diff1.mhd')

    img = itk.image_from_array(mask)
    img.CopyInformation(img1)
    itk.imwrite(img, 'temp/mask.mhd')

    plt.tight_layout()
    plt.savefig('temp/a.pdf', dpi=fig.dpi)
    plt.show()

    tol = 0.2
    dm = np.abs(np.mean(x))
    ds = np.fabs(np.std(x) - 1)
    print(f'Compare mean {dm:.3f} and tolerance {tol}')
    print(f'Compare std-1 {ds:.3f} and tolerance {tol}')
    if dm < tol and ds < tol:
        return True
    return False


# -----------------------------------------------------------------------------
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('output_folders',
                nargs=-1,
                required=True,
                type=click.Path(exists=True, file_okay=True, dir_okay=True))
@gt.add_options(gt.common_options)
def analyse_click(output_folders, **kwargs):
    r = analyse_all_folders(output_folders)
    print("Last return: " + str(r))


def analyse_all_folders(output_folders, **kwargs):
    # logger
    gt.logging_conf(**kwargs)

    # take correct folder:
    outputFolders = []
    for o in output_folders:
        if os.path.isdir(o):
            if not o == "output1" and not o == "output2" and not o == "output":
                outputFolders.append(o)
    # spacial case here because the output are in 2 different folders output1 and output2 and we need to be sure that both are correct
    outputFolders.append("output1")
    outputFolders.append("output2")

    for o in outputFolders[:-2]:
        r = relative_uncertainty(['reference_data', o], [1, 10], 0.05)
    r = relative_uncertainty(['reference_data', outputFolders[-2]], [1, 10], 0.05)
    r = r and relative_uncertainty(['reference_data', outputFolders[-1]], [1, 10], 0.05)

    return r


# --------------------------------------------------------------------------
if __name__ == '__main__':
    analyse_click()
