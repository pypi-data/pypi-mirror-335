from SemiBin.main import training
from SemiBin.fasta import fasta_iter
import os
import logging
import pandas as pd
import argparse

args = argparse.Namespace(
        num_process = 1,
        ratio = 0.05,
        batchsize = 2048,
        epoches = 1,
        orf_finder = 'fast-naive',
        min_len = None,
        prodigal_output_faa = None,
        )

def test_train(tmpdir):
    odir = f'{tmpdir}/output_train'
    os.makedirs(odir)
    ofile = f'{odir}/model.pt'

    args.training_type = 'semi'
    training(contig_fasta = ['test/train_data/input.fasta'],
            data = ['test/train_data/data.csv'],
            data_split = ['test/train_data/data_split.csv'],
            cannot_link = ['test/train_data/cannot.txt'],
            logger = logging,
            output = ofile,
            device = 'cpu',
            mode = 'single',
            args = args,
            )

    assert os.path.exists(ofile)

def test_train_self(tmpdir):
    odir = f'{tmpdir}/output_train_self'
    os.makedirs(odir)
    args.training_type = 'self'
    training(contig_fasta = ['test/train_data/input.fasta'],
            data = ['test/train_data/data.csv'],
            data_split = ['test/train_data/data_split.csv'],
            cannot_link = ['test/train_data/cannot.txt'],
            logger = logging,
            output = odir,
            device = 'cpu',
            mode = 'single',
            args = args,
            )

    assert os.path.exists(f'{odir}/model.pt')


# https://github.com/BigDataBiology/SemiBin/issues/137
def test_regression_137_semi(tmpdir):
    from SemiBin.semi_supervised_model import train_semi
    odir = f'{tmpdir}/output_train_semi'
    os.makedirs(odir)
    # 40 elements plus header: 41
    assert len(open('test/train_data/data.csv', 'r').readlines()) == 41
    model = train_semi(out = odir,
                       contig_fastas = ['test/train_data/input.fasta'],
                       logger = logging,
                       binned_lengths = [1000],
                       datas=['test/train_data/data.csv'],
                       data_splits=['test/train_data/data_split.csv'],
                       cannot_links = ['test/train_data/cannot.txt'],
                       is_combined=False,
                       batchsize=39, # test/semi_data/data.csv has 40 elements so bug is triggered when batchsize is 39
                       epoches=1,
                       device='cpu',
                       num_process=1,
                       mode='single',
                       )
    model.save_with_params_to(f'{odir}/model.pt')
    assert os.path.exists(f'{odir}/model.pt')


# https://github.com/BigDataBiology/SemiBin/issues/137
def test_regression_137_self(tmpdir):
    from SemiBin.self_supervised_model import train_self
    odir = f'{tmpdir}/output_train_self'
    os.makedirs(odir)
    ofile = f'{odir}/model.pt'
    # 40 elements plus header: 41
    assert len(open('test/train_data/data.csv', 'r').readlines()) == 41
    # 80 elements plus header: 81
    assert len(open('test/train_data/data_split.csv', 'r').readlines()) == 81

    # Training adds len(<split>) * 1000//2 + 40 so that the total data is 40040
    # To trigger the bug, batchsize is set to 40039
    model = train_self(logger = logging,
                       datapaths=['test/train_data/data.csv'],
                       data_splits=['test/train_data/data_split.csv'],
                       is_combined=False,
                       batchsize=40039,
                       epoches=1,
                       device='cpu',
                       num_process=1,
                       mode='single',
                       )
    model.save_with_params_to(ofile)
    assert os.path.exists(ofile)

