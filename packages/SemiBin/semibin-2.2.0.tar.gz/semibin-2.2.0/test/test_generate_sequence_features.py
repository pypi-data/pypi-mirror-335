from SemiBin.main import generate_sequence_features_single, generate_sequence_features_multi
import os
import pytest
import logging
import pandas as pd
from argparse import Namespace

def test_generate_seq_feats_multi(tmpdir):
    logger = logging.getLogger('SemiBin2')

    os.makedirs(f'{tmpdir}/output_multi',exist_ok=True)
    generate_sequence_features_multi(logger, Namespace(
                        bams=['test/multi_samples_data/input_multi_sorted1.bam',
                              'test/multi_samples_data/input_multi_sorted2.bam',
                              'test/multi_samples_data/input_multi_sorted3.bam',
                              'test/multi_samples_data/input_multi_sorted4.bam',
                              'test/multi_samples_data/input_multi_sorted5.bam',
                              'test/multi_samples_data/input_multi_sorted6.bam',
                              'test/multi_samples_data/input_multi_sorted7.bam',
                              'test/multi_samples_data/input_multi_sorted8.bam',
                              'test/multi_samples_data/input_multi_sorted9.bam',
                              'test/multi_samples_data/input_multi_sorted10.bam'],
                         num_process=1,
                         separator=':',
                         output=f'{tmpdir}/output_multi',
                         contig_fasta='test/multi_samples_data/input_multi.fasta.xz',
                         ratio=0.05,
                         min_len=None,
                         ml_threshold=None,
                         abundances = None,
                         ))

    for i in range(10):
        data = pd.read_csv(f'{tmpdir}/output_multi/samples/S{i+1}/data.csv', index_col=0)
        data_split = pd.read_csv(f'{tmpdir}/output_multi/samples/S{i+1}/data_split.csv', index_col=0)
        assert data.shape == (20,146)
        assert data_split.shape == (40,146)

def test_generate_seq_feats_multi_abun(tmpdir):
    logger = logging.getLogger('SemiBin2')

    os.makedirs(f'{tmpdir}/output_multi',exist_ok=True)
    generate_sequence_features_multi(logger, Namespace(
                        bams=None,
                         num_process=1,
                         separator=':',
                         output=f'{tmpdir}/output_multi',
                         contig_fasta='test/multi_samples_data/input_multi.fasta.xz',
                         ratio=0.05,
                         min_len=None,
                         ml_threshold=None,
                         abundances = ['test/multi_samples_data/sample1.txt',
                                       'test/multi_samples_data/sample2.txt',
                                       'test/multi_samples_data/sample3.txt',
                                       'test/multi_samples_data/sample4.txt',
                                       'test/multi_samples_data/sample5.txt',
                                       'test/multi_samples_data/sample6.txt',
                                       'test/multi_samples_data/sample7.txt',
                                       'test/multi_samples_data/sample8.txt',
                                       'test/multi_samples_data/sample9.txt',
                                       'test/multi_samples_data/sample10.txt',
                                       ]
                         ))

    for i in range(10):
        data = pd.read_csv(f'{tmpdir}/output_multi/samples/S{i+1}/data.csv', index_col=0)
        data_split = pd.read_csv(f'{tmpdir}/output_multi/samples/S{i+1}/data_split.csv', index_col=0)
        assert data.shape == (20,146)
        assert data_split.shape == (40,146)

def test_generate_seq_feats_single(tmpdir):
    logger = logging.getLogger('SemiBin2')

    os.makedirs(f'{tmpdir}/output_single',exist_ok=True)
    generate_sequence_features_single(
                         bams=['test/single_sample_data/input.sorted.bam'],
                         num_process=1,
                         logger=logger,
                         output=f'{tmpdir}/output_single',
                         contig_fasta='test/single_sample_data/input.fasta',
                         binned_length=2500,
                         must_link_threshold=4000,
                         abundances=None
                         )

    data = pd.read_csv(f'{tmpdir}/output_single/data.csv', index_col=0)
    data_split = pd.read_csv(f'{tmpdir}/output_single/data_split.csv', index_col=0)

    assert data.shape == (40,138)
    assert data_split.shape == (80,136)

def test_generate_seq_feats_coassembly(tmpdir):
    logger = logging.getLogger('SemiBin2')

    os.makedirs(f'{tmpdir}/output_coassembly',exist_ok=True)
    generate_sequence_features_single(bams=['test/coassembly_sample_data/input.sorted1.bam',
                               'test/coassembly_sample_data/input.sorted2.bam',
                               'test/coassembly_sample_data/input.sorted3.bam',
                               'test/coassembly_sample_data/input.sorted4.bam',
                               'test/coassembly_sample_data/input.sorted5.bam'],
                         num_process=1,
                         logger=logger,
                         output=f'{tmpdir}/output_coassembly',
                         contig_fasta='test/coassembly_sample_data/input.fasta',
                         binned_length=2500,
                         must_link_threshold=4000,
                         abundances=None,
                         )

    data = pd.read_csv(f'{tmpdir}/output_coassembly/data.csv', index_col=0).sort_index()
    data_split = pd.read_csv(f'{tmpdir}/output_coassembly/data_split.csv', index_col=0)
    assert data.shape == (40,141)
    assert data_split.shape == (80,141)

    for ix in range(5):
        assert f'input.sorted{ix+1}' in data.columns[-5 + ix]
    col1 = pd.read_csv(f'{tmpdir}/output_coassembly/input.sorted1.bam_0_data_cov.csv', index_col=0).squeeze().sort_index()
    pd.testing.assert_series_equal(data.iloc[:, 136], col1)

    col2 = pd.read_csv(f'{tmpdir}/output_coassembly/input.sorted2.bam_1_data_cov.csv', index_col=0).squeeze().sort_index()
    pd.testing.assert_series_equal(data.iloc[:, 137], col2)

def test_generate_seq_feats_coassembly_abun(tmpdir):
    logger = logging.getLogger('SemiBin2')

    os.makedirs(f'{tmpdir}/output_coassembly',exist_ok=True)
    generate_sequence_features_single(bams=None,
                         num_process=1,
                         logger=logger,
                         output=f'{tmpdir}/output_coassembly',
                         contig_fasta='test/coassembly_sample_data/input.fasta',
                         binned_length=2500,
                         must_link_threshold=4000,
                         abundances=['test/coassembly_sample_data/sample1.txt',
                                     'test/coassembly_sample_data/sample2.txt',
                                     'test/coassembly_sample_data/sample3.txt',
                                     'test/coassembly_sample_data/sample4.txt',
                                     'test/coassembly_sample_data/sample5.txt'],
                         )

    data = pd.read_csv(f'{tmpdir}/output_coassembly/data.csv', index_col=0).sort_index()
    data_split = pd.read_csv(f'{tmpdir}/output_coassembly/data_split.csv', index_col=0)
    assert data.shape == (40,141)
    assert data_split.shape == (80,141)
