# Copyright 2019 Amazon.com, Inc. and its affiliates. All Rights Reserved.
#
# Licensed under the Amazon Software License (the 'License').
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#   http://aws.amazon.com/asl/
#
# or in the 'license' file accompanying this file. This file is distributed
# on an 'AS IS' BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.

import json
import boto3
import logging
import traceback

from typing import Optional, Mapping
from botocore.exceptions import ClientError

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


PROFILES_SSM_PARAMETER_PREFIX = '/emr_launch/emr_profiles'
CONFIGURATIONS_SSM_PARAMETER_PREFIX = '/emr_launch/cluster_configurations'
FUNCTIONS_SSM_PARAMETER_PREFIX = '/emr_launch/emr_launch_functions'


class EMRProfileNotFoundError(Exception):
    pass


class ClusterConfigurationNotFoundError(Exception):
    pass


class EMRLaunchFunctionNotFoundError(Exception):
    pass


def _get_parameter_values(ssm_parameter_prefix: str, top_level_return: str, namespace: str = 'default',
                          next_token: Optional[str] = None) -> Mapping[str, any]:
    params = {
        'Path': f'{ssm_parameter_prefix}/{namespace}/'
    }
    if next_token:
        params['NextToken'] = next_token
    result = boto3.client('ssm').get_parameters_by_path(**params)

    return_val = {
        top_level_return: [json.loads(p['Value']) for p in result['Parameters']]
    }
    if 'NextToken' in result:
        return_val['NextToken'] = result['NextToken']
    return return_val


def _get_parameter_value(ssm_parameter_prefix: str, name: str, namespace: str = 'default') -> Mapping[str, any]:
    configuration_json = boto3.client('ssm').get_parameter(
        Name=f'{ssm_parameter_prefix}/{namespace}/{name}')['Parameter']['Value']
    return json.loads(configuration_json)


def get_profiles_handler(event, context):
    LOGGER.info('Lambda metadata: {} (type = {})'.format(json.dumps(event), type(event)))
    namespace = event.get('Namespace', 'default')
    next_token = event.get('NextToken', None)

    try:
        return _get_parameter_values(PROFILES_SSM_PARAMETER_PREFIX, 'EMRProfiles', namespace, next_token)

    except Exception as e:
        trc = traceback.format_exc()
        s = 'Error processing event {}: {}\n\n{}'.format(str(event), str(e), trc)
        LOGGER.error(s)
        raise e


def get_profile_handler(event, context):
    LOGGER.info('Lambda metadata: {} (type = {})'.format(json.dumps(event), type(event)))
    profile_name = event.get('ProfileName', '')
    namespace = event.get('Namespace', 'default')

    try:
        return _get_parameter_value(PROFILES_SSM_PARAMETER_PREFIX, profile_name, namespace)

    except ClientError as e:
        if e.response['Error']['Code'] == 'ParameterNotFound':
            LOGGER.error(f'ProfileNotFound: {namespace}/{profile_name}')
            raise EMRProfileNotFoundError(f'ProfileNotFound: {namespace}/{profile_name}')
        else:
            trc = traceback.format_exc()
            s = 'Error processing event {}: {}\n\n{}'.format(str(event), str(e), trc)
            LOGGER.error(s)
            raise e
    except Exception as e:
        trc = traceback.format_exc()
        s = 'Error processing event {}: {}\n\n{}'.format(str(event), str(e), trc)
        LOGGER.error(s)
        raise e


def get_configurations_handler(event, context):
    LOGGER.info('Lambda metadata: {} (type = {})'.format(json.dumps(event), type(event)))
    namespace = event.get('Namespace', 'default')
    next_token = event.get('NextToken', None)

    try:
        return _get_parameter_values(CONFIGURATIONS_SSM_PARAMETER_PREFIX, 'ClusterConfigurations',
                                     namespace, next_token)

    except Exception as e:
        trc = traceback.format_exc()
        s = 'Error processing event {}: {}\n\n{}'.format(str(event), str(e), trc)
        LOGGER.error(s)
        raise e


def get_configuration_handler(event, context):
    LOGGER.info('Lambda metadata: {} (type = {})'.format(json.dumps(event), type(event)))
    configuration_name = event.get('ConfigurationName', '')
    namespace = event.get('Namespace', 'default')

    try:
        return _get_parameter_value(CONFIGURATIONS_SSM_PARAMETER_PREFIX, configuration_name, namespace)

    except ClientError as e:
        if e.response['Error']['Code'] == 'ParameterNotFound':
            LOGGER.error(f'ConfigurationNotFound: {namespace}/{configuration_name}')
            raise EMRProfileNotFoundError(f'ConfigurationNotFound: {namespace}/{configuration_name}')
        else:
            trc = traceback.format_exc()
            s = 'Error processing event {}: {}\n\n{}'.format(str(event), str(e), trc)
            LOGGER.error(s)
            raise e
    except Exception as e:
        trc = traceback.format_exc()
        s = 'Error processing event {}: {}\n\n{}'.format(str(event), str(e), trc)
        LOGGER.error(s)
        raise e


def get_functions_handler(event, context):
    LOGGER.info('Lambda metadata: {} (type = {})'.format(json.dumps(event), type(event)))
    namespace = event.get('Namespace', 'default')
    next_token = event.get('NextToken', None)

    try:
        return _get_parameter_values(FUNCTIONS_SSM_PARAMETER_PREFIX, 'EMRLaunchFunctions',
                                     namespace, next_token)

    except Exception as e:
        trc = traceback.format_exc()
        s = 'Error processing event {}: {}\n\n{}'.format(str(event), str(e), trc)
        LOGGER.error(s)
        raise e


def get_function_handler(event, context):
    LOGGER.info('Lambda metadata: {} (type = {})'.format(json.dumps(event), type(event)))
    function_name = event.get('FunctionName', '')
    namespace = event.get('Namespace', 'default')

    try:
        return _get_parameter_value(FUNCTIONS_SSM_PARAMETER_PREFIX, function_name, namespace)

    except ClientError as e:
        if e.response['Error']['Code'] == 'ParameterNotFound':
            LOGGER.error(f'FunctionNotFound: {namespace}/{function_name}')
            raise EMRProfileNotFoundError(f'FunctionNotFound: {namespace}/{function_name}')
        else:
            trc = traceback.format_exc()
            s = 'Error processing event {}: {}\n\n{}'.format(str(event), str(e), trc)
            LOGGER.error(s)
            raise e
    except Exception as e:
        trc = traceback.format_exc()
        s = 'Error processing event {}: {}\n\n{}'.format(str(event), str(e), trc)
        LOGGER.error(s)
        raise e
