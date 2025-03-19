import logging
import requests
from .exception import RequestException, exception_to_dict


def internal_request(
        method: str,
        path: str,
        host: str | None = None,
        auth_key: str | None = None,
        auth_value: str | None = None,
        auth_type: str | None = None,
        disable_caching: bool = True,
        json_return: bool = True,
        has_success_response: bool = True,
        **kwargs,
):
    if host is None:
        return None

    error_details = {
        'subject': f'Internal Request to {host}',
        'controller': f'request_to_{host}',
        'payload': {
            'host': host,
            'auth_key': auth_key,
            'auth_type': auth_type,
            'method': method,
            'path': path,
            'json_return': json_return,
            'success_checking': has_success_response,
        }
    }

    url = f'{host}/{path}'

    if auth_key is not None and auth_value is not None and auth_type is not None:
        if auth_type == 'params':
            if 'params' not in kwargs:
                kwargs['params'] = {}

            kwargs['params'][auth_key] = auth_value
        elif auth_type == 'headers':
            if 'headers' not in kwargs:
                kwargs['headers'] = {}

            kwargs['headers'][auth_key] = auth_value

    if disable_caching:
        if 'headers' not in kwargs:
            kwargs['headers'] = {}

        kwargs['headers'].update({
            'Cache-Control': 'private, no-cache, no-store, must-revalidate, max-age=0, s-maxage=0',
            'Pragma': 'no-cache',
            'Expires': '0',
        })

    try:
        response = requests.request(method=method, url=url, **kwargs)
    except Exception as e:
        logging.error(
            msg="We faced an error while we wanted to send an internal request.",
            extra={
                'details': error_details
            }
        )
        raise RequestException(
            status_code=500,
            message='Internal Request Error.',
            controller=f'request_to_{host}',
            skip_footprint=True,
        )

    if json_return:
        try:
            response_json = response.json()
        except Exception as e:
            error_details['payload']['text'] = response.text
            error_details['payload']['error'] = exception_to_dict(e)
            logging.error(
                msg="We faced an incorrect response from an internal service.",
                extra={
                    'details': error_details
                }
            )
            raise RequestException(
                status_code=500,
                message='Internal Request Error.',
                controller=f'request_to_{host}',
                skip_footprint=True,
            )
    else:
        return response.text

    if has_success_response:
        is_success = response_json.get('success', False) if isinstance(response_json, dict) else False
        if is_success:
            return response_json.get('data')
        else:
            raise RequestException(
                status_code=500,
                message=response_json.get('message'),
                controller=f'request_to_{host}',
                skip_footprint=True,
            )
    else:
        return response_json

