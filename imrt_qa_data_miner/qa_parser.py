#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
IMRT QA PDF report parser
Created on Wed Apr 18 2018
@author: Dan Cutright, PhD
"""

from imrt_qa_data_miner.pdf_to_text import convert_pdf_to_txt
from os.path import basename


def pdf_to_qa_result(abs_file_path):

    try:
        text = convert_pdf_to_txt(abs_file_path).split('\n')
    except:
        return False

    if is_file_snc_mapcheck(text):
        return MapcheckResult(text).data_to_csv() + ',' + basename(abs_file_path)


class MapcheckResult:
    def __init__(self, text_data):
        self.text = text_data
        self.date, self.hospital = [], []
        for row in text_data:
            if row.find('Date: ') > -1:
                self.date = row.strip('Date: ')
            if row.find('Hospital Name: ') > -1:
                self.hospital = row.split('Hospital Name: ', 1)[1]

            if self.date and self.hospital:
                break

        self.qa_file_parameter = self.get_group_results('QA File Parameter')

        try:
            self.text.index('Absolute Dose Comparison')
            self.dose_comparison_type = 'Absolute Dose Comparison'
        except ValueError:
            self.dose_comparison_type = 'Relative Comparison'
        self.dose_comparison = self.get_group_results(self.dose_comparison_type)

        try:
            self.text.index('Summary (Gamma Analysis)')
            self.analysis_type = 'Gamma'
        except ValueError:
            self.analysis_type = 'DTA'
        self.summary = self.get_group_results('Summary (%s Analysis)' % self.analysis_type)

        try:
            self.text.index('Gamma Index Summary')
            self.gamma_stats = self.get_gamma_statistics('Gamma Index Summary')
        except ValueError:
            self.gamma_stats = {'Minimum': 'n/a',
                                'Maximum': 'n/a',
                                'Average': 'n/a',
                                'Stdv': 'n/a'}

    def get_group_results(self, data_group):
        group_start = self.text.index(data_group)
        var_name_start = group_start + 1
        data_start = self.text[var_name_start:-1].index('') + 1 + var_name_start
        data_count = data_start - var_name_start

        # If patient name is too long, sometimes the pdf parsing gets off-set
        if self.text[data_start] == 'Set1':
            data_start += 1

        group_results = {}
        for i in range(0, data_count):
            if self.text[var_name_start+i]:
                group_results[self.text[var_name_start+i]] = self.text[data_start+i].replace(' : ', '')

        return group_results

    def get_gamma_statistics(self, stats_delimiter):
        gamma_stats = {}
        stats_fields = ['Minimum', 'Maximum', 'Average', 'Stdv']

        group_start = self.text.index(stats_delimiter)

        for field in stats_fields:
            field_start = self.text[group_start:-1].index(field) + 1
            gamma_stats[field] = self.text[group_start:-1][field_start]

        return gamma_stats

    def data_to_csv(self):
        row = [self.qa_file_parameter['Patient Name'].replace(',', '^'),
               self.qa_file_parameter['Patient ID'].replace(',', '^'),
               self.qa_file_parameter['Plan Date'].replace(',', '^'),
               self.dose_comparison_type,
               self.dose_comparison['% Diff'],
               self.dose_comparison['Distance (mm)'],
               self.dose_comparison['Threshold'],
               self.dose_comparison['Meas Uncertainty'],
               self.dose_comparison['Use VanDyk'],
               self.analysis_type,
               self.summary['Total Points'],
               self.summary['Passed'],
               self.summary['Failed'],
               self.summary['% Passed'],
               self.gamma_stats['Minimum'],
               self.gamma_stats['Maximum'],
               self.gamma_stats['Average'],
               self.gamma_stats['Stdv']]
        return ','.join(row)


def is_file_snc_mapcheck(text_data):

    find_these = {'QA File Parameter': False,
                  'Threshold': False,
                  'Notes': False,
                  'Reviewed By :': False}

    for row in text_data:
        if row in list(find_these):
            find_these[row] = True

    answer = True
    for i in list(find_these):
        answer = answer * find_these[i]

    return answer

