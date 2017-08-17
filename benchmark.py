#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os, sys, shutil, platform
import urllib.request
import subprocess
import tarfile
import cpuinfo.cpuinfo as cpuinfo
import time
import statistics

def check_deps(args):
    if shutil.which('yasm') == None and shutil.which('yasm.exe') == None:
        print('yasm is not installed or in the PATH')
        sys.exit(-2)

    for command in args:
        if shutil.which(command) == None:
            print('Cannot find ' + command + ' executable')
            sys.exit(-3)

def download_and_extract_ffmpeg():
    print('\nDownloading ffmpeg sources...')
    url = 'http://ffmpeg.org/releases/ffmpeg-2.8.4.tar.gz'
    file_name = url.split('/')[-1]

    if not os.path.isfile(file_name):
        f = open( file_name, 'wb' )

        with urllib.request.urlopen(url) as d:
            f.write( d.read() )

        f.close()
    print('Source code downloaded!\n')

    decompress_file(file_name)

def decompress_file(file_name):
    print('Decompressing sources...')
    compressedFile = tarfile.open(file_name, 'r:gz')
    compressedFile.extractall()
    compressedFile.close()
    print('Sources decompressed!')
    os.chdir(file_name.split('.tar')[0])


def configure(compiler):
    conf = './configure --disable-doc --cc=' + compiler
    FNULL = open(os.devnull, 'w')
    try:
        subprocess.check_call(conf.split(), stdout=FNULL, \
        stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        print('Error using ./configure: {0}'.format(err))
        sys.exit(-4)

def compile():
    make = 'make'
    FNULL = open(os.devnull, 'w')
    try:
        subprocess.check_call(make, stdout=FNULL, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        print('Error compiling: {1}'.format(compiler, err))
        sys.exit(-5)

def clean():
    make = 'make clean'
    FNULL = open(os.devnull, 'w')
    subprocess.call(make.split(),stdout=FNULL, stderr=subprocess.STDOUT)

def greeting():
    print('/*****************************************************************/')
    print('/*                Benchmark to test compile times                */')
    print('/*             with diferent compilers using ffmpeg              */')
    print('/*****************************************************************/')

    try:
        
        import matplotlib.pyplot as plt
        plt.rcdefaults()

    except ImportError as err:
        print('\nTo generate a graph of the stadistics you need to have installed matplotlib')


def show_results(names, times):
    print('\nReview of the results:')
    print('Operating system: {0}'.format(platform.system_alias( \
    platform.system(), platform.release(), platform.version())))
    print( 'Processor: {0}'.format( cpuinfo.get_cpu_info().get('brand','') ) )

    for i in  range(len(names)):
        print('\nStatistics of {0}'.format(names[i]))
        print('Number of iterations: {0}'.format(len(times[i])))
        print('min: {0}'.format(min(times[i])))
        print('mean: {0} seconds'.format(statistics.mean(times[i])))
        print('+/- stdev: {0}'.format(statistics.stdev(times[i])))
        print('max: {0}'.format(max(times[i])))
        print('median: {0} seconds'.format(statistics.median_high(times[i])))


def main():
    greeting()
    if len(sys.argv) < 3:
        print('\nUsage: python {0} <compiler 1> ... \
        <number of samples>'.format(sys.argv[0]))
        sys.exit(-1)

    compilers = sys.argv[1:-1]
    iterations = int(sys.argv[-1])

    print('\n')
    names = []
    for comp in compilers:
        names.append(input('Give a name for the \
        statistics of {0}: '.format(comp)))

    check_deps(compilers)
    download_and_extract_ffmpeg()

    times = []

    for x in  range(len(compilers)):
        print('\nStarting configuration for {0}'.format(compilers[x]))
        configure(comp)
        times.append([])
        for i in range(1, iterations + 1):
            print('Compiling ffmpeg with {0}. {1}º \
            time'.format(compilers[x], i))
            start = time.time()
            compile()
            end = time.time()
            times[x].append(end-start)
            clean()

    cwd = os.getcwd()
    os.chdir('..')
    shutil.rmtree(cwd)
    show_results(names, times)

    try:
        import matplotlib.pyplot as plt
        plt.rcdefaults()
        import numpy as np
        import matplotlib.pyplot as plt

        y_pos = np.arange(len(compilers))
        means = []
        stdevs = []
        for i in  range(len(compilers)):
            means.append(statistics.mean(times[i]))
            stdevs.append(statistics.stdev(times[i]))

        plt.barh(y_pos, means, xerr=stdevs, align='center', alpha=0.4)
        plt.yticks(y_pos, names)
        plt.xlabel('Compiling mean time(seconds)')
        plt.title('Compiling times for ffmpeg')
        fig = plt.gcf()
        fig.savefig('Results.png', dpi=fig.dpi)
        print('\nStatistics saved as Results.png')
    except ImportError as err:
        print('\nTo generate a graph of the stadistics you need to have installed matplotlib')

if __name__ == "__main__":
    main()
