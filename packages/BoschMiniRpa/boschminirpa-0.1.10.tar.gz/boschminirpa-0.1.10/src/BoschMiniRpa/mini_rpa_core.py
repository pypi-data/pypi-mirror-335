"""
-*- coding: utf-8 -*-
@Time : 2/17/2022 3:28 PM
@Author : LV Zhichao
@File : mini_rpa_core
"""
from io import BytesIO
import pandas as pd
from copy import deepcopy
from BoschRpaMagicBox.helper_functions import *
from BoschRpaMagicBox.smb_functions import *

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 1000)
pd.set_option("display.max_colwidth", 20)
pd.set_option('display.width', 1000)


class MiniRPACore:
    """This class is used to generate RPA components

    """

    def __init__(self, user_name: str, user_password: str, server_name: str, share_name: str, port: int,
                 from_period: str, to_period: str, report_save_path: str, report_process_folder_path: str, report_period_type: str,
                 process_number: int, process_dict: dict, delivery_dict: dict, sap_operation_list: list, update_file_condition_setting: list,
                 from_file_condition_setting: list, data_type_dict: dict, download_data=False, process_data: bool = False, delivery_data: bool = False):
        """This function is used to initial parameters

        Args:
            user_name(str): This is the username
            user_password(str): This is the password
            server_name(str):This is the server name (url), e.g. szh0fs06.apac.bosch.com
            share_name(str): This is the share_name of public folder, e.g. GS_ACC_CN$
            port(int): This is the port number of the server name
            from_period(str):This is the start month
            to_period(str): This is the end month
            report_process_folder_path(str): This is the file path for process excel
            report_save_path(str): This is the folder path for original data
            delivery_data(bool): This is the indicator whether to delivery files to folders, receivers or api
            download_data(bool): This is the indicator whether to do sap operation
            process_data(bool): This is the indicator whether to process data
            data_type_dict(dict): This is the dict that save the data type
            process_number(int): This is the number of process
            sap_operation_list: This is the list of sap operation
            report_period_type(str): This is the report period type. e.g. period, current_date
            process_dict(dict): This is the dict that save the process logic data
            delivery_dict(dict): This is the dict that save the delivery logic data
            update_file_condition_setting(list): This is the list of update file condition setting
            from_file_condition_setting(list): This is the list of from file condition setting
        """
        self.user_name = user_name
        self.user_password = user_password
        self.server_name = server_name
        self.share_name = share_name
        self.port = port
        self.from_period = from_period
        self.to_period = to_period
        self.report_save_path = report_save_path
        self.report_process_folder_path = report_process_folder_path
        self.log_folder_path = self.report_save_path + os.sep + 'Log'
        self.download_data = download_data
        self.delivery_data = delivery_data
        self.process_data = process_data
        self.process_dict = process_dict
        self.delivery_dict = delivery_dict
        self.sap_operation_list = sap_operation_list

        # integrated file path and file name
        self.from_file_path, self.from_file_name, self.from_sheet_name, self.update_file_path, self.update_file_name, self.update_sheet_name = (
            '',
            self.process_dict.get('from_file_name', ''),
            self.process_dict.get('from_sheet_name', ''),
            '',
            self.process_dict.get('update_file_name', ''),
            self.process_dict.get('update_sheet_name', ''),
        )

        self.process_number = process_number
        self.report_period_type = report_period_type
        self.file_name_suffix = self.prepare_file_name_suffix()
        self.parse_date_dict = {}

        self.update_file_condition_setting = pd.DataFrame(update_file_condition_setting)
        self.from_file_condition_setting = pd.DataFrame(from_file_condition_setting)

        self.data_type_dict = deepcopy(data_type_dict)
        self.prepare_data_type()
        self.initial_process_file_path()

        self.update_file_condition_syntax_list = self.generate_filter_condition(self.update_file_condition_setting, 'update_file')
        self.from_file_condition_syntax_list = self.generate_filter_condition(self.from_file_condition_setting, 'from_file')

    def prepare_file_name_suffix(self):
        """ This function is used to prepare suffix in file name

        """
        from_period = self.from_period.replace('-', '').replace('.', '') if self.from_period else ''
        to_period = self.to_period.replace('-', '').replace('.', '') if self.to_period else ''

        if from_period and to_period:
            file_name_suffix = f'{from_period}_{to_period}'
        elif from_period:
            file_name_suffix = f'{from_period}'
        else:
            file_name_suffix = ''

        print('file_name_suffix: ', file_name_suffix)
        return file_name_suffix

    def prepare_file_name(self, file_name):
        if not file_name.startswith('Common'):
            split_file_name, file_extension = os.path.splitext(file_name)
            if self.file_name_suffix and file_name:
                if file_extension:
                    file_name = f'{split_file_name}_{self.file_name_suffix}{file_extension}'
                else:
                    file_name = f'{split_file_name}_{self.file_name_suffix}.xlsx'
            elif not self.file_name_suffix and file_name:
                if file_extension:
                    file_name = f'{split_file_name}{file_extension}'
                else:
                    file_name = f'{split_file_name}.xlsx'
            else:
                file_name = None
        else:
            file_name = f'{file_name}.xlsx'

        return file_name

    def initial_process_file_path(self):
        """ This function is used to initial process cache data

        """
        self.from_file_name = self.prepare_file_name(self.from_file_name)
        self.update_file_name = self.prepare_file_name(self.update_file_name)

        if self.from_file_name:
            self.from_file_path = self.report_save_path + os.sep + self.from_file_name

        if self.update_file_name:
            self.update_file_path = self.report_save_path + os.sep + self.update_file_name

    def prepare_data_type(self):
        """This function is used to load data types for preparing dtype parameter

        """
        temp_data_tye_dict = {}

        for file_name, file_data_type_dict in self.data_type_dict.items():
            file_name = self.prepare_file_name(file_name)
            new_file_data_type_dict = deepcopy(file_data_type_dict)
            for sheet_name, sheet_data_type_dict in new_file_data_type_dict.items():
                for column_name, column_type in sheet_data_type_dict.items():
                    if column_type != 'date':
                        file_data_type_dict[sheet_name][column_name] = eval(column_type)
                    else:
                        del file_data_type_dict[sheet_name][column_name]
                        self.parse_date_dict.setdefault(file_name, {}).setdefault(sheet_name, []).append(column_name)

            temp_data_tye_dict[file_name] = deepcopy(file_data_type_dict)

        self.data_type_dict = temp_data_tye_dict

    def generate_filter_condition(self, file_condition_setting: pd.DataFrame, file_type: str) -> list[str]:
        """This function is used to generate related pandas filter syntax

        Args:
            file_condition_setting(pd.DataFrame): This is the file condition setting
            file_type(str): from_file or update_file

        """
        process_syntax_list = []

        if not file_condition_setting.empty:
            file_name = self.from_file_name if file_type == 'from_file' else self.update_file_name
            sheet_name = self.from_sheet_name if file_type == 'from_file' else self.update_sheet_name

            file_condition_setting['operator'] = file_condition_setting['operator'].fillna('')
            step_number_list = sorted(list(set(file_condition_setting['step_number'].values.tolist())))

            # operator_logic not start with not
            operator_list = ['.str.contains', '.str.startswith']
            # operator_logic start with not
            operator_not_list = ['not .str.contains', 'not .str.startswith']
            # nan value as false list
            na_false_list = ['.str.contains', '.str.startswith', 'not .str.contains', 'not .str.startswith']
            process_syntax = ''

            for step_number in step_number_list:
                step_data = file_condition_setting[file_condition_setting['step_number'] == step_number]
                step_syntax = ''
                last_operator_logic = ''

                for step_index in step_data.index:
                    row_data = step_data.loc[step_index]
                    column_name = row_data['column_name']
                    operator = row_data['operator']
                    operator_logic = row_data['operator_logic']
                    value = row_data['filter_value']

                    data_type = self.data_type_dict.get(file_name, {sheet_name: {}}).get(sheet_name, {column_name: str}).get(column_name, str)

                    if operator == '.duplicated':
                        # keep first duplicated row or keep not duplicated rows
                        sub_step_syntax = f'~(target["{column_name}"]{operator}(keep="first"))'
                    elif operator == '.isna':
                        sub_step_syntax = f'(target["{column_name}"]{operator}())'
                    elif operator == 'not .isna':
                        operator = operator.split(' ')[1]
                        sub_step_syntax = f'~(target["{column_name}"]{operator}())'
                    elif operator in operator_not_list:
                        operator = operator.split(' ')[1]
                        if operator in na_false_list:
                            sub_step_syntax = f'~(target["{column_name}"]{operator}("{value}",na=False))'
                        else:
                            sub_step_syntax = f'~(target["{column_name}"]{operator}("{value}"))'
                    elif operator in operator_list:
                        if operator in na_false_list:
                            sub_step_syntax = f'(target["{column_name}"]{operator}("{value}",na=False))'
                        else:
                            sub_step_syntax = f'(target["{column_name}"]{operator}("{value}"))'
                    else:
                        # < > == !== <= >=
                        if data_type == str:
                            sub_step_syntax = f'(target["{column_name}"]{operator}"{value}")'
                        else:
                            sub_step_syntax = f'(target["{column_name}"]{operator}{value})'

                    step_syntax += sub_step_syntax

                    if operator_logic and step_index != step_data.index[-1]:
                        step_syntax += f' {operator_logic} '
                    elif operator_logic and step_index == step_data.index[-1]:
                        last_operator_logic = f' {operator_logic} '
                if last_operator_logic:
                    process_syntax += f'({step_syntax}){last_operator_logic}'
                else:
                    process_syntax += f'({step_syntax})'
                    process_syntax_list.append(process_syntax)
                    process_syntax = ''

        print('process_syntax_list: \n', process_syntax_list)

        return process_syntax_list

    @staticmethod
    def custom_date_parser(date_value):
        """This function is used to parse date value

        Args:
            date_value(str): This is the date value

        """
        date_value = str(date_value)
        try:
            date_value = datetime.datetime.strptime(date_value, '%Y-%m-%d').date()
        except ValueError:
            try:
                date_value = datetime.datetime.strptime(date_value, '%Y-%m-%d %H:%M:%S').date()
            except ValueError:
                date_value = pd.NaT

        return date_value

    @staticmethod
    def string_date_parser(date_value):
        """This function is used to parse date value

        Args:
            date_value(str): This is the date value

        """
        date_value = str(date_value)
        try:
            date_value = str(datetime.datetime.strptime(date_value, '%Y-%m-%d').date())
        except ValueError:
            try:
                date_value = str(datetime.datetime.strptime(date_value, '%Y-%m-%d %H:%M:%S').date())
            except ValueError:
                date_value = ''

        return date_value

    @staticmethod
    def prepare_date_info(date_value):
        """This function is used to prepare date info

        Args:
            date_value(str): This is the date value

        """
        date_value = str(date_value).split(' ')[0]
        transformed_date = None
        for date_format in ['%d.%m.%Y', '%d-%m-%Y', '%Y-%m-%d', '%Y.%m.%d', '%m/%d/%Y', '%Y%m%d', '%d%m%Y', '%m%d%Y']:
            try:
                transformed_date = datetime.datetime.strptime(date_value, date_format).date()
                break
            except ValueError:
                continue

        return transformed_date

    def get_from_or_update_data(self, file_path: str, file_name: str, sheet_name: str, has_file_condition: bool, flag: str = 'update_file') -> tuple[pd.DataFrame, dict]:
        """This function is used to get data of from file or update file

        Args:
            file_path(str): This is the file path of target data
            file_name(str): This is the file name
            sheet_name(str): This is the sheet name
            has_file_condition(bool): This is the condition which is used to filter data
            flag(str): This is the flag of update_file and from_file

        """
        # process_number may not be equal to self.process_number
        dtype_dict = {}
        parse_date_list = []
        if self.data_type_dict.get(file_name):
            if self.data_type_dict[file_name].get(sheet_name):
                dtype_dict = self.data_type_dict[file_name][sheet_name]
                parse_date_list = self.parse_date_dict.get(file_name, {}).get(sheet_name, [])

        file_obj = smb_load_file_obj(self.user_name, self.user_password, self.server_name, self.share_name, file_path, self.port)
        target = pd.read_excel(file_obj, sheet_name=sheet_name, dtype=dtype_dict)
        file_obj.close()
        for column in parse_date_list:
            target[column] = target[column].apply(self.custom_date_parser)

        if has_file_condition:
            process_syntax_list = self.update_file_condition_syntax_list if flag == 'update_file' else self.from_file_condition_syntax_list
            for process_syntax in process_syntax_list:
                target = target[eval(process_syntax)]
        return target, dtype_dict

    def save_file(self, process_number: int, file_name: str, dtype_dict: dict, target: pd.DataFrame, function: str, sheet_name: str = 'Sheet1', is_save: bool = True):
        """This function is used to save file to save folder

        Args:
            is_save(bool): This is indicator whether to save file
            process_number(int): This is the process number of process logic
            file_name(str): This is the file name of related file
            sheet_name(str): This is the sheet name of target data
            target(pd.DataFrame): This is the dataframe instance to be saved as Excel file
            function(str): This is the name of function. e.g. remove, vlookup......
            dtype_dict(dict): This is the dtype dict of target data.
        """

        if is_save:
            for column, column_type in dtype_dict.items():
                if column in target.columns:
                    if column_type == str:
                        target[column] = target[column].fillna('')
                    target[column] = target[column].astype(column_type)

            file_obj = BytesIO()

            sheet_name = sheet_name if sheet_name else 'Sheet1'
            with pd.ExcelWriter(file_obj, engine='xlsxwriter') as writer:
                target.to_excel(writer, index=False, float_format='%.2f', sheet_name=sheet_name)
            file_obj.seek(0)

            save_file_path = self.report_process_folder_path + os.sep + f'{process_number}_{function}_{file_name}'
            smb_store_remote_file_by_obj(self.user_name, self.user_password, self.server_name, self.share_name, save_file_path, file_obj, self.port)

            original_save_file_path = self.report_save_path + os.sep + f'{file_name}'
            smb_store_remote_file_by_obj(self.user_name, self.user_password, self.server_name, self.share_name, original_save_file_path, file_obj, self.port)

            file_obj.close()

    def clear_cache(self):
        """This function is used to clear cache

        """
        self.download_data = None
        self.delivery_data = None
        self.process_data = None
        self.process_dict = None
        self.delivery_dict = None
        self.sap_operation_list = None
        self.update_file_condition_setting = None
        self.from_file_condition_setting = None
        self.update_file_condition_syntax_list = None
        self.from_file_condition_syntax_list = None
